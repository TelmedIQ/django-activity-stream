from django.dispatch import Signal

notification = Signal(providing_args=['verb', 'action_object', 'target',
                                      'description', 'timestamp'])
