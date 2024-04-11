"""Reminder app views."""

from __future__ import annotations

import typing
from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reminder.models import Reminder
from reminder.serializers import ReminderSerializer

if TYPE_CHECKING:
    import uuid

    from rest_framework.request import Request


class ReminderView(APIView):
    """Reminder api view."""

    permission_classes: typing.ClassVar = [IsAuthenticated]

    def get(self: ReminderView, request: Request) -> None:
        """GET method.

        Returns list of reminders.
        """
        user = request.user
        reminders = Reminder.objects.filter(user=user)
        serializer = ReminderSerializer(reminders, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self: ReminderView, request: Request) -> Response:
        """POST: create new reminder."""
        data = request.data.copy()
        data["user"] = request.user.id
        serializer = ReminderSerializer(data=data)

        if not serializer.is_valid():
            raise ValidationError(
                detail=serializer.errors,
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        reminder = serializer.save()
        serialized = ReminderSerializer(reminder).data

        return Response(data=serialized, status=status.HTTP_201_CREATED)


class DeleteReminderView(APIView):
    """Delete Reminder view."""

    def delete(
        self: DeleteReminderView,
        _request: Request,
        reminder_id: uuid.UUID,
    ) -> Response:
        """Delete method."""
        try:
            reminder = Reminder.objects.get(id=reminder_id)
        except Reminder.DoesNotExist:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            reminder.delete()
        except Exception as e:  # noqa: BLE001
            raise APIException(  # noqa: B904
                detail=e,
                code=status.HTTP_304_NOT_MODIFIED,
            )
        return Response(status=status.HTTP_202_ACCEPTED)
