import json
from unittest.mock import Mock

import pytest
from pika.connection import Connection
from pika.spec import Basic

from tests.base_test import RabbitBrokerTest
from broker.broker_rabbit.exceptions import (ConnectionNotOpenedYet,
                                             WorkerExitException,
                                             ConnectionIsClosed)
from broker.broker_rabbit.rabbit.channels import ChannelHandler, WorkerChannel, ProducerChannel
from broker.broker_rabbit.rabbit.connection_handler import ConnectionHandler
from tests import common


@pytest.mark.functional_test
class TestChannelHandler(RabbitBrokerTest):
    def setup_method(self):
        self.connection = ConnectionHandler(common.get_rabbit_url())
        self.channel_handler = ChannelHandler(self.connection.get_current_connection())

    def test_if_channel_is_open(self):
        self.channel_handler.open()
        assert self.connection._connection.is_open
        self.channel_handler.close()

    def test_if_channel_is_open_failed(self):
        with pytest.raises(ConnectionNotOpenedYet):
            channel_handler = ChannelHandler(None)
            channel_handler.open()

    def test_if_connection_is_closed(self):
        with pytest.raises(ConnectionIsClosed):
            self.channel_handler._connection.close()
            assert self.connection._connection.is_closed
            self.channel_handler.open()


@pytest.mark.unit_test
class TestWorkerChannel:
    def setup_method(self):
        connection = Mock(Connection)
        connection.is_closed = False
        self.worker_channel = WorkerChannel(connection, None, None, None)
        self.worker_channel.open()

    def teardown_method(self):
        self.worker_channel.close()

    def test_raising_error_on_keyboard_interrupt(self):
        self.worker_channel._channel.start_consuming.side_effect = \
            KeyboardInterrupt('Testing Keyboard Exception')
        with pytest.raises(WorkerExitException):
            self.worker_channel.run()

    def test_execute_rabbit_is_not_called_when_exception_raised(self):
        empty_body_as_bytes = b'{}'
        self.worker_channel.event_handler = Mock()
        # When
        self.worker_channel.on_message(None, Basic.GetOk(), None, empty_body_as_bytes)
        # Then
        assert not self.worker_channel.event_handler.execute_rabbit.called


@pytest.mark.unit_test
class TestProducerChannel:
    def setup_method(self):
        connection = Mock(Connection)
        connection.is_closed = False
        self.producer_channel = ProducerChannel(connection)
        self.producer_channel.open()

    def teardown_method(self):
        self.producer_channel.close()

    def test_send_message(self):
        exchange = 'TEST_EXCHANGE'
        queue = 'TEST_QUEUE'
        message = 'TEST_MESSAGE'
        properties = 'TEST_PROPERTIES'

        self.producer_channel._basic_properties = properties
        body = json.dumps(message)

        self.producer_channel.send_message(exchange, queue, message)

        self.producer_channel._channel.basic_publish.assert_called_with(
            exchange=exchange, routing_key=queue, body=body, properties=properties)
