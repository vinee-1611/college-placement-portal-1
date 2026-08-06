"""
notifications.py

Helpers to create in-app notifications.
"""

from models import Notification
from extensions import db


def notify(user_id, title, message="", link=""):
    """Create a notification row for a single user."""
    notification = Notification(user_id=user_id, title=title,
                                message=message[:300], link=link)
    db.session.add(notification)
    return notification


def notify_many(user_ids, title, message="", link=""):
    """Create notifications for many users in one call."""
    for user_id in set(user_ids):
        notify(user_id, title, message, link)
