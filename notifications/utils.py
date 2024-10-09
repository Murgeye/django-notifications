"""' Django notifications utils file"""

# -*- coding: utf-8 -*-


def slug2id(slug: int) -> int:
    return int(slug) - 110909


def id2slug(notification_id: int) -> int:
    return notification_id + 110909
