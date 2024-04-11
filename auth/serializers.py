"""Serializer for User Auth."""

from typing import ClassVar

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Reminder model serializer."""

    class Meta:
        """METAdata."""

        model = User
        fields: ClassVar = ["id", "username", "password"]
