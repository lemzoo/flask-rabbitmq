import logging
from unittest.mock import Mock

import pytest

from broker_rabbit.worker import Worker
from broker_rabbit.channels import WorkerChannel

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
        # When
        mocked_worker.consume_message()

        # Then
        assert mocked_worker._worker_channel.run.called

    def test_consume_one_message(self, mocked_worker):
        # When
        mocked_worker.consume_one_message()

        # Then
        channel = mocked_worker._worker_channel
        assert channel.open.called is True
        assert channel.consume_one_message.called is True
        assert channel.close.called is True
