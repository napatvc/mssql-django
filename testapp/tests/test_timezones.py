# Copyright (c) Microsoft Corporation.
# Licensed under the BSD license.

import datetime
import copy
from django.conf import settings
from django.utils import timezone
from django.test import TestCase
from django.test.utils import override_settings

from ..models import TimeZone

class TestDateTimeField(TestCase):

    def test_iso_week_day(self):
        days = {
            1: TimeZone.objects.create(date=datetime.datetime(2022, 5, 16)),
            2: TimeZone.objects.create(date=datetime.datetime(2022, 5, 17)),
            3: TimeZone.objects.create(date=datetime.datetime(2022, 5, 18)),
            4: TimeZone.objects.create(date=datetime.datetime(2022, 5, 19)),
            5: TimeZone.objects.create(date=datetime.datetime(2022, 5, 20)),
            6: TimeZone.objects.create(date=datetime.datetime(2022, 5, 21)),
            7: TimeZone.objects.create(date=datetime.datetime(2022, 5, 22)),
        }
        for k, v in days.items():
            self.assertSequenceEqual(TimeZone.objects.filter(date__iso_week_day=k), [v])

class TestDateTimeToDateTimeOffsetMigration(TestCase):

    def setUp(self):
        # Want this to be a naive datetime so don't want
        # to override settings before TimeZone creation
        self.time = TimeZone.objects.create()

    def tearDown(self):
        TimeZone.objects.all().delete()

    @override_settings(USE_TZ=True)
    def test_datetime_to_datetimeoffset_utc(self):
        dt = self.time.date

        # Do manual migration from DATETIME2 to DATETIMEOFFSET
        # and local time to UTC
        # with connection.schema_editor() as cursor:
        #     cursor.execute("""
        #         ALTER TABLE [testapp_timezone]
        #            ALTER COLUMN [date] DATETIMEOFFSET;
        #
        #         UPDATE [testapp_timezone]
        #            SET [date] = TODATETIMEOFFSET([date], 0) AT TIME ZONE 'UTC'
        #     """)

        dto = TimeZone.objects.get(id=self.time.id).date
        self.assertEqual(dt, dto.replace(tzinfo=None))

        # try:
        #     self.assertEqual(dt, dto.replace(tzinfo=None))
        # finally:
        #     # Migrate back to DATETIME2 for other unit tests
        #     with connection.schema_editor() as cursor:
        #         cursor.execute("ALTER TABLE [testapp_timezone] ALTER column [date] datetime2")

    @override_settings(USE_TZ=True)
    def test_datetime_to_datetimeoffset_local_timezone(self):
        db = copy.deepcopy(settings.DATABASES)
        db['default']['TIME_ZONE'] = "Africa/Nairobi"
        with override_settings(DATABASES=db):
            dt = TimeZone.objects.create(date=timezone.now())
            dto = TimeZone.objects.get(id=dt.id).date
            self.assertEqual(dt.date - datetime.timedelta(hours=3), dto.replace(tzinfo=None))

    @override_settings(USE_TZ=True, TIME_ZONE="Africa/Nairobi")
    def test_datetime_to_datetimeoffset_other_timezone(self):
        dt = TimeZone.objects.create(date=timezone.now())
        dto = TimeZone.objects.get(id=dt.id).date
        self.assertEqual(dt - datetime.timedelta(hours=7), dto.replace(tzinfo=None))
