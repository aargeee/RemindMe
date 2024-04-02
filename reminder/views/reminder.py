"""Reminder app views."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from reminder.models import Reminder
from reminder.serializers import ReminderSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class ReminderView(APIView):
    """Reminder api view."""

    def get(self: ReminderView, _request: Request) -> Response:
        """GET method.

        Returns list of reminders.
        """
        return Response(
            data=ReminderSerializer(Reminder.objects.all(), many=True).data,
            status=status.HTTP_200_OK,
        )

    def delete(self: ReminderView, _request: Request) -> Response:
        """DELETE method.

        deletes Reminder.
        """
        return Response(status=status.HTTP_202_ACCEPTED)
