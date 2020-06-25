# coding: utf8

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
from datetime import datetime, timedelta
from functools import partial

from cacheops import invalidate_all as invalidate_model_caches
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from xmlunittest import XmlTestMixin
from freezegun import freeze_time
from mock import patch
from bitmapist import DayEvents, get_redis

from omaha.tests import fixtures, OverloadTestStorageMixin
from omaha.tests.utils import temporary_media_root

from omaha.factories import ApplicationFactory, ChannelFactory, PlatformFactory, VersionFactory
from omaha.models import Action, Request, EVENT_DICT_CHOICES, Data, NAME_DATA_DICT_CHOICES, Version
from omaha.utils import get_id


class UpdateViewTest(OverloadTestStorageMixin, TestCase, XmlTestMixin):
    model = Version

    def setUp(self):
        self.client = Client()
        get_redis().flushdb()
        super(UpdateViewTest, self).setUp()

    def tearDown(self):
        get_redis().flushdb()
        # We are creating Version objects, which builder.py caches.
        # Prevent cross-test dependencies by clearing caches here.
        invalidate_model_caches()
        super(UpdateViewTest, self).tearDown()

    @freeze_time('2014-01-01 15:41:48')  # 56508 sec
    def test_updatecheck_negative(self):
        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_negative)

    @freeze_time('2014-01-01 15:41:48')  # 56508 sec
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_updatecheck_positive(self):
        self._set_up_positive_updatecheck()
        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_positive)

    def _set_up_positive_updatecheck(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        platform = PlatformFactory.create(name='win')
        channel = ChannelFactory.create(name='stable')
        obj = self._create_version(app, platform, (channel,), '13.0.782.112', './chrome_installer.exe')

        Action.objects.create(
            version=obj,
            arguments='--do-not-launch-chrome',
            event=EVENT_DICT_CHOICES['install'],
            run='chrome_installer.exe'
        )

        Action.objects.create(
            version=obj,
            event=EVENT_DICT_CHOICES['postinstall'],
            other=dict(
                version='13.0.782.112',
                onsuccess='exitsilentlyonlaunchcmd',
            )
        )

        return app, platform, channel

    @freeze_time('2014-01-01 15:41:48')  # 56508 sec
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_updatecheck_allowed_oem_ids(self):
        app, platform, channel = self._set_up_positive_updatecheck()
        v = self._create_version(
            app, platform, (channel,), '13.0.782.111', './chrome_installer_critical.exe',
            is_critical=True, allowed_oem_ids='some-nonexistent-device-id'
        )

        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_positive)

        v.allowed_oem_ids = 'RM110-000-0113'
        v.save()

        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check,
                                    content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_postitive_critical)


    def _create_version(self, app, platform, channels, version, file_name, **kwargs):
        # Give each version / file different contents, so our tests pick up wrong SHA-256s:
        contents = (version + file_name).encode('utf-8')
        obj = VersionFactory.create(
            app=app,
            platform=platform,
            channels=channels,
            version=version,
            file=SimpleUploadedFile(file_name, contents),
            file_size=len(contents),
            **kwargs)
        # Force a constant file_hash:
        obj.file_hash = 'VXriGUVI0TNqfLlU02vBel4Q3Zo='
        obj.save()
        return obj


    @freeze_time('2014-01-01 15:41:48')  # 56508 sec
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_updatecheck_positive_critical(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        platform = PlatformFactory.create(name='win')
        channel = ChannelFactory.create(name='stable')

        create_version = partial(self._create_version, app, platform, (channel,))
        create_version('13.0.782.110', './chrome_installer_first.exe')
        create_version('13.0.782.111', './chrome_installer_critical.exe', is_critical=True)
        create_version('13.0.782.112', './chrome_installer.exe')

        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_postitive_critical)


    @freeze_time('2014-01-01 15:41:48')  # 56508 sec
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_updatecheck_positive_critical_on_other_channel(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        platform = PlatformFactory.create(name='win')
        channel = ChannelFactory.create(name='stable')
        channel2 = ChannelFactory.create(name='alpha')

        create_version = partial(self._create_version, app, platform)
        create_version((channel, channel2), '13.0.782.110', './chrome_installer_first.exe')
        create_version((channel2,), '13.0.782.111', './chrome_installer_critical.exe', is_critical=True)
        last_version = create_version(
            (channel, channel2), '13.0.782.112', './chrome_installer.exe')

        Action.objects.create(
            version=last_version,
            arguments='--do-not-launch-chrome',
            event=EVENT_DICT_CHOICES['install'],
            run='chrome_installer.exe'
        )

        Action.objects.create(
            version=last_version,
            event=EVENT_DICT_CHOICES['postinstall'],
            other=dict(
                version='13.0.782.112',
                onsuccess='exitsilentlyonlaunchcmd',
            )
        )

        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_positive)



    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_userid_counting(self):
        now = datetime.utcnow()
        userid = '{D0BBD725-742D-44ae-8D46-0231E881D58E}'
        user_id = get_id(userid)
        appid1 = '{430FD4D0-B729-4F61-AA34-91526481799D}'
        appid2 = '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}'
        install_date = datetime(year=2014, month=1, day=1, hour=15, minute=41, second=48)
        update_date = install_date + timedelta(days=31)

        request_events = DayEvents('request', install_date.year, install_date.month, install_date.day)
        app1_install_events = DayEvents('new_install:%s' % appid1, install_date.year, install_date.month, install_date.day)
        app2_install_events = DayEvents('new_install:%s' % appid2, install_date.year, install_date.month, install_date.day)
        app1_update_events = DayEvents('request:%s' % appid1, update_date.year, update_date.month, update_date.day)
        app2_update_events = DayEvents('request:%s' % appid2, update_date.year, update_date.month, update_date.day)

        self.assertEqual(len(request_events), 0)
        self.assertEqual(len(app1_install_events), 0)
        self.assertEqual(len(app2_install_events), 0)

        app = ApplicationFactory.create(id=appid2, name='chrome')
        platform = PlatformFactory.create(name='win')
        channel = ChannelFactory.create(name='stable')
        channel2 = ChannelFactory.create(name='alpha')

        obj = self._create_version(
            app, platform, (channel, channel2), '13.0.782.112', './chrome_installer.exe')

        Action.objects.create(
            version=obj,
            arguments='--do-not-launch-chrome',
            event=EVENT_DICT_CHOICES['install'],
            run='chrome_installer.exe'
        )

        Action.objects.create(
            version=obj,
            event=EVENT_DICT_CHOICES['postinstall'],
            other=dict(
                version='13.0.782.112',
                onsuccess='exitsilentlyonlaunchcmd',
            )
        )

        with freeze_time(install_date):  # 56508 sec
            self.client.post(reverse('update'),
                             fixtures.request_update_check, content_type='text/xml')
            self.client.post(reverse('update'),
                             fixtures.request_event_install_success, content_type='text/xml')

        self.assertEqual(len(request_events), 1)
        self.assertEqual(len(app1_install_events), 0)
        self.assertEqual(len(app2_install_events), 1)
        self.assertEqual(len(app1_update_events), 0)
        self.assertEqual(len(app2_update_events), 0)
        self.assertTrue(user_id in request_events)
        self.assertFalse(user_id in app1_install_events)
        self.assertTrue(user_id in app2_install_events)

        with freeze_time(update_date):
            self.client.post(reverse('update'),
                             fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(len(app1_update_events), 0)
        self.assertEqual(len(app2_update_events), 1)
        self.assertFalse(user_id in app1_update_events)
        self.assertTrue(user_id in app2_update_events)

    @freeze_time('2014-01-01 15:45:54')  # 56754 sec
    def test_event(self):
        response = self.client.post(reverse('update'),
                                    fixtures.request_event,
                                    REMOTE_ADDR="8.8.8.8",
                                    content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_event)

        request = Request.objects.get()
        self.assertEqual(request.ip, '8.8.8.8')

    @freeze_time('2014-01-01 15:45:54')  # 56754 sec
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_data(self):
        app = ApplicationFactory.create(id='{430FD4D0-B729-4F61-AA34-91526481799D}', name='chrome')
        platform = PlatformFactory.create(name='win')
        channel = ChannelFactory.create(name='stable')

        self._create_version(app, platform, (channel,), '13.0.782.112', './chrome_installer.exe')

        Data.objects.create(
            app=app,
            name=NAME_DATA_DICT_CHOICES['install'],
            index='verboselogging',
            value='app-specific values here')

        Data.objects.create(
            app=app,
            name=NAME_DATA_DICT_CHOICES['untrusted'])

        response = self.client.post(reverse('update'),
                                    fixtures.request_data, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_data)

    def test_bad_request(self):
        response = self.client.post(reverse('update'))

        msg = b"""<?xml version="1.0" encoding="utf-8"?>
<data>
    <message>
        Bad Request
    </message>
</data>"""
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, msg)
