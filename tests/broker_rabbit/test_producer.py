from unittest.mock import Mock, patch, call

import pytest

from broker_rabbit.channels import ProducerChannel
from broker_rabbit.connection_handler import ConnectionHandler
from broker_rabbit.exceptions import QueueDoesNotExist, ConnectionNotOpenedYet, \
    ConnectionIsClosed
from broker_rabbit.producer import Producer
from tests import common



class TestBase:
    def setup(self):
        connection = ConnectionHandler(common.BROKER_URL_TEST)
        current_connection = connection.get_current_connection()
        self.exchange_name = 'TEST-EXCHANGE-NAME'
        self.application_id = 'TEST-APPLICATION-ID'
        self.delivery_mode = 2
        channel_handler = ProducerChannel(
            current_connection, self.application_id, self.delivery_mode)
        channel_handler.open()
        self.channel = channel_handler.get_channel()
        self.channel = Mock(ProducerChannel)


@pytest.mark.unit_test
class TestProducer(TestBase):
    def setup(self):
        super().setup()
        self.queues = ['first-queue', 'second-queue']
        self.producer = Producer(self.channel, self.exchange_name, self.queues)

    def test_should_raise_when_queue_to_publish_does_not_exist(self):
        # Given
        unknown_queue = 'UNKNOWN'
        message = "TEST-MESSAGE-CONTENT"

        # When
        with pytest.raises(QueueDoesNotExist) as error:
            self.producer.publish(unknown_queue, message)

        # Then
        error_message = 'This queue ’UNKNOWN’ is not declared. Please call ' \
                        'bootstrap before using publish'

        assert error_message == error.value.args[0]

    def test_should_open_channel_before_sending_message(self):
        # Given
        first_queue = self.queues[0]
        message = "TEST-MESSAGE"

        # When
        self.producer.publish(first_queue, message)

        # Then
        method_calls = self.channel.method_calls
        assert call.open() == method_calls[3]
        call_send_message = call.send_message(
            self.exchange_name, first_queue, message)
        assert call_send_message == method_calls[4]

    def test_should_publish_on_given_queue(self):
        # Given
        first_queue = self.queues[0]
        message = "TEST-MESSAGE"

        # When
        self.producer.publish(first_queue, message)

        # Then
        self.channel.send_message.assert_called_with(
            self.exchange_name, first_queue, message)

    def test_should_close_used_channel_after_publishing_message(self):
        # Given
        first_queue = self.queues[0]
        message = "TEST-MESSAGE"

        # When
        self.producer.publish(first_queue, message)

        # Then
        assert self.channel.close.called is True


@patch('broker_rabbit.producer.QueueHandler')
@patch('broker_rabbit.producer.ExchangeHandler')
class TestProducerBootstrap(TestBase):

    def setup(self):
        super().setup()
        self.producer = Producer(self.channel, self.exchange_name)
        self.queues = ['queue-1', 'queue-2', 'queue-3', 'queue-4']

    def test_should_setup_exchange(self, exchange_mock, queue_mock):
        # When
        self.producer.bootstrap(self.queues)

        # Then
        channel = self.channel.get_channel()
        exchange_mock.assert_called_once_with(channel, self.exchange_name)
        exchange_mock().setup_exchange.assert_called_once()

    def test_should_setup_queue(self, exchange_mock, queue_mock):
        # When
        self.producer.bootstrap(self.queues)

        # Then
        channel = self.channel.get_channel()
        queue_mock.assert_called_once_with(channel, self.exchange_name)
        assert 4 == queue_mock().setup_queue.call_count

    def test_should_close_channel_at_the_end(self, exchange_mock, queue_mock):
        # When
        self.producer.bootstrap(self.queues)

        # Then
        channel = self.channel.get_channel()
        channel.close.assert_called_once()

    def test_should_close_channel_at_the_end_while_error_occurred(
            self, exchange_mock, queue_mock):
        # Given
        channel = self.channel.get_channel()
        channel.open.side_effect = ConnectionNotOpenedYet(
            'connection not opened')

        # When
        self.producer.bootstrap(self.queues)

        # Then
        channel.close.assert_called_once()
