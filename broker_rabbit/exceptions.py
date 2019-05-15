class BrokerRabbitException(Exception):
    def __init__(self, args, **kwargs):
        super().__init__(args, kwargs)


class UnknownQueueError(BrokerRabbitException):
    pass


class ExchangeNotDefinedYet(BrokerRabbitException):
    pass


class ChannelNotDefinedError(BrokerRabbitException):
    pass


class ChannelIsAlreadyInUse(BrokerRabbitException):
    pass


class ConnectionNotOpenedError(BrokerRabbitException):
    pass


class ConnectionIsAlreadyInUse(BrokerRabbitException):
    pass


class ConnectionIsClosedError(BrokerRabbitException):
    pass


class QueueDoesNotExistError(BrokerRabbitException):
    pass


class WorkerExitError(BrokerRabbitException):
    pass


class BadFormatMessageError(BrokerRabbitException):
    pass


class CallBackError(BrokerRabbitException):
    pass
