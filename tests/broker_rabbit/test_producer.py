from unittest.mock import Mock, patch, call

import pytest

from broker_rabbit.channels import ProducerChannel
from broker_rabbit.connection_handler import ConnectionHandler
from broker_rabbit.exceptions import (QueueDoesNotExistError,
                                      ConnectionNotOpenedError)
from broker_rabbit.producer import Producer

from tests import common


class TestBase:
    def setup(self):
        connection = ConnectionHandler(common.BROKER_URL_TEST)
        current_connection = connection.get_current_connection()
        self.exchange_name = 'TEST-EXCHANGE-NAME'
        self.application_id = 'TEST-APPLICATION-ID'
        self.delivery_mode = 2
        channel_handler = ProducerChannel(current_connection,
                                          self.application_id,
                                          self.delivery_mode)
        channel_handler.open()
        self.channel = channel_handler.get_channel()
        self.channel = Mock(ProducerChannel)
        self.message = {"content": "TEST-CONTENT-MESSAGE"}


@pytest.mark.unit_test
class TestProducer(TestBase):
    def setup(self):
        super().setup()
        self.queues = ['first-queue', 'second-queue']
        self.producer = Producer(self.channel, self.exchange_name, self.queues)
        self.first_queue = self.queues[0]

    def test_should_raise_when_queue_to_publish_does_not_exist(self):
        # Given
        unknown_queue = 'UNKNOWN'

        # When
        with pytest.raises(QueueDoesNotExistError) as error:
            self.producer.publish(unknown_queue, self.message)

        # Then
        error_message = 'Queue with name `UNKNOWN` is not declared.' \
                        'Please call bootstrap before using publish'

        assert error_message == error.value.args[0][0]

    def test_should_open_channel_before_sending_message(self):
        # When
        self.producer.publish(self.first_queue, self.message)

        # Then
        method_calls = self.channel.method_calls
        assert call.open() == method_calls[3]
        call_send_message = call.send_message(
            self.exchange_name, self.first_queue, self.message)
        assert call_send_message == method_calls[4]

    def test_should_publish_on_given_queue(self):
        # When
        self.producer.publish(self.first_queue, self.message)

        # Then
        self.channel.send_message.assert_called_with(
            self.exchange_name, self.first_queue, self.message)

    def test_should_close_used_channel_after_publishing_message(self):
        # When
        self.producer.publish(self.first_queue, self.message)

        # Then
        assert self.channel.close.called is True


class TestProducerBootstrap(TestBase):

    def setup(self):
        super().setup()
        self.producer = Producer(self.channel, self.exchange_name)
        self.queues = ['queue-1', 'queue-2', 'queue-3', 'queue-4']

        queue_handler = patch('broker_rabbit.producer.QueueHandler')
        self.queue_handler = queue_handler.start()

        exchange_handler = patch('broker_rabbit.producer.ExchangeHandler')
        self.exchange_handler = exchange_handler.start()

    def test_should_setup_exchange(self):
        # When
        self.producer.bootstrap(self.queues)

        # Then
        channel = self.channel.get_channel()
        self.exchange_handler.assert_called_once_with(channel,
                                                      self.exchange_name)
        self.exchange_handler().setup_exchange.assert_called_once()

    def test_should_setup_queue(self):
        # When
        self.producer.bootstrap(self.queues)

        # Then
        channel = self.channel.get_channel()
        self.queue_handler.assert_called_once_with(channel, self.exchange_name)
        assert 4 == self.queue_handler().setup_queue.call_count

    def test_should_close_channel_at_the_end(self):
        # When
        self.producer.bootstrap(self.queues)

        # Then
        self.channel.close.assert_called_once()

    def test_should_close_channel_at_the_end_while_error_occurred(self):
        # Given
        channel = self.channel.get_channel()
        error_msg = 'connection not opened'
        channel.open.side_effect = ConnectionNotOpenedError(error_msg)

        # When
        self.producer.bootstrap(self.queues)

        # Then
        self.channel.close.assert_called_once()
