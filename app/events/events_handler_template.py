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
        'label': 'declaration.vlsts.cree',  # Pas encore testé avec Rabbit
        'queue': 'immi2',
        'processor': 'declaration_arrivee_en_france',
        'event': 'declaration.vlsts.cree',
        'on_error_callback': canceled_message_and_send_mail,
        'to_rabbit': False
    },
    {
        "label": "fne_batch-declaration.vlsts.cree",
        "to_batch": True,
        "queue": "fne",
        'processor_batch_in': 'fne_batch_processor_in',
        "processor_batch_out": "fne_batch_processor_out",
        "event": "declaration.vlsts.cree",
    },
]


def event_handlers_factory(app):
    event_handlers = EVENT_HANDLERS_TEMPLATE.copy()

    return event_handlers
