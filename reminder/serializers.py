"""Reminder Model serializer."""

from rest_framework import serializers

from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    """Reminder model serializer."""

    class Meta:
        """METAdata."""

        model = Reminder
        fields = "__all__"
