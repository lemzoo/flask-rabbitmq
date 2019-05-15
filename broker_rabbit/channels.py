import logging
import json

import pika
from pika.utils import is_callable

from broker_rabbit.exceptions import (
    ConnectionNotOpenedError, ChannelNotDefinedError,
    WorkerExitError, ConnectionIsClosedError, CallBackError)

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class ChannelHandler:
    """This is a  Channel Handler which use the connection handler to get a new
    channel to allow the client to communicate with RabbitMQ.

    """

    def __init__(self, connection):
        """Create a new instance of the channel class by using the current
        connection.

        :param ConnectionHandler connection: The given connection to allow
        communication with RabbitMQ.

        """
        self._connection = connection
        self._channel = None

    def open(self):
        LOGGER.info('Opening channel for the producer')
        if self._connection is None:
            LOGGER.error('The connection is not opened')
            raise ConnectionNotOpenedError('The connection is not opened')

        if self._connection.is_closed:
            LOGGER.error('The connection is closed')
            raise ConnectionIsClosedError('The connection is closed')

        self._channel = self._connection.channel()

    def close(self):
        LOGGER.info('The channel will close in a few time')
        self._channel.close()

    def get_channel(self):
        LOGGER.info('Getting the channel object')
        if self._channel is None:
            LOGGER.error('The channel doesn''t exist yet')
            raise ChannelNotDefinedError('The channel does not exist yet')

        return self._channel


class WorkerChannel(ChannelHandler):

    def __init__(self, connection, queue, on_message_callback):
        super().__init__(connection)
        self._queue = queue
        self._on_message_callback = on_message_callback

    def run(self):
        LOGGER.info('Consuming message on queue : %s', self._queue)

        try:
            """The queue can be non exist on broker_rabbit, so ChannelClosed exception
            is handled by RabbitMQ and then the TCP connection is closed.
            Re-implement this if others worker can be launch and handle the
            Exception.
            """
            self.open()
            self.add_on_cancel_callback()
            self._channel.basic_consume(self.on_message, self._queue)
            LOGGER.info(' [*] Waiting for messages. To exit press CTRL+C')
            self._channel.start_consuming()
        except KeyboardInterrupt:
            LOGGER.info('The Worker will be exit after CTRL+C signal')
            raise WorkerExitError('Worker stopped pulling message')
        finally:
            self.close()

    def consume_one_message(self):
        method, header, body = self._channel.basic_get(self._queue)
        if not method or method.NAME == 'Basic.GetEmpty':
            return False
        else:
            self.on_message(self._channel, method, header, body)
            return True

    def bind_callback(self, message):
        if not is_callable(self._on_message_callback):
            LOGGER.info('Wrong callback is binded')
            raise CallBackError('The callback is not callable')

        try:
            self._on_message_callback(message)
            LOGGER.info('Received message # %s #', message)
        except TypeError as error:
            LOGGER.info('Error on the callback definition. Message is not '
                        'acknowledge. And it will be keep on the RabbitMQ')
            error_message = 'You should implement your callback ' \
                            'like my_callback(content)'
            raise CallBackError(error_message, original_exception=str(error))

    def on_message(self, channel, method, properties, body):
        try:
            # TODO: Handle here a dead letter queue after deciding
            # TODO: the next step of the received message
            decoded_message = body.decode()
            raw_message = json.loads(decoded_message)
            self.bind_callback(raw_message)
        except Exception as exception_info:
            # TODO: handle dead letter
            LOGGER.error(
                'Exception {exception} occurred when trying to decode the data'
                'received RabbitMQ. So the message content will be put on '
                'queue dead letter. Here are the content of the message : '
                '{content}'.format(exception=exception_info, content=body))

        self.acknowledge_message(method.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def add_on_cancel_callback(self):
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self.close()


class ProducerChannel(ChannelHandler):

    def __init__(self, connection, application_id, delivery_mode):
        super().__init__(connection)
        self.basic_properties = self.apply_basic_properties(application_id,
                                                            delivery_mode)

    def send_message(self, exchange, queue, message):
        serialized_message = json.dumps(message)

        self._channel.basic_publish(
            exchange=exchange, routing_key=queue,
            body=serialized_message, properties=self.basic_properties)
        LOGGER.info('message was published successfully into RabbitMQ')

    @staticmethod
    def apply_basic_properties(app_id, delivery_mode,
                               content_type='application/json'):
        """Apply the basic properties for RabbitMQ.

        :param str app_id : The id of the current app.
        :param int delivery_mode : The delivering mode for RabbitMQ.
                `2` means the message will be persisted on the disk
                `1` means the message will not be persisted.
        :param str content_type : The content type of the message
        """
        LOGGER.info('Applying the properties for RabbitMQ')
        properties = pika.BasicProperties(app_id=app_id,
                                          content_type=content_type,
                                          delivery_mode=delivery_mode)
        return properties
