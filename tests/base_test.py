import pytest

from tests.rabbit.rabbit_api import get_queues, delete_queue, client_rabbit
from tests.common import get_rabbit_management_parsed_url


class TestingConfiguration:

    @staticmethod
    def get_config():
        config = {
            'DISABLE_SOLR': True,
            'DISABLE_EVENTS': True,
            'DISABLE_BROKER_LEGACY': True,
            'DISABLE_BROKER_BATCH': True,
            'DISABLE_RABBIT': True,
            'DISABLE_SWIFT': True,
            'TESTING': True,
            'ENABLE_CACHE': False,
            'MAIL_SUPPRESS_SEND': True,
            'DISABLE_MAIL': False,
            'FPR_TESTING_STUB': True,
            'FNE_TESTING_STUB': True,
            'AGDREF_NUM_TESTING_STUB': True,
            'ALERT_MAIL_BROKER': ['test@test.com', 'arthur@martin.com']
        }

        return config

    @classmethod
    def setup_class(cls):
        pass

    def setup_method(self, method):
        pass

    @classmethod
    def teardown_class(cls):
        pass


@pytest.mark.rabbit
@pytest.mark.functional_test
class RabbitBrokerTest(TestingConfiguration):
    @staticmethod
    def update_config(config):
        config['DISABLE_EVENTS'] = False
        config['DISABLE_RABBIT'] = False
        return config

    @staticmethod
    def get_config():
        config = TestingConfiguration.get_config()
        RabbitBrokerTest.update_config(config)
        return config

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
        super().setup_method(method)
