from __future__ import unicode_literals, absolute_import
from django.core.exceptions import ImproperlyConfigured

from django.db import models

from django.conf import settings
from actstream import settings as actstream_settings


def assert_soft_delete():
    if not actstream_settings.NOTIFICATIONS_SOFT_DELETE:
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


class Notification(models.Model):

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='stream_notifications')
    action = models.ForeignKey('actstream.Action', related_name='notifications')
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = actstream_settings.get_notification_manager()
    # objects = NotificationManager.from_queryset(NotificationQuerySet)()

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    def mark_as_unread(self):
        if self.is_read:
            self.is_read = False
            self.save()

    def delete(self, using=None):

        if actstream_settings.NOTIFICATIONS_SOFT_DELETE:
            self.soft_delete()
        else:
            super(Notification, self).delete()

    def soft_delete(self):
        if not self.is_deleted:
            self.is_deleted = True
            self.save()
