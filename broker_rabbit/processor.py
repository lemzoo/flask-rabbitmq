from broker_rabbit.exceptions import UnknownProcessorError


class ProcessorManager:

    """
    Hold a list of processor (i.e. functions) a worker can apply to a message.
    """

    def __init__(self):
        self._processors = {}

    def exists(self, name):
        return name in self._processors

    def register(self, function, name=None):
        "Register a new processor"
        if not name:
            name = function.__name__
        self._processors[name] = function
        return function

    def find(self, name):
        "Retreive a processor from it name"
        return self._processors.get(name)

    def execute(self, processor, *args, **kwargs):
        "Process the given message with it assign processor"
        f = self.find(processor)
        if f:
            return f(*args, **kwargs)
        else:
            raise UnknownProcessorError('Cannot execute processor %s' %
                                        processor)

    def list(self):
        return list(self._processors.keys())


processor_manager = ProcessorManager()
find_and_execute = processor_manager.execute
register_processor = processor_manager.register
