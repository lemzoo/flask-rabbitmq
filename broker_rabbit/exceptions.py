class BrokerRabbitException(Exception):
    pass


class ExchangeNotDefinedYet(BrokerRabbitException):
    pass


class ExchangeAlreadyExist(BrokerRabbitException):
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


class ExchangeNameDoesntMatch(BrokerRabbitException):
    pass


class BasicPropertiesIsNotSet(BrokerRabbitException):
    pass


class WorkerExitException(BrokerRabbitException):
    pass


class ChannelRunningException(BrokerRabbitException):
    pass


class EventError(Exception):
    pass


class UnknownEventHandlerError(EventError):
    pass


class UnknownEventError(EventError):
    pass


class ProcessorError(Exception):
    pass


class UnknownProcessorError(ProcessorError):
    pass


class ProcessMessageError(ProcessorError):
    pass


class ProcessMessageEventHandlerConfigError(ProcessMessageError):
    pass


class ProcessMessageBadResponseError(ProcessMessageError):
    pass


class ProcessMessageNoResponseError(ProcessMessageError):
    pass


class ProcessServerNotifyRetryError(ProcessMessageError):
    pass


class ProcessMessageNeedWaitError(ProcessorError):
    pass


class ProcessMessageSkippedError(ProcessorError):
    pass
