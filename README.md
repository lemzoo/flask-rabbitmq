[![Build Status](https://travis-ci.org/lemzoo/flask-rabbitmq.svg?branch=master)](https://travis-ci.org/lemzoo/flask-rabbitmq)

# Flask with Rabbit MQ message broker in Python

Overview
--------

Flask with Rabbit MQ message broker is an example project which demonstrates the use
of flask API which publishing a message to the Rabbit MQ server.

It contains four routes. And in it's route, an event will send to the message broker.
The broker message will route the message to Rabbit MQ by publishing the message on the correct queue.

 * Flask application
 * A producer which push the messages to the right queue
 * A worker which consume the pushed messages from RabbitMQ server.

Requirements
------------

* Python 3 and requirements file dependencies
* RabbitMQ broker

Installing
----------

Install and update using pip:

Create a virtualenv
    
    $ python -m venv venv


Source the virtualenv

    $ source venv/bin/activate


Install all the dependencies on the requirements file

    $ pip install -Ur requirements.txt


A simple example
----------------

create three files which represent the application


app.py

    from time import sleep
    
    from flask import Flask
    
    from broker_rabbit import BrokerRabbitMQ
    
    
    def process_message(message):
        print('Message received and content is ’{content}’'.format(content=message))
        sleep(2)
    
    
    app = Flask(__name__)
    app.config['RABBIT_MQ_URL'] = 'amqp://guest:guest@localhost:5672/test-flask-rabbitmq'
    app.config['EXCHANGE_NAME'] = 'test-exchange'
    
    
    broker = BrokerRabbitMQ()
    broker.init_app(app=app, queues=['users'], on_message_callback=process_message)


producer.py

    from app import broker
    
    broker.send(queue='users', context={'key': 'value', 'number': 1})


consumer.py

    from app import broker
    
    broker.start(queue='users')


Contributing
------------

This section will be soon available
