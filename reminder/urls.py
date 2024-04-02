"""Urls module for reminder."""

from django.urls import path

from .views.reminder import DeleteReminderView, ReminderView

urlpatterns = [
    path("", ReminderView.as_view(), name="reminder"),
    path("<uuid:reminder_id>/", DeleteReminderView.as_view(), name="delete-reminder"),
]
