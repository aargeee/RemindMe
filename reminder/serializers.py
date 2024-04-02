"""Reminder Model serializer."""

from rest_framework import serializers

from .models import REMINDER_TITLE_MAXLEN


class ReminderSerializer(serializers.Serializer):
    """Reminder model serializer."""

    id = serializers.UUIDField()
    reminder_title = serializers.CharField(max_length=REMINDER_TITLE_MAXLEN)
    end_date_time = serializers.DateTimeField()
