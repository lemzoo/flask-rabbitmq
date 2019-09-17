from unittest.mock import Mock

import pytest

from broker_rabbit import BrokerRabbitMQ, UnknownQueueError
from tests.base_test import RabbitBrokerTest
from tests.common import BROKER_URL_TEST


class TestBrokerRabbitMQ(RabbitBrokerTest):

    def setup(self):
        config = {'RABBIT_MQ_URL': BROKER_URL_TEST,
                  'EXCHANGE_NAME': 'test-exchange'}
        attributes = {'config': config, 'extensions': {}}
        app = Mock(name='broker', **attributes)

        self.queue = 'test-queue'
        self.broker = BrokerRabbitMQ()
        self.broker.init_app(app=app, queues=[self.queue],
                             on_message_callback=self.handler)

    @staticmethod
    def handler(message):
        pass

    def test_return_success_after_publishing_a_message(self):
        # Given
        context = {'key': 'value', 'number': 1}

        # When
        res = self.broker.send(queue=self.queue, context=context)

        # Then
        assert res is None

    def test_return_error_when_trying_to_publish_on_not_registered_queue(self):
        # Given
        queue = 'UNKNOWN_QUEUE'
        context = {'key': 'value', 'number': 1}

        # When
        with pytest.raises(UnknownQueueError) as error:
            self.broker.send(queue=queue, context=context)

        # Then
        assert error.value.args[0][0] == f'Queue ‘{queue}‘ is not registered'
