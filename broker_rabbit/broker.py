from datetime import datetime


from broker_rabbit.channels import ProducerChannel
from broker_rabbit.exceptions import UnknownQueueError

from broker_rabbit.connection_handler import ConnectionHandler
from broker_rabbit.producer import Producer
from broker_rabbit.worker import Worker

DEFAULT_URL = 'amqp://test:test@localhost:5672/foo-test'
DEFAULT_EXCHANGE = 'FOO-EXCHANGE'
DEFAULT_APP = 'FOO-APPLICATION-ID'
DEFAULT_DELIVERY = 2
STATUS_READY = 'READY'


class BrokerRabbitMQ:
    """Message Broker based on RabbitMQ middleware"""

    def __init__(self, app=None):
        """
        Create a new instance of Broker Rabbit by using
        the given parameters to connect to RabbitMQ.
        """
        self.app = app
        self.connection_handler = None
        self.producer = None
        self.url = None
        self.exchange_name = None
        self.application_id = None
        self.delivery_mode = None
        self.queues = None
        self.on_message_callback = None

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
        self.exchange_name = app.config.get('EXCHANGE_NAME', DEFAULT_EXCHANGE)
        self.application_id = app.config.get('APPLICATION_ID', DEFAULT_APP)
        self.delivery_mode = app.config.get('DELIVERY_MODE', DEFAULT_DELIVERY)
        self.queues = queues
        self.on_message_callback = on_message_callback

        # Open Connection to RabbitMQ
        self.connection_handler = ConnectionHandler(self.url)
        connection = self.connection_handler.get_current_connection()

        # Setup default producer for broker_rabbit
        channel = ProducerChannel(connection, self.application_id,
                                  self.delivery_mode)
        self.producer = Producer(channel, self.exchange_name)
        self.producer.bootstrap(self.queues)

    def send(self, queue, context={}):
        """Post the message to the correct queue with the given context

        :param str queue: queue which to post the message
        :param dict context: content of the message to post to RabbitMQ server
        """
        if queue not in self.queues:
            error_msg = f'Queue ‘{queue}‘ is not registered'
            raise UnknownQueueError(error_msg)

        message = {
            'created_at': datetime.utcnow().isoformat(),
            'queue': queue,
            'context': context
        }

        return self.producer.publish(queue, message)

    def list_queues(self):
        """List all available queue in the app"""
        for queue in self.queues:
            print('Queue name : `%s`' % queue)

    def start(self, queue):
        """Start worker on a given queue
        :param queue: the queue which you consume message for
        """
        if queue not in self.queues:
            raise RuntimeError(f'Queue with name`{queue}` not found')

        worker = Worker(connection_handler=self.connection_handler,
                        message_callback=self.on_message_callback, queue=queue)
        print(f'Start consuming message on the queue `{queue}')
        worker.consume_message()