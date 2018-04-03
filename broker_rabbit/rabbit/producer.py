from broker_rabbit.rabbit.channels import ProducerChannel
from broker_rabbit.rabbit.exchange_handler import ExchangeHandler
from broker_rabbit.rabbit.queue_handler import QueueHandler


class Producer:
    """Producer component that will publish message and handle
    connection and channel interactions with RabbitMQ.

    """

    def __init__(self, connection, exchange_name, app_id, app=None, **kwargs):
        self._exchange_name = exchange_name
        self._producer_channel = ProducerChannel(connection, app_id)

    def init_env_rabbit(self, queues):
        """Initialize the queue on RabbitMQ

        :param list queues: List of queue to setup on rabbit
        """
        self._producer_channel.open()
        try:
            channel = self._producer_channel.get_channel()

            exchange_handler = ExchangeHandler(channel, self._exchange_name)
            exchange_handler.setup_exchange()

            queue_handler = QueueHandler(channel, self._exchange_name)
            queue_handler.setup_queues(queues)
        finally:
            self._producer_channel.close()

    def publish(self, queue, message):
        """Publish the given message in the given queue

        :param str queue : The queue name which to publish the given message
        :param dict message : The message to publish in RabbitMQ
        """
        self._producer_channel.open()
        try:
            self._producer_channel.send_message(self._exchange_name,
                                                queue, message)
        finally:
            self._producer_channel.close()
