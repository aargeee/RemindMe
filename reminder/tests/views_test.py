"""Reminder Views test module."""
from __future__ import annotations

import datetime
import json
import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from reminder.models import Reminder
from reminder.serializers import ReminderSerializer


class TestReminderView(APITestCase):
    """ReminderView tests."""

    def setUp(self: TestReminderView) -> None:
        """Testcase setup."""
        self.url = reverse("reminder")
        self.client = APIClient()
        self.reminder1: dict[str, str] = dict(
            ReminderSerializer(
                Reminder.objects.create(
                    reminder_title="Test Title 1",
                    end_date_time=datetime.datetime.now(tz=datetime.timezone.utc)
                    + datetime.timedelta(days=2),
                ),
            ).data,
        )
        self.reminder2: dict[str, str] = dict(
            ReminderSerializer(
                Reminder.objects.create(
                    reminder_title="Test Title 2",
                    end_date_time=datetime.datetime.now(tz=datetime.timezone.utc)
                    + datetime.timedelta(days=3),
                ),
            ).data,
        )

    def test_get_returns_list(self: TestReminderView) -> None:
        """GET request returns list of reminders."""
        res = self.client.get(self.url)
        assert res.status_code == status.HTTP_200_OK, "Incorrect status"
        resdata: list[dict[str, str]] = json.loads(res.content)
        self.assertEqual(resdata, [self.reminder1, self.reminder2])

    def test_post_creates_reminder(self: TestReminderView) -> None:
        """POST request creates a reminder."""
        self.assertEqual(Reminder.objects.all().count(), 2)
        res = self.client.post(
            self.url,
            data={
                "reminder_title": "Test Title 3",
                "end_date_time": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(days=4),
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reminder.objects.all().count(), 3)
        resdata = json.loads(res.content)
        self.assertIn("id", resdata)
        obj = Reminder.objects.filter(id=resdata["id"]).values()
        self.assertEqual(obj.count(), 1)
        self.assertEqual(obj[0]["reminder_title"], "Test Title 3")

    def test_post_no_data(self: TestReminderView) -> None:
        """POST request no data returns Validation error."""
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_wrong_data(self: TestReminderView) -> None:
        """POST request with wrong or missing data."""
        self.assertEqual(Reminder.objects.all().count(), 2)
        res = self.client.post(
            self.url,
            data={
                "title": "Test Title 3",
                "end_date_time": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(days=4),
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestDeleteReminderView(APITestCase):
    """DeleteReminderView tests."""

    def setUp(self: TestDeleteReminderView) -> None:
        """Testcase setup."""
        self.reminder1: dict[str, str] = dict(
            ReminderSerializer(
                Reminder.objects.create(
                    reminder_title="Test Title 1",
                    end_date_time=datetime.datetime.now(tz=datetime.timezone.utc)
                    + datetime.timedelta(days=2),
                ),
            ).data,
        )
        self.reminder2: dict[str, str] = dict(
            ReminderSerializer(
                Reminder.objects.create(
                    reminder_title="Test Title 2",
                    end_date_time=datetime.datetime.now(tz=datetime.timezone.utc)
                    + datetime.timedelta(days=3),
                ),
            ).data,
        )
        self.client = APIClient()
        self.url = reverse("delete-reminder", args=[self.reminder1["id"]])
        return super().setUp()

    def test_delete_deletes_reminder(self: TestDeleteReminderView) -> None:
        """Test delete deletes reminder given id."""
        self.assertEqual(Reminder.objects.all().count(), 2)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Reminder.objects.all().count(), 1)

    def test_delete_with_bad_uuid(self: TestDeleteReminderView) -> None:
        """Test delete with bad UUID."""
        url = reverse("delete-reminder", args=[str(uuid.uuid4())])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
