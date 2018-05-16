from unittest.mock import Mock

import pytest
from pika import BlockingConnection

from broker.broker_rabbit.exceptions import (ChannelDoesntExist, QueueNameDoesntMatch,
                                             ExchangeNotDefinedYet)
from broker.broker_rabbit.rabbit import QueueHandler


@pytest.mark.unit_test
class TestQueueHandler:
    def test_setup_queue(self):
        channel = Mock()
        exchange_name = 'TEST_EXCHANGE_NAME'
        queue_handler = QueueHandler(channel, exchange_name)

        queue_handler.create_queue = Mock()

        queue_name = 'TEST_QUEUE_NAME'
        queue_handler.setup_queue(queue_name)

        queue_handler.create_queue.assert_called_with(queue_name)

    def test_setup_queue_without_channel(self):
        queue_handler = QueueHandler(None, None)

        with pytest.raises(ChannelDoesntExist):
            queue_handler.setup_queue(None)

    def test_setup_queue_without_exchange(self):
        connection = Mock(BlockingConnection)
        channel = connection.channel()
        queue_handler = QueueHandler(channel, None)

        with pytest.raises(ExchangeNotDefinedYet):
            queue_handler.setup_queue(None)

    def test_setup_queues(self):
        channel = Mock()
        exchange_name = 'TEST_EXCHANGE_NAME'
        queue_handler = QueueHandler(channel, exchange_name)
        queue_handler.setup_queue = Mock()

        queues = ['TEST_QUEUE_1', 'TEST_QUEUE_2', 'TEST_QUEUE_3']
        queue_handler.setup_queues(queues)

        assert queue_handler.setup_queue.call_count == len(queues)

    def test_create_queue_with_short_name(self):
        channel = Mock()
        exchange_name = 'TEST_EXCHANGE_NAME'
        queue_handler = QueueHandler(channel, exchange_name)

        queue_name = '-'

        with pytest.raises(QueueNameDoesntMatch):
            queue_handler.create_queue(queue_name)

    def test_create_queue(self):
        channel = Mock()
        exchange_name = 'TEST_EXCHANGE_NAME'
        queue_handler = QueueHandler(channel, exchange_name)

        queue_name = 'TEST_QUEUE_NAME'

        ret = queue_handler.create_queue(queue_name)

        assert ret == queue_name
        queue_handler._channel.queue_declare.assert_called_with(
            queue=queue_name,
            durable=True,
            auto_delete=False,
            arguments={'x-ha-policy': 'all'}
        )

    def test_bind_queue_to_default_exchange(self):
        channel = Mock()
        exchange_name = 'TEST_EXCHANGE_NAME'
        queue_handler = QueueHandler(channel, exchange_name)

        queue_name = 'TEST_QUEUE_NAME'

        queue_handler.bind_queue_to_default_exchange(queue_name)

        queue_handler._channel.queue_bind.assert_called_with(
            queue=queue_name, exchange=exchange_name)
