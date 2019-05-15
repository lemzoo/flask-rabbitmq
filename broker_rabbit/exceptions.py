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


class ConnectionNotOpenedYet(BrokerRabbitException):
    pass


class ConnectionIsAlreadyInUse(BrokerRabbitException):
    pass


class ConnectionIsClosed(BrokerRabbitException):
    pass


class QueueDoesNotExistError(BrokerRabbitException):
    pass


class WorkerExitException(BrokerRabbitException):
    pass



class BadFormatMessageError(BrokerRabbitException):
    pass



class CallBackError(BrokerRabbitException):
    pass
