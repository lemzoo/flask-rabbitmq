from unittest.mock import Mock

import pytest

from broker.broker_rabbit.rabbit.channels import ProducerChannel
from broker.broker_rabbit.rabbit.producer import Producer


@pytest.mark.unit_test
class TestProducer:
    def test_publish(self):
        exchange_name = "TEST_EXCHANGE_NAME"
        producer = Producer(None, exchange_name)
        producer._producer_channel = Mock(ProducerChannel)
        queue = "FAKE_QUEUE"
        message = "TEST_MESSAGE"

        producer.publish(queue, message)

        assert producer._producer_channel.open.called
        producer._producer_channel.send_message.assert_called_with(exchange_name, queue, message)
        assert producer._producer_channel.close.called
