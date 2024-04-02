"""Register models to admin app."""
# Register your models here.

from django.contrib import admin

from .models import Reminder

admin.site.register(Reminder)
