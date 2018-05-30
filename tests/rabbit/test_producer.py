from unittest.mock import Mock

import pytest

from broker_rabbit.channels import ProducerChannel
from broker_rabbit.producer import Producer


@pytest.mark.unit_test
class TestProducer:
    def test_publish(self):
        # Given
        connection = None
        exchange_name = "TEST_EXCHANGE_NAME"
        application_id = 'TEST-APPLICATION-ID'
        delivery_mode = 2
        producer = Producer(connection, exchange_name, application_id, delivery_mode)
        queues = ['first-queue', 'second-queue']
        producer._producer_channel = Mock(ProducerChannel)
        producer.bootstrap(queues)
        first_queue = queues[0]
        message = "TEST_MESSAGE"

        # When
        producer.publish(first_queue, message)

        # Then
        channel = producer._producer_channel
        assert channel.open.called is True
        channel.send_message.assert_called_with(exchange_name, first_queue, message)
        assert channel.close.called is True
