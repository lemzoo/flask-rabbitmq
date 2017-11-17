from datetime import datetime, timedelta
from traceback import format_exc

from broker_rabbit.processor import find_and_execute


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

    def __init__(self, event_handler_item_data):
        self.label = event_handler_item_data['label']
        self.queue = event_handler_item_data.get('queue')
        self.processor = event_handler_item_data.get('processor')
        self.event = event_handler_item_data.get('event')
        self.to_skip = event_handler_item_data.get('to_skip')
        self.on_error_callback = event_handler_item_data.get('on_error_callback', default_callback)

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
        # result_msg = str(find_and_execute(handler.processor, handler, msg))
        print('Received message number `%s`, content = {%s}' % (self.count_received_msg, received_msg))

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
