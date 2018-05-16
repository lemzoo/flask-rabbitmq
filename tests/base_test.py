import pytest

from tests.rabbit.rabbit_api import client_rabbit_bis, get_queues, \
    delete_queue, client_rabbit
from tests.common import (
    AuthRequests, AnonymousRequests, get_rabbit_url,
    DEFAULT_FRONTEND_DOMAIN, get_rabbit_management_parsed_url,
    DEFAULT_FRONTEND_DOMAIN_INTRANET, DEFAULT_DATAMODEL_PATH, PdfRequests,
    DUMMY_APP)


class TestingConfiguration:

    @staticmethod
    def _get_config(app):
        config = {
            'BROKER_RABBIT_URL': get_rabbit_url(),
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
            'ALERT_MAIL_BROKER': ['test@test.com', 'arthur@martin.com'],
            'FRONTEND_DOMAIN': DEFAULT_FRONTEND_DOMAIN,
            'FRONTEND_DOMAIN_INTRANET': DEFAULT_FRONTEND_DOMAIN_INTRANET,
            'DATAMODEL_PATH': DEFAULT_DATAMODEL_PATH
        }

        return config

    @classmethod
    def setup_class(cls, config={}):
        """
        Initialize flask app and configure it with a clean test database
        """
        app = DUMMY_APP
        app.testing = True
        test_config = cls._get_config(app)
        test_config.update(config)

        cls.app = app
        cls.ctx = app.app_context()
        cls.ctx.push()

    def setup_method(self, method):
        pass

    @classmethod
    def teardown_class(cls):
        cls.ctx.pop()


class WithRequests:
    def make_auth_request(self, user, password=None, url_prefix=None):
        if not url_prefix:
            if isinstance(user, ''):
                url_prefix = '/agent'
            else:
                url_prefix = '/usager'
        return AuthRequests(user, self.app, self.client_app, url_prefix=url_prefix)

    def make_anonymous_request(self):
        return AnonymousRequests(self.app, self.client_app)

    def make_pdf_request(self):
        return PdfRequests(self.app, self.client_app)


@pytest.mark.integration_test
class IntegrationTest(TestingConfiguration):
    pass


@pytest.mark.functional_test
class FunctionalTest(TestingConfiguration, WithRequests):
    pass


@pytest.mark.rabbit
@pytest.mark.functional_test
class RabbitBrokerTest(TestingConfiguration, WithRequests):
    @staticmethod
    def _update_config(config):
        config['DISABLE_EVENTS'] = False
        config['DISABLE_RABBIT'] = False
        return config

    @staticmethod
    def _get_config(app):
        config = TestingConfiguration._get_config(app)
        RabbitBrokerTest._update_config(config)
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
