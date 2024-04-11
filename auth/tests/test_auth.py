"""Tests for Login."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

if TYPE_CHECKING:
    from rest_framework.response import Response


class TestSignUpView(APITestCase):
    """Signup tests."""

    def setUp(self: TestSignUpView) -> None:
        """Signup tests Setup."""
        super().setUp()
        self.url = reverse("signup")
        self.client = APIClient()
        self.existing_user = User.objects.create(username="existing-user")

    def test_register_new_user(self: TestSignUpView) -> None:
        """Test register new user."""
        payload = {
            "username": "test-user",
            "password": "test-pass",
        }
        res = self.client.post(self.url, data=payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        resdata: list[dict[str, str]] = json.loads(res.content)
        self.assertEqual(
            resdata,
            {
                "success": True,
                "data": {
                    "detail": "User Created.",
                },
            },
        )

    def test_duplicate_username(self: TestSignUpView) -> None:
        """Test duplicate username."""
        payload = {
            "username": "existing-user",
            "password": "password",
        }
        self.assertEqual(User.objects.all().count(), 1)
        res = self.client.post(self.url, data=payload)
        resdata: list[dict[str, str]] = json.loads(res.content)
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(resdata["success"])
        self.assertEqual(len(resdata["data"]["errors"]), 1)
        self.assertTrue("username" in resdata["data"]["errors"])
        self.assertEqual(
            resdata["data"]["errors"]["username"],
            ["A user with that username already exists."],
        )
        self.assertEqual(User.objects.all().count(), 1)

    def test_invalid_username(self: TestSignUpView) -> None:
        """Test invalid username."""
        usernames = ["I am user", "world%user", "**allhailuser**", "#loluser"]
        for username in usernames:
            payload = {
                "username": username,
                "password": "pass",
            }
            res = self.client.post(self.url, data=payload)
            resdata: list[dict[str, str]] = json.loads(res.content)
            self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            self.assertFalse(resdata["success"])
            self.assertEqual(len(resdata["data"]["errors"]), 1)
            self.assertTrue("username" in resdata["data"]["errors"])
            self.assertEqual(
                resdata["data"]["errors"]["username"],
                [
                    "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.",
                ],
            )

    def test_missing_data(self: TestSignUpView) -> None:
        """Test missing data."""
        res = self.client.post(self.url)
        resdata: list[dict[str, str]] = json.loads(res.content)
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(resdata["success"])
        self.assertEqual(len(resdata["data"]["errors"]), 2)
        self.assertTrue("username" in resdata["data"]["errors"])
        self.assertTrue("password" in resdata["data"]["errors"])
        self.assertEqual(
            resdata["data"]["errors"]["username"],
            ["This field is required."],
        )
        self.assertEqual(
            resdata["data"]["errors"]["password"],
            ["This field is required."],
        )

    def test_empty_data(self: TestSignUpView) -> None:
        """Test missing data."""
        payload = {
            "username": "",
            "password": "",
        }
        res = self.client.post(self.url, data=payload)
        resdata: list[dict[str, str]] = json.loads(res.content)
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(resdata["success"])
        self.assertEqual(len(resdata["data"]["errors"]), 2)
        self.assertTrue("username" in resdata["data"]["errors"])
        self.assertTrue("password" in resdata["data"]["errors"])
        self.assertEqual(
            resdata["data"]["errors"]["username"],
            ["This field may not be blank."],
        )
        self.assertEqual(
            resdata["data"]["errors"]["password"],
            ["This field may not be blank."],
        )

    def test_short_password(self: TestSignUpView) -> None:
        """Test short password."""
        self.assertEqual(User.objects.all().count(), 1)
        payload = {
            "username": "test-user",
            "password": "pass",
        }
        with self.assertRaisesMessage(
            ValidationError,
            "['This password is too short. It must contain at least 9 characters.', 'This password is too common.']",
        ):
            self.client.post(self.url, data=payload)
        self.assertEqual(User.objects.all().count(), 1)

    def test_weak_password(self: TestSignUpView) -> None:
        """Test weak password."""
        self.assertEqual(User.objects.all().count(), 1)
        payload = {
            "username": "test-user",
            "password": "password1",
        }
        with self.assertRaisesMessage(
            ValidationError,
            "['This password is too common.']",
        ):
            self.client.post(self.url, data=payload)
        self.assertEqual(User.objects.all().count(), 1)

    def test_username_length(self: TestSignUpView) -> None:
        """Test long username."""
        payload = {
            "username": "a" * 151,
            "password": "usbkas389@fb",
        }
        resp = self.client.post(self.url, data=payload)
        self.assertEqual(resp.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        resdata: list[dict[str, str]] = json.loads(resp.content)
        self.assertEqual(
            resdata,
            {
                "success": False,
                "data": {
                    "errors": {
                        "username": [
                            "Ensure this field has no more than 150 characters.",
                        ],
                    },
                },
            },
        )


class TestLoginView(APITestCase):
    """Login Tests."""

    def setUp(self: TestLoginView) -> None:
        """Login tests Setup."""
        self.url = reverse("login")
        self.client = APIClient()
        self.existing_user = User.objects.create_user(
            username="test-user",
            password="test-pass",
        )

    def test_login(self: TestLoginView) -> None:
        """Test successful login."""
        payload = {
            "username": "test-user",
            "password": "test-pass",
        }
        res: Response = self.client.post(self.url, data=payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["success"])
        self.assertTrue("data" in res.data)
        self.assertTrue("token" in res.data["data"])

    def test_incorrect_username(self: TestLoginView) -> None:
        """Test with incorrect username."""
        payload = {
            "username": "non-existing-user",
            "password": "test-pass",
        }
        res: Response = self.client.post(self.url, data=payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(res.data["success"])
        self.assertTrue("data" in res.data)
        self.assertTrue("detail" in res.data["data"])

    def test_incorrect_password(self: TestLoginView) -> None:
        """Test incorrect password."""
        payload = {
            "username": "test-user",
            "password": "wrong-password",
        }
        res: Response = self.client.post(self.url, data=payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(res.data["success"])
        self.assertTrue("data" in res.data)
        self.assertTrue("detail" in res.data["data"])

    def test_missing_credentials(self: TestLoginView) -> None:
        """Test missing credentails."""
        res: Response = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data["success"])
        self.assertTrue("data" in res.data)
        self.assertTrue("detail" in res.data["data"])
