"""Django notifications apps file"""

# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class Config(AppConfig):
    name = "notifications"
    verbose_name = _("Notifications")
    default_auto_field = "django.db.models.AutoField"

    def ready(self) -> None:
        super(Config, self).ready()
        # this is for backwards compatibility
        import notifications.signals

        notifications.notify = (  # type: ignore[attr-defined]
            notifications.signals.notify
        )
