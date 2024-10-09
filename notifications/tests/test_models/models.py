from django.db import models
from django.http import HttpRequest

from notifications.models import Notification


class Customer(models.Model):
    name = models.CharField(max_length=64)
    address = models.TextField()

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return f"foo/{self.id}/"


class TargetObject(Customer):
    def get_url_for_notifications(
        self, notification: Notification, request: HttpRequest
    ) -> str:
        return f"bar/{self.id}/"
