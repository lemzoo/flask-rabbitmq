import logging
from unittest.mock import Mock

import pytest

from broker.broker_rabbit.rabbit import Worker
from broker.broker_rabbit.rabbit.channels import WorkerChannel

RABBIT_MQ_WORKER = 'test-logger'
QUEUE = 'test-queue'


@pytest.fixture
def mocked_worker():
    class MockedWorker(Worker):
        def __init__(self):
            self._worker_channel = Mock(WorkerChannel)
            self._queue = QUEUE
            self.logger = logging.getLogger(RABBIT_MQ_WORKER)

    return MockedWorker()


@pytest.mark.unit_test
class TestWorker:
    def test_consume_message(self, mocked_worker):
        mocked_worker.consume_message()

        assert mocked_worker._worker_channel.run.called

    def test_consume_one_message(self, mocked_worker):
        mocked_worker.consume_one_message()

        assert mocked_worker._worker_channel.open.called
        assert mocked_worker._worker_channel.consume_one_message.called
        assert mocked_worker._worker_channel.close.called
