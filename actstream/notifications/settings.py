from django.conf import settings

SETTINGS = getattr(settings, 'ACTSTREAM_SETTINGS', {})


def get_notification_queryset():
    """
    Returns the class of the action manager to use from ACTSTREAM_SETTINGS['NOTIFICATION_QUERYSET']
    """
    mod = SETTINGS.get('NOTIFICATION_QUERYSET', 'actstream.notifications.managers.NotificationQuerySet')
    mod_path = mod.split('.')

    try:
        return getattr(__import__('.'.join(mod_path[:-1]), {}, {},
                                  [mod_path[-1]]), mod_path[-1])()

    except ImportError:
        raise ImportError('Cannot import %s try fixing ACTSTREAM_SETTINGS[NOTIFICATION_QUERYSET]'
                          'setting.' % mod)


def get_notification_manager():
    """
    Returns the class of the action manager to use from ACTSTREAM_SETTINGS['NOTIFICATION_MANAGER']
    """
    mod = SETTINGS.get('NOTIFICATION_MANAGER', 'actstream.notifications.managers.NotificationManager')
    mod_path = mod.split('.')

    try:
        manager = getattr(__import__('.'.join(mod_path[:-1]), {}, {},
                                     [mod_path[-1]]), mod_path[-1])()
        queryset = get_notification_queryset()
        return manager.from_queryset(queryset)()

    except ImportError:
        raise ImportError('Cannot import %s try fixing ACTSTREAM_SETTINGS[NOTIFICATION_MANAGER]'
                          'setting.' % mod)

NOTIFICATIONS_SOFT_DELETE = SETTINGS.get('NOTIFICATIONS_SOFT_DELETE', False)