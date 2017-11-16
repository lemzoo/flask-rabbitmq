import logging

from broker_rabbit.rabbit.channels import WorkerChannel


class Worker:
    """This is a  Worker that will handle a connection and queue to work
    on the available messages in RabbitMQ server.
    The worker will setup the channel to use and when finished, it will also
    close the current channel.
    """

    def __init__(self, connection_handler, queue, event_handler):
        """
        Instantiate a Worker with an opened connection and a queue name to work
        The channel is opened in the instantiation of the module for ready use.
        It will be closed after consuming the message on the given queue.

        :param ConnectionHandler connection : The connection to use between the
         worker and RabbitMQ.
        :param Queue queue : The name of the queue to work
        :param EventHandler event_handler: the event handler which execute the message
        """
        self._connection = connection_handler.get_current_connection()
        self._queue = queue
        self.event_handler = event_handler
        self._worker_channel = WorkerChannel(self._connection, self._queue, self.event_handler)

        self.logger = logging.getLogger('RabbitMQ-Worker')

    def consume_message(self):
        self.logger.info('Consuming message on queue %s' % self._queue)
        self._worker_channel.run()

    def consume_one_message(self):
        try:
            self.logger.info('Consuming one message on queue %s' % self._queue)
            self._worker_channel.open()
            ret = self._worker_channel.consume_one_message()
        finally:
            self._worker_channel.close()
        return ret
