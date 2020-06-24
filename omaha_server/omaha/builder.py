# coding: utf-8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""

from builtins import filter
from functools import partial, reduce
from uuid import UUID

from django.utils.timezone import now
from django.db.models import Q

from lxml import etree
from cacheops import cached_as

from omaha import tasks
from omaha.models import Version, PartialUpdate
from omaha.parser import parse_request
from omaha import parser
from omaha.statistics import is_user_active
from omaha.core import (Response, App, Updatecheck_negative, Manifest, Updatecheck_positive,
                  Packages, Package, Actions, Action, Event, Data)


__all__ = ['build_response']


def on_event(event_list, event):
    event_list.append(Event())
    return event_list


def on_data(data_list, data, version):
    name = data.get('name')
    if name == 'untrusted':
        _data = Data('untrusted')
    elif name == 'install':
        index = data.get('index')
        data_obj_list = filter(lambda d: d.index == index, version.app.data_set.all())
        try:
            _data = Data('install', index=index, text=next(data_obj_list).value)
        except StopIteration:
            _data = Data('install', index=index, status='error-nodata')

    data_list.append(_data)
    return data_list


def on_action(action_list, action):
    action = Action(
        event=action.get_event_display(),
        **action.get_attributes()
    )
    action_list.append(action)
    return action_list


def is_new_user(version):
    if version == '':
        return True
    return False


@cached_as(Version, timeout=60)
def _get_versions(app_id, platform, channel, version):
    date = now().date()

    qs = Version.objects.select_related('app')
    qs = qs.filter_by_enabled(app=app_id,
                              platform__name=platform,
                              channels__name=channel)
    if version:
        qs = qs.filter(version__gt=version)
    qs = qs.filter(
        Q(partialupdate__isnull=True) |
        Q(partialupdate__is_enabled=False) |
        Q(
            partialupdate__is_enabled=True,
            partialupdate__start_date__lte=date,
            partialupdate__end_date__gte=date
        )
    )
    qs = qs.prefetch_related("actions", "partialupdate")
    critical = []
    normal = []
    for version in qs.order_by('-version').cache():
        if version.is_critical:
            if not is_new_user(version):
                critical.append(version)
        else:
            normal.append(version)
    return critical + normal

def get_version(app_id, platform, channel, version, userid):
    for v in _get_versions(app_id, platform, channel, version):
        try:
            pu = v.partialupdate
        except PartialUpdate.DoesNotExist:
            pass
        else:
            if pu.exclude_new_users and is_new_user(version):
                continue
            if not is_user_active(pu.active_users, userid):
                continue
            userid_int = UUID(userid).int
            percent = pu.percent
            if not (userid_int % int(100 / percent)) == 0:
                continue
        if v.allowed_user_ids and userid not in v.allowed_user_ids.split('\n'):
            continue
        return v
    raise Version.DoesNotExist

def on_app(apps_list, app, os, userid):
    app_id = app.get('appid')
    version = app.get('version')
    platform = os.get('platform')
    channel = parser.get_channel(app)
    ping = bool(app.findall('ping'))
    events = reduce(on_event, app.findall('event'), [])
    build_app = partial(App, app_id, status='ok', ping=ping, events=events)
    updatecheck = app.findall('updatecheck')

    try:
        version = get_version(app_id, platform, channel, version, userid)
    except Version.DoesNotExist:
        apps_list.append(
            build_app(updatecheck=Updatecheck_negative() if updatecheck else None))
        return apps_list

    data_list = reduce(partial(on_data, version=version), app.findall('data'), [])
    build_app = partial(build_app, data_list=data_list)

    if updatecheck:
        actions = reduce(on_action, version.actions.all(), [])
        updatecheck = Updatecheck_positive(
            urls=[version.file_url],
            manifest=Manifest(
                version=str(version.version),
                packages=Packages([Package(
                    name=version.file_package_name,
                    required='true',
                    size=str(version.file_size),
                    hash=version.file_hash,
                )]),
                actions=Actions(actions) if actions else None,
            )
        )
        apps_list.append(build_app(updatecheck=updatecheck))
    else:
        apps_list.append(build_app())

    return apps_list


def build_response(request, pretty_print=True, ip=None):
    obj = parse_request(request)
    tasks.collect_statistics.apply_async(args=(request, ip), queue='transient')
    userid = obj.get('userid')
    apps = obj.findall('app')
    apps_list = reduce(partial(on_app, os=obj.os, userid=userid), apps, [])
    response = Response(apps_list, date=now())
    return etree.tostring(response, pretty_print=pretty_print,
                          xml_declaration=True, encoding='UTF-8')
