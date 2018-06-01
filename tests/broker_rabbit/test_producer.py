from unittest.mock import Mock

import pytest

from broker_rabbit.channels import ProducerChannel
from broker_rabbit.connection_handler import ConnectionHandler
from broker_rabbit.producer import Producer
from tests import common


@pytest.mark.unit_test
class TestProducer:
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
        self.queues = ['first-queue', 'second-queue']
        self.producer = Producer(self.channel, self.exchange_name, self.queues)

    def test_should_bootstrap_environment_to_work(self):
        pass

    def test_should_publish_on_given_queue(self):
        # Given
        first_queue = self.queues[0]
        message = "TEST_MESSAGE"

        # When
        self.producer.publish(first_queue, message)

        # Then
        assert self.channel.open.called is True
        self.channel.send_message.assert_called_with(self.exchange_name, first_queue, message)
        assert self.channel.close.called is True
