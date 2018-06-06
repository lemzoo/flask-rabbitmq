import json
from unittest.mock import Mock

import pytest
from pika.connection import Connection
from pika.spec import Basic

from broker_rabbit.exceptions import (
    ConnectionNotOpenedYet, ConnectionIsClosed,
    WorkerExitException, ChannelNotDefinedError)

from broker_rabbit.channels import (
    ChannelHandler, WorkerChannel, ProducerChannel)

from broker_rabbit.connection_handler import ConnectionHandler

from tests import common
from tests.base_test import RabbitBrokerTest


# TODO: Test the new added method
@pytest.mark.functional_test
class TestChannelHandler(RabbitBrokerTest):
    def setup_method(self):
        self.connection = ConnectionHandler(common.BROKER_URL_TEST)
        current_connection = self.connection.get_current_connection()
        self.channel_handler = ChannelHandler(current_connection)

    def test_should_raise_when_connection_is_not_defined(self):
        # Given
        connection = None
        channel_handler = ChannelHandler(connection)

        # When
        with pytest.raises(ConnectionNotOpenedYet) as error:
            channel_handler.open()

        # Then
        assert 'The connection is not opened' == error.value.args[0]

    def test_should_raise_when_connection_is_closed(self):
        # Given
        self.connection.close_connection()

        # When
        with pytest.raises(ConnectionIsClosed) as error:
            self.channel_handler.open()

        # Then
        assert 'The connection is closed' == error.value.args[0]

    def test_should_open_channel(self):
        # When
        self.channel_handler.open()

        # Then
        assert self.channel_handler.get_channel().is_open is True

    def test_should_close_channel(self):
        # Given
        self.channel_handler.open()

        # When
        self.channel_handler.close()

        # Then
        assert self.channel_handler.get_channel().is_closed is True

    def test_should_close_channel(self):
        # Given
        self.channel_handler.open()

        # When
        self.channel_handler.close()

        # Then
        assert self.channel_handler.get_channel().is_closed is True

    def test_should_raise_when_channel_is_not_defined(self):
        # Given
        self.channel_handler._channel = None

        # When
        with pytest.raises(ChannelNotDefinedError) as error:
            self.channel_handler.get_channel()

        # Then
        assert 'The channel does not exist yet' == error.value.args[0]


@pytest.mark.unit_test
class TestWorkerChannel:
    def setup_method(self):
        connection = Mock(Connection)
        connection.is_closed = False
        self.worker = WorkerChannel(connection, None, None)
        self.worker.open()

    def teardown_method(self):
        self.worker.close()

    def test_raising_error_on_keyboard_interrupt(self):
        # Given
        self.worker._channel.start_consuming.side_effect = KeyboardInterrupt()

        # When
        with pytest.raises(WorkerExitException) as error:
            self.worker.run()

        # Then
        assert 'Worker stopped pulling message' == error.value.args[0]

    def test_execute_rabbit_is_not_called_when_exception_raised(self):
        empty_body_as_bytes = b'{}'
        self.worker.event_handler = Mock()
        # When
        self.worker.on_message(None, Basic.GetOk(), None, empty_body_as_bytes)
        # Then
        assert not self.worker.event_handler.execute_rabbit.called


@pytest.mark.unit_test
class TestProducerChannel:
    def setup_method(self):
        connection = Mock(Connection)
        connection.is_closed = False
        self.channel = ProducerChannel(connection, delivery_mode=2,
                                       application_id='TEST-APP_ID')
        self.channel.open()
        self.exchange = 'TEST-EXCHANGE'
        self.queue = 'TEST-QUEUE'

    def teardown_method(self):
        self.channel.close()

    def test_send_message(self):
        # Given
        message = {'key': 'value', 'number': 1, 'foo': 'bar'}
        self.channel.basic_properties = 'TEST-PROPERTIES'

        # When
        self.channel.send_message(self.exchange, self.queue, message)

        # Then
        body = json.dumps(message)
        channel = self.channel.get_channel()
        channel.basic_publish.assert_called_with(
            exchange=self.exchange, routing_key=self.queue,
            body=body, properties='TEST-PROPERTIES')

    def test_returns_correct_for_properties(self):
        # Given
        application_id = 'TEST-APPLICATION-ID'
        delivery_mode = 2

        # When
        properties = self.channel.apply_basic_properties(application_id,
                                                         delivery_mode)

        # Then
        assert 'TEST-APPLICATION-ID' == properties.app_id
        assert 2 == properties.delivery_mode
