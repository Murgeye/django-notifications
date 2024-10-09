from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from notifications.base.models import AbstractNotification


class AbstractNotificationAdmin(admin.ModelAdmin[AbstractNotification]):
    list_display = ("recipient", "actor", "level", "target", "unread", "public")
    list_filter = (
        "level",
        "unread",
        "public",
        "timestamp",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[AbstractNotification]:  # type: ignore
        qs = super(AbstractNotificationAdmin, self).get_queryset(request)
        return qs.prefetch_related("actor")
