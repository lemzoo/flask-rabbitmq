from unittest.mock import Mock

import pytest
from pika import BlockingConnection

from broker_rabbit.exceptions import (ChannelUndefinedError,
                                      ExchangeUndefinedError)
from broker_rabbit.queue_handler import QueueHandler


@pytest.mark.unit_test
class TestQueueHandler:
    def test_setup_raise_when_channel_is_not_defined(self):
        queue_handler = QueueHandler(None, None)

        with pytest.raises(ChannelUndefinedError) as error:
            queue_handler.setup_queue(None)

        # Then
        assert 'The Channel is not defined yet' == error.value.args[0]

    def test_setup_raises_when_exchange_is_not_defined(self):
        # Given
        connection = Mock(BlockingConnection)
        channel = connection.channel()
        queue_handler = QueueHandler(channel, None)

        # When
        with pytest.raises(ExchangeUndefinedError) as error:
            queue_handler.setup_queue(None)

        # Then
        assert 'The exchange is not defined' == error.value.args[0]

    def test_setup_queue(self):
        # Given
        channel = Mock()
        exchange_name = 'TEST-EXCHANGE-NAME'
        queue_name = 'TEST-QUEUE-NAME'

        queue_handler = QueueHandler(channel, exchange_name)
        queue_handler.create_queue = Mock()

        # When
        queue_handler.setup_queue(queue_name)

        # Then
        queue_handler.create_queue.assert_called_once_with(queue_name)
        channel.queue_bind.assert_called_once_with(queue=queue_name,
                                                   exchange= exchange_name)

    def test_create_queue(self):
        # Given
        channel = Mock()
        exchange_name = 'TEST-EXCHANGE-NAME'
        queue_name = 'TEST-QUEUE-NAME'
        queue_handler = QueueHandler(channel, exchange_name)

        # When
        queue_handler.create_queue(queue_name)

        # Then
        channel.queue_declare.assert_called_once_with(
            queue=queue_name, durable=True,
            auto_delete=False, arguments={'x-ha-policy': 'all'}
        )
