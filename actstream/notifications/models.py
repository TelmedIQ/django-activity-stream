from __future__ import unicode_literals, absolute_import
from django.core.exceptions import ImproperlyConfigured

from django.db import models
from django.conf import settings

NOTIFICATIONS_SOFT_DELETE = getattr(settings, 'NOTIFICATIONS_SOFT_DELETE', False)


def assert_soft_delete():
    if not NOTIFICATIONS_SOFT_DELETE:
        msg = """To use 'deleted' field, please set 'NOTIFICATIONS_SOFT_DELETE'=True in settings.
        Otherwise NotificationQuerySet.unread and NotificationQuerySet.read do NOT filter by 'deleted' field.
        """
        raise ImproperlyConfigured(msg)


class NotificationLevel(object):
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3

    CHOICES = (
        (INFO, 'Info'),
        (WARNING, 'Warning'),
        (ERROR, 'Error'),
        (CRITICAL, 'Critical'),
    )


class NotificationQuerySet(models.query.QuerySet):

    def unread(self):
        """Return only unread items in the current queryset"""

        if NOTIFICATIONS_SOFT_DELETE:
            return self.filter(unread=True, is_deleted=False)
        else:
            """ when SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
            In this case, to improve query performance, don't filter by 'deleted' field
            """
            return self.filter(unread=True)

    def read(self):
        """Return only read items in the current queryset"""

        if NOTIFICATIONS_SOFT_DELETE:
            return self.filter(unread=False, is_deleted=False)
        else:
            """ when SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
            In this case, to improve query performance, don't filter by 'deleted' field
            """
            return self.filter(unread=False)

    def mark_all_as_read(self, recipient=None):
        """Mark as read any unread messages in the current queryset.
        Optionally, filter these by recipient first.
        """

        # We want to filter out read ones, as later we will store
        # the time they were marked as read.
        qs = self.unread()
        if recipient:
            qs = qs.filter(recipient=recipient)
        qs.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        """Mark as unread any read messages in the current queryset.
        Optionally, filter these by recipient first.
        """

        qs = self.read()
        if recipient:
            qs = qs.filter(recipient=recipient)
        qs.update(unread=True)

    def deleted(self):
        """Return only deleted items in the current queryset"""

        assert_soft_delete()
        return self.filter(is_deleted=True)

    def active(self):
        """Return only active(un-deleted) items in the current queryset"""

        assert_soft_delete()
        return self.filter(is_deleted=False)

    def mark_all_as_deleted(self, recipient=None):
        """Mark current queryset as deleted.
        Optionally, filter by recipient first.
        """

        assert_soft_delete()
        qs = self.active()
        if recipient:
            qs = qs.filter(recipient=recipient)
        qs.update(deleted=True)

    def mark_all_as_active(self, recipient=None):
        """Mark current queryset as active(un-deleted).
        Optionally, filter by recipient first.
        """

        assert_soft_delete()
        qs = self.deleted()
        if recipient:
            qs = qs.filter(recipient=recipient)
        qs.update(deleted=False)


class NotificationManager(models.Manager):
    pass


class Notification(models.Model):

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='stream_notifications')
    action = models.ForeignKey('actstream.Action', related_name='notifications')
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = NotificationManager.from_queryset(NotificationQuerySet)()

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    def mark_as_unread(self):
        if self.is_read:
            self.is_read = False
            self.save()

    def delete(self, using=None):

        if NOTIFICATIONS_SOFT_DELETE:
            self.soft_delete()
        else:
            super(Notification, self).delete()

    def soft_delete(self):
        if not self.is_deleted:
            self.is_deleted = True
            self.save()
