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
<code>
$ virtualenv -p /usr/bin/python3 venv
</code>

Where /usr/bin/python3 is the location of the python on your laptop

Source the virtualenv
<code>
$ source venv/bin/activate
</code>

Install all the dependencies on the requirements file
<code>
$ pip install -Ur requirements.txt
</code>


Starting and Stopping API and Broker
========================================

To launch the API on debug mode:
<code>
$ python manager.py runserver -dr
</code>

To list the availbales queues which pusblish and consume for:
<code>
$ python manager.py broker list_queues
</code>

To start consuming on a queue `user`
<code>
$ python manager.py broker start user
</code>


APIs and Documentation
======================


To create a new user:

    POST /users
    Create a new user basing on the given payload.

    {
      "email": "john.doe@user.com",
      "first_name": "Doe",
      "last_name": "John"
    }

    ===> 201 Ok
    {
        "email": "john.doe@user.com",
        "first_name": "Doe",
        "last_name": "John"
    }
    ...... output truncated ......

To get a created user:

    GET /users/john.doe@user.com
    Returns a corresponding user in the database.

    {
        "email": "john.doe@user.com",
        "first_name": "Doe",
        "last_name": "John"
    },
    ...... output truncated ......


To update a user:

    PATCH /users/john.doe@user.com
    Create a new user basing on the given payload.

    {
      "first_name": "Doe-updated"
    }

    ===> 200 Ok
    {
        "email": "john.doe@user.com",
        "first_name": "Doe-updated",
        "last_name": "John"
    }
    ...... output truncated ......

Create a user :
    Sent a welcome message
    Sent a temporary password to change
    Sent a link to activate the account
