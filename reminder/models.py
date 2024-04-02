"""Models module for reminder."""

from __future__ import annotations

import datetime
import uuid

from django.core.exceptions import ValidationError
from django.db import models

REMINDER_TITLE_MAXLEN = 20


class Reminder(models.Model):
    """Reminder model to store the title and end-datetime of event."""

    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    reminder_title = models.CharField(max_length=REMINDER_TITLE_MAXLEN)
    end_date_time = models.DateTimeField()

    def __str__(self: Reminder) -> str:
        """Reminder object string representation."""
        return f"{self.reminder_title} - {self.id}"

    def save(self: Reminder) -> None:
        """Overloading save method."""
        today = datetime.datetime.now(tz=datetime.timezone.utc)
        if (
            self.end_date_time.date() == today.date()
            and self.end_date_time.time() < today.time()
        ):
            msg = "Time cannot be in past"
            raise ValidationError(msg)
        if self.end_date_time.date() < today.date():
            msg = "Date cannot be in past"
            raise ValidationError(msg)
        return super().save()
