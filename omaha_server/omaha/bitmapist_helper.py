"""
The purpose of this module is to send Bitmapist data both to Redis (as is normal
for Bitmapist) and to an instance of bitmapist-server. This allows us to
evaluate the stability of the latter in our production use, to maybe, eventually
use it to replace the RAM-hungry former.
"""
from io import BytesIO
from traceback import print_exception

from django.conf import settings
from django.utils.timezone import localtime, now
from django_redis import get_redis_connection
from redis import Redis

import bitmapist
import sys

def init():
    global _REDIS_LOG_DB
    _REDIS_LOG_DB = get_redis_connection('log')
    master = Redis(
        settings.REDIS_STAT_HOST, settings.REDIS_STAT_PORT,
        settings.REDIS_STAT_DB, settings.REDIS_PASSWORD
    )
    slave = _BitmapistRedis(settings.BITMAPIST_HOST, settings.BITMAPIST_PORT)
    bitmapist.SYSTEMS['default'] = _TeeRedis(master, slave)

_REDIS_LOG_DB = None
# Limit the number of log entries stored in Redis.
# This prevents them from filling up all available memory:
_NUM_REDIS_LOGS = 10000

def _log(message):
    # Log to Redis (not to a file on disk) for speed.
    message = localtime(now()).isoformat() + ' ' + message
    _REDIS_LOG_DB.set(_REDIS_LOG_DB.incr('i') % _NUM_REDIS_LOGS, message)

def _log_curr_exception():
    traceback = BytesIO()
    print_exception(*sys.exc_info(), file=traceback)
    _log(traceback.getvalue().decode('utf-8'))

class _BitmapistRedis(Redis):
    def flushdb(self):
        # Bitmapist doesn't implement the FLUSHDB command. Our tests require it
        # though, in particular for tearDown(). So implement it here:
        keys = self.keys()
        if keys:
            self.delete(*keys)

class _Tee(object):
    """
    A proxy object that forwards all method calls to *two* other objects.
    Optionally, it verifies that methods whose names are listed in CHECK return
    the same result for both objects.
    """
    CHECK = set()
    def __init__(self, master, slave):
        self._master = master
        self._slave = slave
    def __getattr__(self, item):
        result = getattr(self._master, item)
        if callable(result):
            check = item in self.CHECK
            result = _TeeFn(result, getattr(self._slave, item), check)
        return result

class _TeeRedis(_Tee):
    CHECK = ('bitcount', 'getbit', 'bitop')
    def __init__(self, master, slave):
        super(_TeeRedis, self).__init__(master, slave)
    def pipeline(self):
        master_pipeline = self._master.pipeline()
        try:
            slave_pipeline = self._slave.pipeline()
        except Exception:
            _log_curr_exception()
            return master_pipeline
        return _Tee(master_pipeline, slave_pipeline)

class _TeeFn:
    def __init__(self, master, slave, check=False):
        self._master = master
        self._slave = slave
        self._check = check
    def __call__(self, *args, **kwargs):
        master_result = self._master(*args, **kwargs)
        try:
            slave_result = self._slave(*args, **kwargs)
        except Exception:
            _log_curr_exception()
            return master_result
        if self._check and master_result != slave_result:
            fn_name = self._master.__name__
            args_repr = ', '.join(map(repr, args))
            args_repr += ', '.join('%s=%r' % kwarg for kwarg in kwargs.items())
            _log(
                'Warning: %s(%s) returned %r instead of %r.'
                % (fn_name, args_repr, slave_result, master_result)
            )
        return master_result