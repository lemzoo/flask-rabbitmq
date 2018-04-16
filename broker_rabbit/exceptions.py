class BrokerRabbitException(Exception):
    pass


class UnknownQueueError(BrokerRabbitException):
    pass


class ExchangeNotDefinedYet(BrokerRabbitException):
    pass


class ChannelDoesntExist(BrokerRabbitException):
    pass


class ChannelIsAlreadyInUse(BrokerRabbitException):
    pass


class ConnectionNotOpenedYet(BrokerRabbitException):
    pass


class ConnectionIsAlreadyInUse(BrokerRabbitException):
    pass


class ConnectionIsClosed(BrokerRabbitException):
    pass


class QueueNameDoesntMatch(BrokerRabbitException):
    pass


class QueueDoesNotExist(BrokerRabbitException):
    pass


class WorkerExitException(BrokerRabbitException):
    pass
