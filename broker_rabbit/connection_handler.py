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

    def init_connection(self, url, timeout=5):
        # TODO: add ssl certification
        """Setup the publisher object, passing in the host, port, user id and
        the password to create a parameters objects to connect to RabbitMQ.

        :param str url: url for RabbitMQ server
        :param int timeout: Timeout for handling the connection.
            By default, it's 0.25 seconds.
            It's not recommended to keep it to 0.25. So, we change it to 5.
        """

        self.parameters = pika.URLParameters(url)
        self.parameters.heartbeat = 0
        self.parameters.socket_timeout = timeout
        self._connection = pika.BlockingConnection(self.parameters)

    def close_connection(self):
        self._connection.close()

    def get_current_connection(self):
        return self._connection
