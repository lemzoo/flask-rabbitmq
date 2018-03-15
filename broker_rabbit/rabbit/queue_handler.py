from broker_rabbit.exceptions import (
    ChannelDoesntExist, QueueNameDoesntMatch, ExchangeNotDefinedYet)


class QueueHandler:
    """This is an Exchange Handler which use the channel handler to set a new
    or default exchange in RabbitMQ.

    """

    def __init__(self, channel, exchange_name):
        """Create a new instance of exchange handler class by using the channel

        :param ChannelHandler channel: The given channel to connect to RabbitMQ
        :param str exchange_name : The name of the exchange to set
        """
        self._channel = channel
        self._exchange = exchange_name

    def _check_basic_config(self):
        if self._channel is None:
            raise ChannelDoesntExist('Channel is not defined yet')

        if self._exchange is None:
            raise ExchangeNotDefinedYet('The exchange is not defined')

        return

    def setup_queue(self, queue_name):
        """Setting the queue to allow pushong in a specied exchange

        :param str queue_name : The name of the queue to set in RabbitMQ.
        """
        # Check if the channel is set or not
        self._check_basic_config()

        # Create the queue
        declared_queue = self.create_queue(queue_name)

        # Bind the queue to the exchange
        self.bind_queue_to_default_exchange(declared_queue)

    def setup_queues(self, queues):
        for queue_name in queues:
            self.setup_queue(queue_name)

    def create_queue(self, queue_name, durable=True, auto_delete=False):
        """Create a new queue with the arguments such as its name.

        :param str queue_name : The name of the queue to set in RabbitMQ.
        :param boolean durable : The durability of the queue in RabbitMQ.
        :param boolean auto_delete : Auto delete the queue when  the message
        are purged (No consumer/publisher working on this particular queue)
        """

        if len(queue_name) < 3:
            raise QueueNameDoesntMatch("This queue name doesn't match")

        # TODO : Check declared_queue to return the real name of the queue
        self._channel.queue_declare(queue=queue_name, durable=durable, auto_delete=auto_delete)
        return queue_name

    def bind_queue_to_default_exchange(self, queue_name):
        self._check_basic_config()
        self._channel.queue_bind(queue=queue_name, exchange=self._exchange)
