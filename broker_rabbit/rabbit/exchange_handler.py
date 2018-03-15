from broker_rabbit.exceptions import (
    ExchangeNameDoesntMatch, ChannelDoesntExist, ExchangeNotDefinedYet)


class ExchangeHandler:
    """This is an Exchange Handler which used by the channel handler to
    set a new or default exchange in RabbitMQ.

    """

    def __init__(self, channel, exchange_name, exchange_type='direct',
                 durable=True, auto_delete=False):
        """Create a new instance of exchange handler class by using the channel

        :param ChannelHandler channel: The given channel to connect to RabbitMQ
        :param str exchange_name : The name of the exchange to set
        :param str : exchange_type : The type of exchange.
            By default, the exchange is direct type to allow simple routing
            via the queue name.
            Here are the type of exchange : direct - fanout - topic.
        :param boolean durable : The durability of the exchange.
            Durable exchange remain active when a server restarts.
            Non-durable exchanges (transient exchanges) are purged when the
            server restarts. This is not recommended.
        :param boolean auto_delete : Delete the exchange when all queues have
        finished using it. By default, it's False.
        """
        self._channel = channel
        self._exchange = exchange_name
        self._type = exchange_type
        self._durable = durable
        self._auto_delete = auto_delete

    def setup_exchange(self):
        if self._channel is None:
            raise ChannelDoesntExist("The channel doesn't exist")

        # Avoid to set an exchange name less than 3 chars. It's a bas practice.
        if len(self._exchange) < 3:
            raise ExchangeNameDoesntMatch("This exchange name doesn't match")

        # Check Me : self._channel.basic_qos(prefetch_count=1)
        self._channel.exchange_declare(exchange=self._exchange, type=self._type,
                                       durable=self._durable, auto_delete=self._auto_delete)

    def get_exchange_name(self):
        if self._exchange is None:
            raise ExchangeNotDefinedYet("The exchange is not defined")
        return self._exchange
