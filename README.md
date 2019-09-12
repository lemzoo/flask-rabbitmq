[![Build Status](https://travis-ci.org/lemzoo/flask-rabbitmq.svg?branch=master)](https://travis-ci.org/lemzoo/flask-rabbitmq)

# Flask with Rabbit MQ message broker in Python

Overview
========

Flask with Rabbit MQ message broker is an example project which demonstrates the use
of flask API which publishing a message to the Rabbit MQ server.

It contains four routes. And in it's route, an event will send to the message broker.
The broker message will route the message to Rabbit MQ by publishing the message on the correct queue.

 * Flask API: Provides four route which publish the message.
 * Broker: Routes the message to the correct queue on the RabbitMQ server.
 * Broker Manager: Provides a services which consume the message on RabbitMQ server.

Requirements
===========

* Python 3 and requirements file dependencies
* virtualenv
* RabbitMQ

Install
=======

The quick way is use the provided `make` file.

Create first a virtual env
    
    $ virtualenv -p /usr/bin/python3 venv

Where /usr/bin/python3 is the location of the python on your laptop

Source the virtualenv

    $ source venv/bin/activate


Install all the dependencies on the requirements file

    $ pip install -Ur requirements.txt


Getting Started
===============

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
