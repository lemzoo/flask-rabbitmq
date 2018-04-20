from flask import current_app
from flask_script import Manager

from broker_rabbit.exceptions import BrokerRabbitException
from broker_rabbit.worker import Worker
from broker_rabbit.connection_handler import ConnectionHandler

broker_rabbit_manager = Manager(usage="Perform broker rabbitmq operations")


def _get_broker_extension():
    broker_app = current_app.extensions.get('broker_rabbit')

    if not broker_app:
        raise BrokerRabbitException('Extension `broker_rabbit` is not'
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
        raise RuntimeError('This queue `{name}` is not found'.format(name=queue))

    on_message_callback = broker.on_message_callback
    connection_handler = ConnectionHandler(broker.url)

    worker = Worker(connection_handler, queue, on_message_callback)
    print('Start consuming message on the queue `%s`' % queue)
    worker.consume_message()
