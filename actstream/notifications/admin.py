from django.contrib import admin

from actstream.notifications import models


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'action', 'is_read', 'is_deleted', 'level')
    list_filter = ('is_read', 'is_deleted', 'level')
    raw_id_fields = ('recipient', 'action')


admin.site.register(models.Notification, NotificationAdmin)
