from urllib import parse


BROKER_MANAGEMENT_PORT = 15672
BROKER_URL_TEST = 'amqp://guest:guest@localhost:5672/test-flask-rabbitmq'


def get_rabbit_management_parsed_url():
    parse.uses_netloc.append("amqp")
    parsed_url = parse.urlparse(BROKER_URL_TEST)

    port = BROKER_MANAGEMENT_PORT
    url = '{host}:{port}'.format(host=parsed_url.hostname, port=port)

    return {
        'url': url,
        'username': parsed_url.username,
        'password': parsed_url.password,
        'vhost': parsed_url.path[1:],
    }
