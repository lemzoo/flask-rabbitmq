import pytest

from tests.rabbit.rabbit_api import get_queues, delete_queue, client_rabbit
from tests.common import get_rabbit_management_parsed_url


@pytest.mark.rabbit
@pytest.mark.functional_test
class RabbitBrokerTest:

    @staticmethod
    def _clean_rabbit():
        """Get all queues names and delete each."""
        parsed_url = get_rabbit_management_parsed_url()
        url = parsed_url['url']
        user = parsed_url['username']
        password = parsed_url['password']
        vhost = parsed_url['vhost']

        client_api_rabbit = client_rabbit(url, user, password)

        queues = get_queues(client_api_rabbit, vhost)
        for queue in queues:
            delete_queue(client_api_rabbit, vhost, queue)

    def setup_method(self, method):
        self._clean_rabbit()
