from flask import current_app
from flask_script import Manager

from broker_rabbit.rabbit.worker import Worker
from broker_rabbit.rabbit.connection_handler import ConnectionHandler

broker_rabbit_manager = Manager(usage="Perform broker rabbitmq operations")


def _get_broker_rabbit():
    broker_rabbit = current_app.extensions.get('broker')
    if not broker_rabbit:
        raise Exception('Extension `broker` not initialized')
    return broker_rabbit


@broker_rabbit_manager.command
def list_queues():
    """List all available queue in the app"""
    broker = _get_broker_rabbit()
    for queue in broker.queues:
        print('Queue name : `%s`' % queue)


@broker_rabbit_manager.option('queue', help='Single queue to consume')
def start(queue):
    """Start worker on a given queue
    :param queue: the queue which you consume message for
    """
    broker = _get_broker_rabbit()

    if queue not in broker.queues:
        raise RuntimeError('This queue `%s` is not found' % queue)

    rabbit_url = broker.rabbit_url
    event_handler = broker.event_handler
    connection_handler = ConnectionHandler(rabbit_url)

    worker = Worker(connection_handler, queue, event_handler)
    worker.consume_message()
