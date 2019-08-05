from flask import current_app
from flask_script import Manager

from broker_rabbit.exceptions import BrokerRabbitError
from broker_rabbit.worker import Worker


broker_rabbit_manager = Manager(usage="Perform broker rabbitmq operations")


def _get_broker_extension():
    broker_app = current_app.extensions.get('broker_rabbit')

    if not broker_app:
        raise BrokerRabbitError('Extension `broker_rabbit` is not '
                                'initialized. Call broker.init_app')
    return broker_app


@broker_rabbit_manager.command
def list_queues():
    """List all available queue in the app"""
    broker = _get_broker_extension()
    for queue in broker.queues:
        print('Queue name : `%s`' % queue)


@broker_rabbit_manager.option('queue', help='Single queue to consume')
def start(queue):
    """Start worker on a given queue
    :param queue: the queue which you consume message for
    """
    broker = _get_broker_extension()

    if queue not in broker.queues:
        raise RuntimeError(f'Queue with name`{queue}` not found')

    on_message_callback = broker.on_message_callback
    connection_handler = broker.connection_handler

    worker = Worker(connection_handler, queue, on_message_callback)
    print(f'Start consuming message on the queue `{queue}')
    worker.consume_message()
