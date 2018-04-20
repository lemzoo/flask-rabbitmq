from datetime import datetime

from broker_rabbit.exceptions import UnknownQueueError

from broker_rabbit.connection_handler import ConnectionHandler
from broker_rabbit.producer import Producer

DEFAULT_URL = 'amqp://test:test@localhost:5672/foo-test'
DEFAULT_EXCHANGE_NAME = 'FOO-EXCHANGE'
DEFAULT_APPLICATION_ID = 'FOO-APPLICATION-ID'
DEFAULT_DELIVERY_MODE = 2
STATUS_READY = 'READY'


class BrokerRabbitMQ:
    """Message Broker based on RabbitMQ middleware"""

    def __init__(self, app=None, queues=None):
        """
        Create a new instance of Broker Rabbit by using
        the given parameters to connect to RabbitMQ.
        """
        self.app = app
        self.queues = queues
        self.connection_handler = None
        self.producer = None
        self.url = None
        self.exchange_name = None
        self.application_id = None
        self.delivery_mode = None
        self.on_message_callback = None

        if self.app is not None:
            self.init_app(self.app, self.queues)

    def init_app(self, app, queues, on_message_callback):
        """ Init the Broker by using the given configuration instead
        default settings.

        :param app: Current application context
        :param list queues: Queues which the message will be post
        :param callback on_message_callback: callback to execute when new
        message is pulled to RabbitMQ
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        if 'broker_rabbit' not in app.extensions:
            app.extensions['broker_rabbit'] = self
        else:
            # Raise an exception if extension already initialized as
            # potentially new configuration would not be loaded.
            raise RuntimeError('Extension already initialized')

        self.url = app.config.get('RABBIT_MQ_URL', DEFAULT_URL)
        self.exchange_name = app.config.get('EXCHANGE_NAME', DEFAULT_EXCHANGE_NAME)
        self.application_id = app.config.get('APPLICATION_ID', DEFAULT_APPLICATION_ID)
        self.delivery_mode = app.config.get('DELIVERY_MODE', DEFAULT_DELIVERY_MODE)
        self.queues = queues
        self.on_message_callback = on_message_callback

        # Open Connection to RabbitMQ
        self.connection_handler = ConnectionHandler(self.url)
        connection = self.connection_handler.get_current_connection()

        # Setup default producer for rabbit
        self.producer = Producer(
            connection, self.exchange_name, self.exchange_type,
            self.application_id, self.delivery_mode)
        self.producer.init_env_rabbit(self.queues)

    def send(self, queue, context={}):
        """Post the message to the correct queue with the given context

        :param str queue: queue which to post the message
        :param dict context: content of the message to post to RabbitMQ server
        """
        if queue not in self.queues:
            message = 'Queue ‘{name}‘ is not registered'.format(name=queue)
            raise UnknownQueueError(message)

        message = {
            'created_at': datetime.utcnow().isoformat(),
            'status': STATUS_READY,
            'queue': queue,
            'context': context
        }

        return self.producer.publish(queue, message)
