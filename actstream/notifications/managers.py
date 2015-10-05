from __future__ import unicode_literals, absolute_import


from django.db import models

from actstream import settings as actstream_settings
from actstream.notifications.models import assert_soft_delete


class NotificationQuerySet(models.query.QuerySet):

    def unread(self):
        """Return only unread items in the current queryset"""

        if actstream_settings.NOTIFICATIONS_SOFT_DELETE:
            return self.filter(unread=True, is_deleted=False)
        else:
            """ when SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
            In this case, to improve query performance, don't filter by 'deleted' field
            """
            return self.filter(unread=True)

    def read(self):
        """Return only read items in the current queryset"""

        if actstream_settings.NOTIFICATIONS_SOFT_DELETE:
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
