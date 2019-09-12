from examples.getting_started.app import broker

broker.send(queue='users', context={'key': 'value', 'number': 1})
