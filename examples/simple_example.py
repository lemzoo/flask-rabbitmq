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

queue = 'users'

broker = BrokerRabbitMQ()
broker.init_app(app=app, queues=[queue], on_message_callback=process_message)

message_context = {
    'key': 'value',
    'number': 1
}

broker.send(queue=queue, context=message_context)

