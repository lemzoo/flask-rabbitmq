import json
from datetime import datetime
from unittest.mock import Mock

import pytest

from broker_rabbit import BrokerRabbitMQ, UnknownQueueError
from tests.base_test import RabbitBrokerTest
from tests.broker_rabbit.rabbit_api import get_messages, client_rabbit_bis
from tests.common import BROKER_URL_TEST


class TestBrokerRabbitMQ(RabbitBrokerTest):
    queue = 'test-queue'
    broker = BrokerRabbitMQ()

    @property
    def client_rabbit(self):
        return client_rabbit_bis(BROKER_URL_TEST)

    def setup(self):
        attributes = {'config': {'RABBIT_MQ_URL': BROKER_URL_TEST,
                                 'EXCHANGE_NAME': 'test-exchange'}}
        app = Mock(name='broker', **attributes)

        self.broker.init_app(app=app, queues=[self.queue],
                             on_message_callback=self.handler)

    @staticmethod
    def handler(message):
        pass

    def test_return_success_after_publishing_a_message(self):
        # Given
        context = {'key': 'value', 'number': 1}

        # When
        self.broker.send(queue=self.queue, context=context)

        # Then
        # TODO: retrieve the message on the broker and make the assertion
        messages = get_messages(client=self.client_rabbit, queue=self.queue)
        assert len(messages) == 1

        body = json.loads(messages[0]['body'])
        assert body['queue'] == self.queue
        now = datetime.utcnow()
        assert body['created_at'][:19] == now.isoformat()[:19]
        assert body['context'] == context

    def test_return_error_when_trying_to_publish_on_not_registered_queue(self):
        # Given
        queue = 'UNKNOWN_QUEUE'
        context = {'key': 'value', 'number': 1}

        # When
        with pytest.raises(UnknownQueueError) as error:
            self.broker.send(queue=queue, context=context)

        # Then
        assert error.value.args[0][0] == f'Queue ‘{queue}‘ is not registered'
