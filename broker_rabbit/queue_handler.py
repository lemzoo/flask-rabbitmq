from broker_rabbit.exceptions import (ChannelNotDefinedError,
                                      ExchangeNotDefinedYet)


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

    def setup_queue(self, name):
        """Setting the queue to allow pushong in a specied exchange

        :param str name : The name of the queue to set in RabbitMQ.
        """
        # Check if the channel is set or not
        self._check_basic_config()

        # Create the queue
        self.create_queue(name)

        # Bind the queue to the exchange
        self._channel.queue_bind(queue=name, exchange=self._exchange)

    def _check_basic_config(self):
        if self._channel is None:
            raise ChannelNotDefinedError('The Channel is not defined yet')

        if self._exchange is None:
            raise ExchangeNotDefinedYet('The exchange is not defined')

    def create_queue(self, queue_name, durable=True, auto_delete=False):
        """Create a new queue with the arguments such as its name.

        :param str queue_name : The name of the queue to set in RabbitMQ.
        :param boolean durable : The durability of the queue in RabbitMQ.
        :param boolean auto_delete : Auto delete the queue when  the message
        are purged (No consumer/publisher working on this particular queue)
        """

        # TODO : Check declared_queue to return the real name of the queue
        self._channel.queue_declare(queue=queue_name, durable=durable,
                                    auto_delete=auto_delete,
                                    arguments={'x-ha-policy': 'all'})
