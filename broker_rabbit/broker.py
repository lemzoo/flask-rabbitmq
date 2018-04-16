from datetime import datetime

from broker_rabbit.exceptions import UnknownQueueError

from broker_rabbit.connection_handler import ConnectionHandler
from broker_rabbit import Producer

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
        self.producer = None
        self.url = None
        self.exchange = None
        self.app_id = None
        self.delivery = None

        if self.app is not None:
            self.init_app(self.app, self.queues)

    def init_app(self, app, queues):
        """ Init the Broker by using the given configuration instead
        default settings.

        :param app: Current application context
        :param list queues: Queues which the message will be post
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
        self.exchange = app.config.get('EXCHANGE_NAME', DEFAULT_EXCHANGE_NAME)
        self.app_id = app.config.get('APPLICATION_ID', DEFAULT_APPLICATION_ID)
        self.delivery = app.config.get('DELIVERY_MODE', DEFAULT_DELIVERY_MODE)
        self.queues = queues

        # Open Connection to RabbitMQ
        connection_handler = ConnectionHandler(self.url)
        connection = connection_handler.get_current_connection()

        # Setup default producer for rabbit
        self.producer = Producer(connection, self.exchange,
                                 self.app_id, self.delivery)
        self.producer.init_env_rabbit(self.queues)

    def send(self, queue, context={}):
        """Post the message to the correct queue with the given context

        :param str queue: queue which to post the message
        :param dict context: content of the message to post to RabbitMQ server
        """
        if queue not in self.queues:
            message = 'Queue ‘{queue}‘ is not registered'.format(queue=queue)
            raise UnknownQueueError(message)

        message = {
            'created': datetime.utcnow().isoformat(),
            'status': STATUS_READY,
            'queue': queue,
            'context': context
        }

        return self.producer.publish(queue, message)
