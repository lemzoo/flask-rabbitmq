from datetime import datetime

from broker_rabbit.event_handler import EventManager
from broker_rabbit.exceptions import UnknownEventError

from broker_rabbit.rabbit.connection_handler import ConnectionHandler
from broker_rabbit.rabbit.producer import Producer

DEFAULT_URL = 'amqp://test:test@localhost:5672/sief-test'
DEFAULT_EXCHANGE = 'SIEF'


class BrokerRabbitMQ:
    """This is a  Message Broker which using RabbitMQ process for publishing
    and consuming message on SIAEF application.
    """

    def __init__(self, app=None, **kwargs):
        """Create a new instance of Broker Rabbit by using the given
        parameters to connect to RabbitMQ.
        """
        self.app = app
        self.event_manager = None
        self.events = None
        self._producer_for_rabbit = None
        self.disable_rabbit = None
        self.rabbit_url = None
        self.exchange_name = None
        self.queues = None

        if self.app is not None:
            self.init_app(self.app, **kwargs)

    def init_app(self, app, event_message_manager=[], config=None):
        """ Init the Broker Dispatcher by using the given configuration instead
        default settings.

        :param app: Current application context
        :param list event_message_manager: Events handlers defined on the SIAEF app
        :param dict config: Config parameters to use for this instance
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        if 'broker' not in app.extensions:
            app.extensions['broker'] = self
        else:
            # Raise an exception if extension already initialized as
            # potentially new configuration would not be loaded.
            raise RuntimeError('Extension already initialized')

        self.app = app
        self.event_manager = EventManager(event_message_manager)

        config = config or app.config
        config.setdefault('RABBIT_MQ_URL', DEFAULT_URL)
        config.setdefault('EXCHANGE_NAME', DEFAULT_EXCHANGE)
        config.setdefault('BROKER_AVAILABLE_EVENTS', [])

        self.events = config['BROKER_AVAILABLE_EVENTS']
        self.rabbit_url = config['RABBIT_MQ_URL']
        self.exchange_name = app.config['EXCHANGE_NAME']
        self.queues = list({eh.queue for eh in self.event_manager.items})

        # Open Connection to RabbitMQ
        connection_handler = ConnectionHandler(self.rabbit_url)
        rabbit_connection = connection_handler.get_current_connection()

        # Setup default producer for rabbit
        self._producer_for_rabbit = Producer(rabbit_connection, self.exchange_name)
        self._producer_for_rabbit.init_env_rabbit(self.queues)

    def send(self, event, origin, context={}):
        """Notify the event_handlers who have subscribed to the given event

        :param event: event to trigger
        :param origin: skip the event handlers with similar origin
        :param context: dict of arbitrary data to transfer
        """
        if event not in self.events:
            raise UnknownEventError('Event %s is not registered' % event)

        event_manager_items = self.event_manager.filter(event)
        for event_message in event_manager_items:
            self.publish_message(event_message, context)

    def publish_message(self, event_message, context):
        """Route the message to the correct to RabbitMQ by with context

        :param event_message: the retrieved event on the Event Manager List
        :param context: the content of the message
        """
        queue = event_message.queue
        message = {
            'created': datetime.utcnow().isoformat(),
            'queue': queue,
            'label': event_message.label,
            'json_context': context,
            'status': 'READY',
        }

        return self._producer_for_rabbit.publish(queue, message)
