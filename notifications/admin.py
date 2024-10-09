"""Django notifications admin file"""

# -*- coding: utf-8 -*-
import typing

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.utils.translation import gettext_lazy
from swapper import load_model  # type: ignore[import-untyped]

from notifications.base.admin import AbstractNotificationAdmin
from notifications.base.models import AbstractNotification

Notification = load_model("notifications", "Notification")
if typing.TYPE_CHECKING:
    pass


def mark_unread(
    _modeladmin: "NotificationAdmin",
    _request: HttpRequest,
    queryset: QuerySet[AbstractNotification],
) -> HttpResponseBase | None:
    queryset.update(unread=True)
    return None


mark_unread.short_description = gettext_lazy("Mark selected notifications as unread")  # type: ignore[attr-defined]


class NotificationAdmin(AbstractNotificationAdmin):
    readonly_fields = (
        "recipient",
        "action_object_url",
        "actor_object_url",
        "target_object_url",
    )
    list_display = ("recipient", "actor", "level", "target", "unread", "public")
    list_filter = (
        "level",
        "unread",
        "public",
        "timestamp",
    )
    actions = [mark_unread]

    def get_queryset(self, request: HttpRequest) -> QuerySet[AbstractNotification]:
        qs = super(NotificationAdmin, self).get_queryset(request)
        return qs.prefetch_related("actor")


admin.site.register(Notification, NotificationAdmin)
