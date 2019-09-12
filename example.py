from time import sleep

from flask import Flask

from broker_rabbit import BrokerRabbitMQ


def process_message(message):
    print('Message Content = ’{content}’'.format(content=message))
    sleep(2)


app = Flask(__name__)
rabbitmq_url = 'amqp://guest:guest@localhost:5672/test-flask-rabbitmq'
app.config['RABBIT_MQ_URL'] = rabbitmq_url
app.config['EXCHANGE_NAME'] = 'testing'
queues = ['users']

broker = BrokerRabbitMQ()
broker.init_app(app, queues, process_message())

import pdb; pdb.set_trace()
