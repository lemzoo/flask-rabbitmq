import pika


class ConnectionHandler:
    """This is a  Connection Handler to manage the connection between the
    client and RabbitMQ.

    """

    def __init__(self, rabbit_url):
        """Create a new instance of Connection Handler by using the given
        parameters to connect to RabbitMQ which is on environment variable
        """
        self._connection = None
        self.parameters = None
        self.init_connection(rabbit_url)

    def init_connection(self, rabbit_url, timeout=5):
        """Setup the publisher object, passing in the host, port, user id and
        the password to create a parameters objects to connect to RabbitMQ.

        :param app: Current application context
        :param integer timeout: Timeout for handling the conection.
        By default, it's 0.25 seconds. It's not recommended to keep 0.25
        """

        self.parameters = pika.URLParameters(rabbit_url)
        self.parameters.heartbeat = 0
        self.parameters.socket_timeout = timeout
        self._connection = pika.BlockingConnection(self.parameters)

    def close_connection(self):
        self._connection.close()

    def get_current_connection(self):
        return self._connection
