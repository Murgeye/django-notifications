# -*- coding: utf-8 -*-
"""Django Notifications example views"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import (
    Http404,
    HttpRequest,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    JsonResponse,
)
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.generic import ListView
from swapper import load_model  # type: ignore[import-untyped]

from notifications import settings as notification_settings
from notifications.helpers import get_notification_list
from notifications.utils import slug2id

Notification = load_model("notifications", "Notification")

if TYPE_CHECKING:

    from notifications.models import Notification as NotificationCls


class NotificationViewList(ListView["NotificationCls"]):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = notification_settings.get_config()["PAGINATE_BY"]

    @method_decorator(login_required)
    def dispatch(
        self, request: HttpRequest, *args: list[Any], **kwargs: dict[Any, Any]
    ) -> HttpResponseBase:
        return super(NotificationViewList, self).dispatch(request, *args, **kwargs)


class AllNotificationsList(NotificationViewList):
    """
    Index page for authenticated user
    """

    def get_queryset(self) -> QuerySet["NotificationCls"]:
        if notification_settings.get_config()["SOFT_DELETE"]:
            qset = Notification.objects.filter(
                recipient=self.request.user.id,  # type: ignore[union-attr]
                active=True,
            )
        else:
            qset = Notification.objects.filter(recipient=self.request.user.id)  # type: ignore[union-attr]
        return cast(QuerySet["NotificationCls"], qset)


class UnreadNotificationsList(NotificationViewList):
    def get_queryset(self) -> QuerySet["NotificationCls"]:
        return cast(
            QuerySet["NotificationCls"],
            Notification.objects.filter(recipient=self.request.user.id, unread=True),  # type: ignore[union-attr]
        )


@login_required
def mark_all_as_read(
    request: HttpRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    notifications = Notification.objects.filter(recipient=request.user.id)  # type: ignore[union-attr]
    notifications.mark_all_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))
    return redirect("notifications:unread")

@login_required
def delete_all(
    request: HttpRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    notifications = Notification.objects.filter(recipient=request.user.id)  # type: ignore[union-attr]
    notifications.delete_all()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))
    return redirect("notifications:unread")

@login_required
def mark_as_read(
    request: HttpRequest, slug: int | None = None
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    if slug is None:
        raise Http404()
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id
    )
    notification.mark_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:unread")


@login_required
def mark_as_unread(
    request: HttpRequest, slug: int | None = None
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    if slug is None:
        raise Http404()
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification,
        recipient=request.user.id,  # type: ignore[union-attr]
        id=notification_id,
    )
    notification.mark_as_unread()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:unread")


@login_required
def delete(
    request: HttpRequest, slug: int | None = None
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    if slug is None:
        raise Http404()
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification,
        recipient=request.user.id,  # type: ignore[union-attr]
        id=notification_id,
    )

    if notification_settings.get_config()["SOFT_DELETE"]:
        notification.deleted = True
        notification.save()
    else:
        notification.delete()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:all")


@never_cache
def live_unread_notification_count(request: HttpRequest) -> JsonResponse:
    user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {"unread_count": 0}
    else:
        data = {
            "unread_count": Notification.objects.filter(
                recipient=request.user.id,  # type: ignore[union-attr]
                unread=True,
            ).count(),
        }
    return JsonResponse(data)


@never_cache
def live_unread_notification_list(request: HttpRequest) -> JsonResponse:
    """Return a json with a unread notification list"""
    user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {"unread_count": 0, "unread_list": []}
        return JsonResponse(data)

    unread_list = get_notification_list(request, "unread")

    data = {
        "unread_count": Notification.objects.filter(
            recipient=request.user.id,  # type: ignore[union-attr]
            unread=True,
        ).count(),
        "unread_list": unread_list,
    }
    return JsonResponse(data)


@never_cache
def live_all_notification_list(request: HttpRequest) -> JsonResponse:
    """Return a json with a unread notification list"""
    user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {"all_count": 0, "all_list": []}
        return JsonResponse(data)

    all_list = get_notification_list(request)

    data = {
        "all_count": Notification.objects.filter(recipient=request.user.id).count(),  # type: ignore[union-attr]
        "all_list": all_list,
    }
    return JsonResponse(data)


def live_all_notification_count(request: HttpRequest) -> JsonResponse:
    user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {"all_count": 0}
    else:
        data = {
            "all_count": Notification.objects.filter(recipient=request.user.id).count(),  # type: ignore[union-attr]
        }
    return JsonResponse(data)
