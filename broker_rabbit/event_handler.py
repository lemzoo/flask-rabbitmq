from broker_rabbit.processor import find_and_execute


class EventError(Exception):
    pass


class UnknownEventHandlerError(EventError):
    pass


class UnknownEventError(EventError):
    pass


class EventHandlerItem:

    def __init__(self, event_handler_item_data):
        self.label = event_handler_item_data['label']
        self.queue = event_handler_item_data.get('queue')
        self.processor = event_handler_item_data.get('processor')
        self.event = event_handler_item_data.get('event')

    def modify(self, *args, **kwargs):
        if 'label' in kwargs:
            self.label = kwargs['label']
        if 'queue' in kwargs:
            self.queue = kwargs['queue']
        if 'processor' in kwargs:
            self.processor = kwargs['processor']
        if 'event' in kwargs:
            self.event = kwargs['event']


class EventHandler:

    def __init__(self, handlers):
        self.items = [EventHandlerItem(eh) for eh in handlers]
        self.count_received_msg = 0

    def process_message(self, received_msg):
        self.count_received_msg += 1
        print('Received message number `%s`, content = {%s}' % (self.count_received_msg, received_msg))
        # find_and_execute(handler.processor, handler, msg)

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

    def filter(self, event=None):
        ret = self.items
        if event:
            ret = [x for x in ret if x.event == event]
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
