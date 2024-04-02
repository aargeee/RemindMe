"""Urls module for reminder."""

from django.urls import path

from .views.reminder import ReminderView

urlpatterns = [
    path("", ReminderView.as_view(), name="reminder"),
]
