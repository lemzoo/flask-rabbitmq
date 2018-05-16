import json
from base64 import b64encode
from collections import namedtuple
from os import environ
from urllib import parse

import pytest
from flask import Flask

DEFAULT_FRONTEND_DOMAIN = 'http://internet.com'
DEFAULT_FRONTEND_DOMAIN_INTRANET = 'http://intranet'
DEFAULT_DATAMODEL_PATH = 'tests/sief/controller/datamodel/test_datamodel.json'


class NOT_SET:
    def __repr__(self):
        return '<not_set>'


NOT_SET = NOT_SET()


def _patch_url_if_xdist(url):
    if environ.get('PYTEST_XDIST_WORKER'):
        url = '%s-%s' % (url, environ.get('PYTEST_XDIST_WORKER'))
    return url


def _patch_url_if_mongomock(url):
    if not pytest.config.getoption('--runmongodb'):
        url = url.replace('mongodb://', 'mongomock://', 1)
    return url


DUMMY_APP = Flask(__name__)
DUMMY_APP.config['BROKER_RABBIT_TEST_MANAGEMENT_PORT'] = 15672


def get_rabbit_url():
    return 'amqp://guest:guest@localhost:5672/test-flask-rabbitmq'


def get_rabbit_management_parsed_url():
    parse.uses_netloc.append("amqp")
    rabbit_url = get_rabbit_url()
    parsed_url = parse.urlparse(rabbit_url)

    port = DUMMY_APP.config['BROKER_RABBIT_TEST_MANAGEMENT_PORT']
    url = '{host}:{port}'.format(host=parsed_url.hostname, port=port)

    return {
        'url': url,
        'username': parsed_url.username,
        'password': parsed_url.password,
        'vhost': parsed_url.path[1:],
    }


def update_payload(payload, route, value):
    splitted = route.split('.')
    cur_node = payload
    for key in splitted[:-1]:
        if isinstance(cur_node, (list, tuple)):
            key = int(key)
            if len(cur_node) <= key:
                raise ValueError('indice %s is not in list' % key)
        elif isinstance(cur_node, dict):
            if key not in cur_node:
                cur_node[key] = {}
        else:
            raise ValueError('%s must lead to a dict' % key)
        cur_node = cur_node[key]
    last_key = splitted[-1]
    if value is NOT_SET:
        if last_key in cur_node:
            del cur_node[last_key]
    elif isinstance(cur_node, (list, tuple)):
        cur_node[int(last_key)] = value
    else:
        cur_node[last_key] = value


def assert_response_contains_links(response, links):
    assert '_links' in response.data
    data_links = response.data['_links']
    for l in links:
        assert l in data_links, l
    assert not data_links.keys() - set(links)


class AnonymousRequests:
    """Wrap user model to easily do requests on the api with it credentials"""

    CookedResponse = namedtuple('CookedResponse', ['status_code', 'headers', 'data'])

    def __init__(self, app, client_app):
        self.client_app = client_app
        self.app = app

    def _decode_response(self, response):
        encoded = response.get_data()
        if encoded:
            decoded = json.loads(encoded.decode('utf-8'))
            if isinstance(decoded, str):
                decoded = json.loads(decoded)
            assert isinstance(decoded, dict)
        else:
            decoded = encoded
        return self.CookedResponse(response.status_code, response.headers, decoded)

    def __getattr__(self, name):
        method_name = name.upper()
        if method_name not in ['POST', 'PATCH', 'PUT', 'GET', 'OPTIONS', 'HEAD', 'DELETE']:
            raise RuntimeError('Only HTTP verbs are allowed as methods')
        return lambda *args, **kwargs: self._mk_request(method_name)(*args, **kwargs)

    def request(self, method, *args, **kwargs):
        return self._mk_request(method)(*args, **kwargs)

    def _mk_request(self, method_name):
        def caller(route, headers=None, data=None, auth=True, dump_data=True, **kwargs):
            if dump_data:
                serial_data = json.dumps(data, cls=self.app.json_encoder)
            else:
                serial_data = data
            headers = headers or {}
            params = {
                'headers': headers,
                'content_type': 'application/json',
                'content_length': len(serial_data)
            }
            params.update(kwargs)
            if data or isinstance(data, dict):
                params['data'] = serial_data
            method_fn = getattr(self.client_app, method_name.lower())
            with self.app.app_context():
                raw_ret = method_fn(route, **params)
            return self._decode_response(raw_ret)

        return caller


class AuthRequests(AnonymousRequests):
    """Wrap user model to easily do requests on the api with it credentials"""

    def __init__(self, document, app, client_app, url_prefix=None):
        super().__init__(app, client_app)
        self.document = document
        # generate a token for the requests
        with self.app.app_context():
            self.token = ''

    def _mk_request(self, method_name):
        parent_caller = super()._mk_request(method_name)

        def caller(*args, headers=None, auth=True, **kwargs):
            headers = headers or {}
            if 'Origin' not in headers:
                headers['Origin'] = DUMMY_APP.config['FRONTEND_DOMAIN_INTRANET']
            if auth:
                headers['Authorization'] = 'Token ' + self.token
            return parent_caller(*args, headers=headers, **kwargs)

        return caller


class PdfRequests(AnonymousRequests):
    def _decode_response(self, response):
        assert response.mimetype == 'application/pdf'
        return response


def build_basic_auth(email, password):
    concat = '%s:%s' % (email, password)
    return 'Basic ' + b64encode(concat.encode()).decode()


def build_request(headers=None, auth=None, data=None, dump_data=True):
    kw = {'headers': headers or {}}
    if auth:
        kw['headers']['Authorization'] = build_basic_auth(*auth)
    if data:
        if dump_data:
            kw['data'] = json.dumps(data)
            kw['content_type'] = 'application/json'
        else:
            kw['data'] = data
        kw['content_length'] = len(kw['data'])
    return kw


class ClientAppRouteWrapper:
    def __init__(self, app):
        self.app = app
        self.client_app = app.test_client()

    def _wrap(self, fn):
        url_prefix = self.app.config['BACKEND_API_PREFIX']
        if not url_prefix:
            return fn

        def wrapper(route, *args, force_route=False, **kwargs):
            if not force_route and not route.startswith(url_prefix):
                route = url_prefix + route
            return fn(route, *args, **kwargs)

        return wrapper

    def __getattr__(self, method_name):
        if method_name in ['post', 'patch', 'put', 'get',
                           'options', 'head', 'delete']:
            return self._wrap(getattr(self.client_app, method_name))
        return super().__getattr__(method_name)


def pagination_testbed(user_req, route):
    """
    Generic pagination test (just need to populate 5 documents before)
    """
    r = user_req.get(route)
    assert r.status_code == 200
    assert r.data['_meta']['total'] == 5, ('Must be 5 elements in the'
                                           ' ressource to use the testbed !')
    items_len = len(r.data['_items'])
    if items_len < r.data['_meta']['per_page']:
        assert items_len == r.data['_meta']['total']
    else:
        assert items_len == r.data['_meta']['per_page']
    assert '_links' in r.data['_items'][0], r.data['_items'][0]
    assert 'self' in r.data['_items'][0]['_links'], r.data['_items'][0]
    assert 'parent' in r.data['_items'][0]['_links'], r.data['_items'][0]

    # Now let's test the pagination !

    def check_page(data, page, count, per_page, total):
        assert len(r.data['_items']) == count
        assert r.data['_meta']['page'] == page
        assert r.data['_meta']['per_page'] == per_page
        assert r.data['_meta']['total'] == total

    for page, count, per_page in [(1, 2, 2), (2, 2, 2), (3, 1, 2),
                                  (1, 5, 5), (1, 5, 100), (3, 1, 2)]:
        r = user_req.get('%s?page=%s&per_page=%s' % (route, page, per_page))
        assert r.status_code == 200, r
        check_page(r.data, page, count, per_page, 5)
    # Test links
    r = user_req.get('%s?page=1&per_page=100' % route)
    assert r.status_code == 200, r
    assert 'next' not in r.data['_links']
    assert 'previous' not in r.data['_links']
    assert 'self' in r.data['_links']
    r = user_req.get('%s?page=1&per_page=2' % route)
    assert r.status_code == 200, r
    assert 'next' in r.data['_links']
    assert 'previous' not in r.data['_links']
    assert 'self' in r.data['_links']
    r = user_req.get('%s?page=2&per_page=2' % route)
    assert r.status_code == 200, r
    assert 'next' in r.data['_links']
    assert 'previous' in r.data['_links']
    assert 'self' in r.data['_links']
    # Test bad pagination as well
    r = user_req.get('%s?page=2&per_page=10' % route)
    assert r.status_code == 404, r
    for page, per_page in [('', 20), (1, ''), ('nan', 20), (1, 'nan'),
                           (-1, 20), (1, -20)]:
        r = user_req.get('%s?page=%s&per_page=%s' % (route, page, per_page))
        assert r.status_code == 400, (page, per_page)
