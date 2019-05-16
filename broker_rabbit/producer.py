from broker_rabbit.exceptions import QueueDoesNotExistError
from broker_rabbit.exchange_handler import ExchangeHandler
from broker_rabbit.queue_handler import QueueHandler


class Producer:
    """Producer component that will publish message and handle
    connection and channel interactions with RabbitMQ.

    """

    def __init__(self, channel, exchange_name, queues=None):
        self._channel = channel
        self._exchange_name = exchange_name

        if queues:
            self.bootstrap(queues)

    def bootstrap(self, queues):
        """Initialize the queue on RabbitMQ

        :param list queues: List of queue to setup on broker_rabbit
        """
        self._channel.open()
        try:
            channel = self._channel.get_channel()

            exchange_handler = ExchangeHandler(channel, self._exchange_name)
            exchange_handler.setup_exchange()

            queue_handler = QueueHandler(channel, self._exchange_name)
            for queue in queues:
                queue_handler.setup_queue(queue)
        finally:
            self._queues = queues
            self._channel.close()

    def publish(self, queue, message):
        """Publish the given message in the given queue

        :param str queue : The queue name which to publish the given message
        :param dict message : The message to publish in RabbitMQ
        """

        if queue not in self._queues:
            error_msg = f'Queue with name `{queue}` is not declared.' \
                f'Please call bootstrap before using publish'
            raise QueueDoesNotExistError(error_msg)

        self._channel.open()
        try:
            self._channel.send_message(self._exchange_name, queue, message)
        finally:
            self._channel.close()
