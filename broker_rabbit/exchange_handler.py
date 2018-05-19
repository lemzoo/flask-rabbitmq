from broker_rabbit.exceptions import ChannelNotDefinedError, ExchangeNotDefinedYet


class ExchangeHandler:
    """This is an Exchange Handler which used by the channel handler to
    set a new or default exchange in RabbitMQ.

    """

    def __init__(self, channel, name):
        """Create a new instance of exchange handler class by using the channel

        :param ChannelHandler channel: The given channel to connect to RabbitMQ
        :param str name : The name of the exchange to set
        """
        self._channel = channel
        self._name = name

    def setup_exchange(self, exchange_type='direct',
                       durable=True, auto_delete=False):
        """
        :param str exchange_type : The type of exchange.
            By default, the exchange is set to direct type to allow simple
            routing via the queue name.
            Here are the type of exchange : direct - fanout - topic.
        :param boolean durable : The durability of the exchange.
            Durable exchange remain active when a server restarts.
            Non-durable exchanges (transient exchanges) are purged when the
            server restarts. This is not recommended.
        :param boolean auto_delete : Delete the exchange when all queues have
        finished using it. By default, it's False.
        """
        if self._channel is None:
            raise ChannelNotDefinedError('The channel was not defined')

        # Check Me : self._channel.basic_qos(prefetch_count=1)
        self._channel.exchange_declare(
            exchange=self._name, type=exchange_type,
            durable=durable, auto_delete=auto_delete)

    @property
    def name(self):
        if self._name is None:
            raise ExchangeNotDefinedYet('The exchange is not defined')

        return self._name
