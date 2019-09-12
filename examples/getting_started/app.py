from time import sleep

from flask import Flask

from broker_rabbit import BrokerRabbitMQ


def process_message(message):
    print('Message received and content is ’{content}’'.format(content=message))
    sleep(1)


app = Flask(__name__)
connection_string = 'amqp://guest:guest@localhost:5672/test-flask-rabbitmq'
app.config['RABBIT_MQ_URL'] = connection_string
app.config['EXCHANGE_NAME'] = 'test-exchange'

broker = BrokerRabbitMQ()
broker.init_app(app=app, queues=['users'], on_message_callback=process_message)
