"""Reminder Views test module."""
from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from reminder.models import Reminder

if TYPE_CHECKING:
    from rest_framework.response import Response


class TestReminderView(APITestCase):
    """ReminderView tests."""

    def setUp(self: TestReminderView) -> None:
        """Testcase setup."""
        self.url = reverse("reminder")
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test-user",
            password="test-pass",
        )
        self.ouser = User.objects.create_user(
            username="other-user",
            password="test-pass",
        )
        self.client.login(username="test-user", password="test-pass")
        self.reminder1 = Reminder.objects.create(
            reminder_title="Test Title 1",
            user=self.user,
            end_date_time=datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=2),
        )
        self.reminder2 = Reminder.objects.create(
            reminder_title="Test Title 2",
            user=self.ouser,
            end_date_time=datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=3),
        )

    def test_get_returns_list(self: TestReminderView) -> None:
        """GET request returns list of reminders."""
        self.client.force_authenticate(user=self.user)
        res: Response = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK, "Incorrect status")
        self.assertEqual(len(res.data), 1)  # Only one reminder belongs to the test-user
        self.assertEqual(res.data[0]["reminder_title"], self.reminder1.reminder_title)

    def test_unauthenticated_user(self: TestReminderView) -> None:
        """Unauthenticated user gets 401 status."""
        res: Response = self.client.get(self.url)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect status",
        )
        self.assertTrue("errors" in res.data)
        self.assertEqual(len(res.data["errors"]), 1)
        self.assertTrue("code" in res.data["errors"][0])
        self.assertTrue("detail" in res.data["errors"][0])
        self.assertTrue("attr" in res.data["errors"][0])

    def test_post_creates_reminder(self: TestReminderView) -> None:
        """POST request creates a reminder."""
        self.client.force_authenticate(user=self.user)
        self.assertEqual(Reminder.objects.all().count(), 2)
        res: Response = self.client.post(
            self.url,
            data={
                "reminder_title": "Test Title 3",
                "end_date_time": "2054-04-11T22:15:13Z",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reminder.objects.all().count(), 3)
        self.assertIn("id", res.data)
        obj = Reminder.objects.filter(id=res.data["id"]).values()
        self.assertEqual(obj.count(), 1)
        self.assertEqual(obj[0]["reminder_title"], "Test Title 3")

    def test_post_creates_reminder_seconds(self: TestReminderView) -> None:
        """POST request creates a reminder."""
        self.client.force_authenticate(user=self.user)
        self.assertEqual(Reminder.objects.all().count(), 2)
        res: Response = self.client.post(
            self.url,
            data={
                "reminder_title": "Test Title 3",
                "end_date_time": "2054-04-11T22:15:13Z",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        self.assertEqual(Reminder.objects.all().count(), 3)
        self.assertIn("id", res.data)
        obj = Reminder.objects.filter(id=res.data["id"]).values()
        self.assertEqual(obj.count(), 1)
        self.assertEqual(obj[0]["reminder_title"], "Test Title 3")

    def test_post_creation_wrong_data(self: TestReminderView) -> None:
        """POST request creates a reminder."""
        self.client.force_authenticate(user=self.user)
        self.assertEqual(Reminder.objects.all().count(), 2)
        res: Response = self.client.post(
            self.url,
            data={
                "reminder_title": "Test Title 3",
                "end_date_time": datetime.datetime.now(tz=datetime.timezone.utc)
                - datetime.timedelta(days=4),
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reminder.objects.all().count(), 2)
        self.assertTrue("errors" in res.data)
        self.assertEqual(len(res.data["errors"]), 1)
        self.assertTrue("code" in res.data["errors"][0])
        self.assertTrue("detail" in res.data["errors"][0])
        self.assertTrue("attr" in res.data["errors"][0])

    def test_post_creation_wrong_data_seconds(self: TestReminderView) -> None:
        """POST request creates a reminder."""
        self.client.force_authenticate(user=self.user)
        self.assertEqual(Reminder.objects.all().count(), 2)
        res: Response = self.client.post(
            self.url,
            data={
                "reminder_title": "Test Title 3",
                "end_date_time": datetime.datetime.now(tz=datetime.timezone.utc)
                - datetime.timedelta(seconds=1),
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reminder.objects.all().count(), 2)
        self.assertTrue("errors" in res.data)
        self.assertEqual(len(res.data["errors"]), 1)
        self.assertTrue("code" in res.data["errors"][0])
        self.assertTrue("detail" in res.data["errors"][0])
        self.assertTrue("attr" in res.data["errors"][0])

    def test_post_no_data(self: TestReminderView) -> None:
        """POST request with wrong or missing data."""
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_title(self: TestReminderView) -> None:
        """Test empty title."""
        self.client.force_authenticate(user=self.user)
        self.assertEqual(Reminder.objects.all().count(), 2)
        res: Response = self.client.post(
            self.url,
            data={
                "reminder_title": "",
                "end_date_time": "2054-04-11T22:15:13Z",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reminder.objects.all().count(), 2)
        self.assertTrue("errors" in res.data)
        self.assertEqual(len(res.data["errors"]), 1)
        self.assertTrue("code" in res.data["errors"][0])
        self.assertTrue("detail" in res.data["errors"][0])
        self.assertTrue("attr" in res.data["errors"][0])

    def test_incorrect_datetime_format(self: TestReminderView) -> None:
        """Test empty title."""
        self.client.force_authenticate(user=self.user)
        self.assertEqual(Reminder.objects.all().count(), 2)
        res: Response = self.client.post(
            self.url,
            data={
                "reminder_title": "Title",
                "end_date_time": "somethingwrong",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reminder.objects.all().count(), 2)
        self.assertTrue("errors" in res.data)
        self.assertEqual(len(res.data["errors"]), 1)
        self.assertTrue("code" in res.data["errors"][0])
        self.assertTrue("detail" in res.data["errors"][0])
        self.assertTrue("attr" in res.data["errors"][0])


class TestDeleteReminderView(APITestCase):
    """DeleteReminderView tests."""

    def setUp(self: TestDeleteReminderView) -> None:
        """Testcase setup."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test-user",
            password="test-pass",
        )
        self.ouser = User.objects.create_user(
            username="other-user",
            password="test-pass",
        )
        self.client.login(username="test-user", password="test-pass")
        self.reminder1 = Reminder.objects.create(
            reminder_title="Test Title 1",
            user=self.user,
            end_date_time=datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=2),
        )
        self.reminder2 = Reminder.objects.create(
            reminder_title="Test Title 2",
            user=self.ouser,
            end_date_time=datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=3),
        )
        self.url = reverse("delete-reminder", args=[str(self.reminder1.id)])
        self.bad_url = reverse("delete-reminder", args=[str(uuid.uuid4())])

    def test_delete_deletes_reminder(self: TestDeleteReminderView) -> None:
        """Test delete deletes reminder given id."""
        self.client.force_authenticate(user=self.user)
        self.assertEqual(Reminder.objects.all().count(), 2)
        res: Response = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Reminder.objects.all().count(), 1)

    def test_delete_unauthenticated(self: TestDeleteReminderView) -> None:
        """Test delete deletes reminder given id."""
        self.assertEqual(Reminder.objects.all().count(), 2)
        res: Response = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Reminder.objects.all().count(), 1)

    def test_delete_with_bad_uuid(self: TestDeleteReminderView) -> None:
        """Test delete with bad UUID."""
        self.client.force_authenticate(user=self.user)
        self.assertEqual(Reminder.objects.all().count(), 2)
        res: Response = self.client.delete(self.bad_url)
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(Reminder.objects.all().count(), 2)
