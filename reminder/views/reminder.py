"""Reminder app views."""

from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ReminderView(APIView):
    """Reminder api view."""

    def get(self: ReminderView) -> Response:
        """GET method.

        Returns list of reminders.
        """
        return Response(data="Hello", status=status.HTTP_200_OK)
