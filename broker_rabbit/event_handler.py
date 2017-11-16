from datetime import datetime, timedelta
from traceback import format_exc

from broker_rabbit.processor import find_and_execute

from broker_rabbit.exceptions import (
    ProcessMessageError, ProcessMessageNeedWaitError,
    ProcessMessageNoResponseError, ProcessMessageBadResponseError,
    ProcessMessageSkippedError, ProcessServerNotifyRetryError)


STATUS_FAILURE = 'FAILURE'
STATUS_CANCELLED = 'CANCELLED'
STATUS_SKIPPED = 'SKIPPED'
STATUS_DONE = 'DONE'
STATUS_DELETED = 'DELETED'

BASE_DELAY = 60
MAX_DELAY = 6 * 60 * 60  # 6 hours


class EventError(Exception):
    pass


class UnknownEventHandlerError(EventError):
    pass


class UnknownEventError(EventError):
    pass


def default_callback(message, exception, origin):
    return STATUS_FAILURE


class EventHandlerItem:

    def __repr__(self):
        return ("<{clsname}"
                "(label={self.label}, "
                "origin={self.origin}, "
                "queue={self.queue}, "
                "processor={self.processor}, "
                "processor_batch_in={self.processor_batch_in}, "
                "processor_batch_out={self.processor_batch_out}, "
                "context={self.context}, "
                "event={self.event}, "
                "to_skip={self.to_skip}, "
                "to_rabbit={self.to_rabbit}, "
                "to_batch={self.to_batch}, "
                "discriminant_generator={self.discriminant_generator}, "
                "find_numero_etranger={self.find_numero_etranger}, "
                "on_error_callback={self.on_error_callback}"
                ")>".format(clsname=type(self).__name__, self=self))

    def __init__(self, event_handler_item_data):
        self.label = event_handler_item_data['label']
        self.origin = event_handler_item_data.get('origin')
        self.queue = event_handler_item_data.get('queue')
        self.processor = event_handler_item_data.get('processor')
        self.processor_batch_in = event_handler_item_data.get('processor_batch_in')
        self.processor_batch_out = event_handler_item_data.get('processor_batch_out')
        self.context = event_handler_item_data.get('context')
        self.event = event_handler_item_data.get('event')
        self.to_skip = event_handler_item_data.get('to_skip')
        self.to_rabbit = event_handler_item_data.get('to_rabbit', False)
        self.to_batch = event_handler_item_data.get('to_batch', False)
        self.discriminant_generator = event_handler_item_data.get('discriminant_generator')
        self.find_numero_etranger = event_handler_item_data.get('find_numero_etranger')
        self.find_numero_recueil = event_handler_item_data.get('find_numero_recueil')
        if 'on_error_callback' in event_handler_item_data:
            self.on_error_callback = event_handler_item_data.get('on_error_callback')
        else:
            self.on_error_callback = default_callback

    def modify(self, *args, **kwargs):
        if 'label' in kwargs:
            self.label = kwargs['label']
        if 'origin' in kwargs:
            self.origin = kwargs['origin']
        if 'queue' in kwargs:
            self.queue = kwargs['queue']
        if 'processor' in kwargs:
            self.processor = kwargs['processor']
        if 'processor_batch_in' in kwargs:
            self.processor_batch_in = kwargs['processor_batch_in']
        if 'processor_batch_out' in kwargs:
            self.processor_batch_out = kwargs['processor_batch_out']
        if 'context' in kwargs:
            self.context = kwargs['context']
        if 'event' in kwargs:
            self.event = kwargs['event']
        if 'to_skip' in kwargs:
            self.event = kwargs['to_skip']
        if 'on_error_callback' in kwargs:
            self.on_error_callback = kwargs['on_error_callback']
        if 'to_rabbit' in kwargs:
            self.to_rabbit = kwargs['to_rabbit']
        if 'to_batch' in kwargs:
            self.to_batch = kwargs['to_batch']


class EventHandler:

    def __init__(self, handlers):
        self.items = [EventHandlerItem(eh) for eh in handlers]
        self.count_received_msg = 0

    def process_message(self, received_msg):
        self.count_received_msg += 1
        print('Received message number `%s`, content = {%s}' % (self.count_received_msg, received_msg))

    def execute_rabbit(self, msg):
        handler = self.get(msg.handler)
        if not handler:
            msg.insert_or_update(
                status_comment="Pas de handler pour ce type de message", status=STATUS_FAILURE)
            raise ProcessMessageError(
                "Pas de handler pour traiter le message %s: %s n'est pas un handler valide" %
                (msg.id, msg.handler))

        if msg.status in (STATUS_DONE, STATUS_CANCELLED, STATUS_DELETED):
            return
        elif msg.status == STATUS_FAILURE:
            raise ProcessMessageError('Message %s already in status FAILURE' % msg.id)

        msg.sent = datetime.utcnow()

        if msg.is_folder_on_error():
            msg.insert_or_update(
                status_comment="Le message n'a pas été envoyé du au fait que des"
                               "anciens messages de ce dossier sont tombés en CANCELLED",
                status=STATUS_SKIPPED, returned=datetime.utcnow())
            return

        try:
            result_msg = str(find_and_execute(handler.processor, handler, msg))
        except (ProcessMessageNoResponseError, ProcessServerNotifyRetryError) as exc:
            msg.insert_or_update(
                status_comment=str(exc), status='NEED_WAIT', returned=datetime.utcnow())
            raise ProcessMessageNeedWaitError(
                "Message %s cannot be processed for the moment, wait and retry" % (msg.id))
        except ProcessMessageSkippedError as exc:
            msg.insert_or_update(status_comment="Skipped", status=STATUS_SKIPPED,
                                 returned=datetime.utcnow())
        except ProcessMessageBadResponseError as exc:
            msg.returned = datetime.utcnow()
            new_status = handler.on_error_callback(message=msg, exception=exc, origin=handler.queue)
            msg.insert_or_update(status_comment=str(exc), status=new_status)
            if new_status == STATUS_FAILURE:
                raise ProcessMessageError("Error processing message %s: %s" % (msg.id, str(exc)))
        except:
            msg.returned = datetime.utcnow()
            exc_msg = format_exc()
            new_status = handler.on_error_callback(
                message=msg, exception=exc_msg, origin=handler.queue)
            msg.insert_or_update(status_comment=exc_msg, status=new_status)
            if new_status == STATUS_FAILURE:
                raise ProcessMessageError(
                    "Exception occured during processing message %s: %s" % (msg.id, exc_msg))
        else:
            msg.insert_or_update(
                status_comment=result_msg, status=STATUS_DONE, returned=datetime.utcnow())

    def get(self, label, default=None):
        try:
            return self[label]
        except IndexError:
            return default

    def __getitem__(self, label):
        for item in self.items:
            if item.label == label:
                return item
        raise IndexError()

    def filter(self, event=None, origin=None):
        ret = self.items
        if event:
            ret = [x for x in ret if x.event == event]
        if origin:
            ret = [x for x in ret if x.origin != origin]
        return ret

    def flush(self):
        self.items = []

    def append(self, item):
        if isinstance(item, EventHandlerItem):
            self.items.append(item)
        elif isinstance(item, dict):
            self.items.append(EventHandlerItem(item))
        else:
            raise ValueError()
