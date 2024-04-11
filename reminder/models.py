"""Models module for reminder."""

from __future__ import annotations

import datetime
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

REMINDER_TITLE_MAXLEN = 20


def validate_future_datetime(value: datetime.datetime) -> None:
    """Future datetime validator function."""
    today = datetime.datetime.now(tz=datetime.timezone.utc)
    if value.date() == today.date() and value.time() < today.time():
        raise ValidationError("Time cannot be in the past")
    if value.date() < today.date():
        raise ValidationError("Date cannot be in the past")


class Reminder(models.Model):
    """Reminder model to store the title and end-datetime of event."""

    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_title = models.CharField(max_length=REMINDER_TITLE_MAXLEN)
    end_date_time = models.DateTimeField(validators=[validate_future_datetime])

    def __str__(self: Reminder) -> str:
        """Reminder object string representation."""
        return f"{self.reminder_title} - {self.id}"
