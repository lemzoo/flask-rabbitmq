import json
import logging
import subprocess

import pika
from pyrabbit import Client

logger = logging.getLogger(__name__)


def client_rabbit_bis(url: str):
    parameters = pika.URLParameters(url)
    client_rabbit = pika.BlockingConnection(parameters=parameters)
    return client_rabbit


def client_rabbit(url, username, password):
    """Configure the client for broker_rabbit

    :param str url: The address url of the host where broker_rabbit located
    :param str username: The username id
    :param str password: The password
    :return Client client: authenticated client which is ready to use
    """
    client = Client(url, username, password)
    return client


def get_queues_old(admin_path, vhost):
    cmd = "{} list queues name vhost | grep {} | tr -d \| |tr -d '\n'".format(
        admin_path, vhost)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    return str(out.decode('utf8').replace(vhost, "")).split()


def get_queues(client, vhost):
    """Get all queues, or all queues in a vhost if vhost is not None.
    Returns a list.

    :param Client client : authenticated client which is ready to use
    :param str vhost: virtual host where the queues will be found
    :return A list of dicts, each representing a queue
    """
    queues = [q['name'] for q in client.get_queues(vhost)]

    return queues


def delete_queue(client, vhost, queue):
    """Deletes the named queue from the named vhost.

    :param Client client : authenticated client which is ready to use
    :param str vhost : Name of the virtual host ot get exchange
    :param str queue : Name of the queue to delete
    """
    client.delete_queue(vhost, queue)


def get_messages(client, queue):
    """Gets <count> messages from the queue..

    :param pika.BlockingConnection client : Authentificated client which is ready to use
    :param str queue: Name of the queue to consume from.
    :return list messages: list of dicts. messages[msg-index][‘payload’]
    will contain the message body.
    """
    messages = list()
    channel = client.channel()
    channel.queue_declare(queue=queue, durable=True, auto_delete=False)

    try:
        for method_frame, properties, body in channel.consume(
                queue=queue,
                exclusive=True,
                inactivity_timeout=10):
            message_body = json.loads(body.decode('utf8').replace("'", '"'))
            message_body = json.dumps(message_body)
            messages.append({'method_frame': method_frame,
                            'properties': properties, 'body': message_body})
            # Acknowledge the message
            channel.basic_ack(method_frame.delivery_tag)
            # Escape out of the loop after 10 messages
            if method_frame.delivery_tag == 1:
                break
    except TypeError:
        logger.info("Fin de la lecture des messages.")

    # Cancel the consumer and return any pending messages
    requeued_messages = channel.cancel()
    logger.info('Requeued %i messages' % requeued_messages)

    # Close the channel and the connection
    channel.close()
    return messages


def get_number_message_on_queue(client, queue):
    """Gets <count> messages from the queue..

    :param pika.BlockingConnection client : Authentificated client which is ready to use
    :param str queue: Name of the queue to consume from.
    :return int numbe_msg: The number of the message availabale on
                           the specified queue
    """
    messages = list()
    channel = client.channel()
    channel.queue_declare(queue=queue, durable=True, auto_delete=False)

    try:
        for method_frame, properties, body in channel.consume(
                queue=queue,
                exclusive=True,
                inactivity_timeout=30):
            messages.append({'method_frame': method_frame, 'properties': properties, 'body': body})
            # Acknowledge the message
            channel.basic_ack(method_frame.delivery_tag)
    except TypeError:
        print("Fin de la lecture des messages.")

    # Cancel the consumer and return any pending messages
    requeued_messages = channel.cancel()
    logger.info('Requeued %i messages' % requeued_messages)

    # Close the channel and the connection
    channel.close()
    return len(messages)


def purge_queue(client, queue):
    """Gets <count> messages from the queue..

    :param pika.BlockingConnection client : Authentificated client which is ready to use
    :param str queue: Name of the queue to consume from.
    :return int numbe_msg: The number of the message availabale on
                           the specified queue
    """
    channel = client.channel()

    channel.queue_declare(queue=queue, durable=True, auto_delete=False)
    channel.queue_purge(queue)
    channel.close()
