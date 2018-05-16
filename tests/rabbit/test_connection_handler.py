import pytest
from pika import BlockingConnection
from pika.exceptions import ConnectionClosed, ProbableAuthenticationError

from tests.base_test import RabbitBrokerTest
from broker_rabbit.connection_handler import ConnectionHandler
from tests import common


class TestConnectionHandler(RabbitBrokerTest):
    def test_initialize_new_connection(self):
        # When
        connection_handler = ConnectionHandler(common.get_rabbit_url())

        # Then
        connection = connection_handler.get_current_connection()
        assert connection.is_open
        assert isinstance(connection, BlockingConnection)

    def test_raise_when_trying_to_open_connection_with_bad_port(self):
        # Given
        rabbit_url = "amqp://guest:guest@localhost:8225/%2F"

        # When and Then is expecting an exception to be raised
        with pytest.raises(ConnectionClosed):
            ConnectionHandler(rabbit_url)

    def test_raises_when_trying_to_open_connection_with_bad_credentials(self):
        # Given
        rabbit_url = "amqp://vip:vip@localhost:5672/%2F"

        # When and Then is expecting an exception to be raised
        with pytest.raises(ProbableAuthenticationError):
            ConnectionHandler(rabbit_url)

    def test_open_connection_successfully(self):
        # When
        connection_handler = ConnectionHandler(common.get_rabbit_url())

        # Then
        connection = connection_handler.get_current_connection()
        assert connection.is_open is True

    def test_close_connection_successfully(self):
        # Given
        connection_handler = ConnectionHandler(common.get_rabbit_url())

        # When
        connection_handler.close_connection()

        # Then
        connection = connection_handler.get_current_connection()
        assert connection.is_closed is True
        assert connection.is_open is False
