from flask import current_app


def canceled_message_and_send_mail(message, exception, origin=None):
    if 'mail_service' not in current_app.extensions:
        current_app.logger.warning("Extension 'mail_service' not initialized")
        return 'CANCELLED'  # TODO : choose a different status ?

    subject = 'Message %s CANCELLED par le système' % str(message.id)
    body = """Bonjour,
Le message (id : {id}) de la file {queue} a été automatiquement passé en CANCELLED par le système.

Exception: {error}

Cordialement,
-- Mailer Daemon""".format(id=str(message.id), queue=str(origin), error=str(exception))

    recipients = {}  # [utilisateur.email for utilisateur in administrateurs_nationaux_valides]

    mail = current_app.extensions['mail_service']
    mail.send_threaded(subject=subject, recipients=recipients, body=body)
    return 'CANCELLED'


EVENT_HANDLERS_TEMPLATE = [
    {
        'label': 'Register a user',
        'queue': 'user',
        'processor': 'register_processor',
        'event': 'user.create',
        'on_error_callback': canceled_message_and_send_mail
    },
    {
        'label': 'View user',
        'queue': 'user',
        'processor': 'count_user_viewing_processor',
        'event': 'user.read',
        'on_error_callback': canceled_message_and_send_mail
    },
    {
        'label': 'Update user',
        'queue': 'user',
        'processor': 'notify_user_update',
        'event': 'user.update',
        'on_error_callback': canceled_message_and_send_mail
    },
    {
        'label': 'Delete a user',
        'queue': 'user',
        'processor': 'disable_user_processor',
        'event': 'user.delete',
        'on_error_callback': canceled_message_and_send_mail
    },
]
