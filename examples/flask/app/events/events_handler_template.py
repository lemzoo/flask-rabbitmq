EVENT_MESSAGE_MANAGER = [
    {
        'label': 'Register a user',
        'queue': 'user',
        'processor': 'register_processor',
        'event': 'user.create'
    },
    {
        'label': 'View user',
        'queue': 'user',
        'processor': 'count_user_viewing_processor',
        'event': 'user.read'
    },
    {
        'label': 'Update user',
        'queue': 'user',
        'processor': 'notify_user_update',
        'event': 'user.update'
    },
    {
        'label': 'Delete a user',
        'queue': 'user',
        'processor': 'disable_user_processor',
        'event': 'user.delete'
    },
]
