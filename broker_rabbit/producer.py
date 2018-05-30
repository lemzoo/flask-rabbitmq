from broker_rabbit.exceptions import QueueDoesNotExist
from broker_rabbit.channels import ProducerChannel
from broker_rabbit.exchange_handler import ExchangeHandler
from broker_rabbit.queue_handler import QueueHandler


class Producer:
    """Producer component that will publish message and handle
    connection and channel interactions with RabbitMQ.

    """

    def __init__(self, connection, exchange_name,
                 application_id, delivery_mode):
        self._exchange_name = exchange_name
        self._producer_channel = ProducerChannel(
            connection, application_id, delivery_mode)
        self._queues = None

    def bootstrap(self, queues):
        """Initialize the queue on RabbitMQ

        :param list queues: List of queue to setup on broker_rabbit
        """
        self._producer_channel.open()
        try:
            channel = self._producer_channel.get_channel()

            exchange_handler = ExchangeHandler(channel, self._exchange_name)
            exchange_handler.setup_exchange()

            queue_handler = QueueHandler(channel, self._exchange_name)
            for queue in queues:
                queue_handler.setup_queue(queue)
        finally:
            self._queues = queues
            self._producer_channel.close()

    def publish(self, queue, message):
        """Publish the given message in the given queue

        :param str queue : The queue name which to publish the given message
        :param dict message : The message to publish in RabbitMQ
        """

        if queue not in self._queues:
            raise QueueDoesNotExist(
                'This queue ’{queue}’ is not declared. Please call '
                'init_env_rabbit before using publish'.format(queue=queue))

        self._producer_channel.open()
        try:
            self._producer_channel.send_message(self._exchange_name,
                                                queue, message)
        finally:
            self._producer_channel.close()
