# Flask with Rabbit MQ message broker in Python

Overview
========

Flask with Rabbit MQ message broker is an example project which demonstrates the use 
of flask API which publishing a message to the Rabbit MQ server.

It contains four routes. And in it's route, an event will send to the message broker. 
The broker message will route the message to Rabbit MQ by publishing the message on the correct queue.

 * Flask API: Provides four route which publish the message.
 * Broker: Routes the message to the correct queue on the RabbitMQ server.
 * Broker Manager: Provides a services which consume the message on Rabbit. 

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

Source the virtual env
<code>
$ source venv/bin/activate
</code>

Install all the dependencies on the requirements file
<code>
$ pip install -Ur requirements.txt
</code>


Starting and Stopping Backend and Broker
========================================

To launch the Backend:
<code>
$ manager.py runserver
</code>

To list the availbales queues which pusblish and consume for: 
<code>
$ manager.py broker list_queues
</code>

To start consuming on a queue `user`
<code>
$ manager.py broker start user
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
      
    ===> 200 Ok
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
      "first_name": "Done"
    }
      
    ===> 200 Ok
    {
        "email": "john.doe@user.com",
        "first_name": "Done",
        "last_name": "John"
    }
    ...... output truncated ......
