class EventError(Exception):
    pass


class UnknownEventHandlerError(EventError):
    pass


class UnknownEventError(EventError):
    pass


class EventMessage:

    def __init__(self, event_message_item):
        self.label = event_message_item['label']
        self.queue = event_message_item.get('queue')
        self.processor = event_message_item.get('processor')
        self.event = event_message_item.get('event')

    def modify(self, **kwargs):
        if 'label' in kwargs:
            self.label = kwargs['label']
        if 'queue' in kwargs:
            self.queue = kwargs['queue']
        if 'processor' in kwargs:
            self.processor = kwargs['processor']
        if 'event' in kwargs:
            self.event = kwargs['event']


class EventManager:

    def __init__(self, handlers):
        self.items = [EventMessage(eh) for eh in handlers]
        self.count_received_msg = 0

    def process_message(self, received_msg):
        print('Received message with content = {%s}' % received_msg)

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
        if isinstance(item, EventMessage):
            self.items.append(item)
        elif isinstance(item, dict):
            self.items.append(EventMessage(item))
        else:
            raise ValueError()
