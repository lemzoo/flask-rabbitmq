class BrokerRabbitError(Exception):
    def __init__(self, args, **kwargs):
        super().__init__(args, kwargs)


class UnknownQueueError(BrokerRabbitError):
    pass


class ExchangeUndefinedError(BrokerRabbitError):
    pass


class ChannelUndefinedError(BrokerRabbitError):
    pass


class ChannelIsAlreadyInUseError(BrokerRabbitError):
    pass


class ConnectionNotOpenedError(BrokerRabbitError):
    pass


class ConnectionIsAlreadyInUseError(BrokerRabbitError):
    pass


class ConnectionIsClosedError(BrokerRabbitError):
    pass


class QueueDoesNotExistError(BrokerRabbitError):
    pass


class WorkerExitError(BrokerRabbitError):
    pass


class BadFormatMessageError(BrokerRabbitError):
    pass


class CallBackError(BrokerRabbitError):
    pass
