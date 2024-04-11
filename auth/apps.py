"""AppConfig from Auth."""
from django.apps import AppConfig


class AuthConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth"
