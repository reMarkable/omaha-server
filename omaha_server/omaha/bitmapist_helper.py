"""
We use bitmapist to store usage statistics, such as the number of update
requests per day. The default backend for bitmapist is Redis. However, due to
the way bitmapist is implemented, this results in overwhelming RAM usage. To be
precise, bitmapist uses bit strings to store information. Eg. "did user 13 make
an update request on August 6" is stored as a binary 1 in the bit string for
August 6.

Not surprisingly, bitmapist's approach leads to huge RAM consumption. For
example, for every new day there's a new bit string, stored in RAM, of length
equal to the number of users. At the time of this writing, the RAM thus
required is well over 30GB.

To work around this, the creators of bitmapist created their own Redis
implementation, bitmapist-server. It optimises the RAM usage of bit strings.
Instead of tens of GB, it only needs a few hundred MB to store the same
information.

This module configures bitmapist to use bitmapist-server instead of Redis.
"""

from django.conf import settings
from redis import Redis

import bitmapist

def init():
    bitmapist.SYSTEMS['default'] = \
        _BitmapistRedis(settings.BITMAPIST_HOST, settings.BITMAPIST_PORT)

class _BitmapistRedis(Redis):
    def flushdb(self):
        # Bitmapist doesn't implement the FLUSHDB command. Our tests require it
        # though, in particular for tearDown(). So implement it here:
        keys = self.keys()
        if keys:
            self.delete(*keys)