import json

from flask import abort

from app.model import User


def get(email):
    user = User.objects.get_or_404(email=email)
    return json.dumps({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    })


def post(payload={}):
    user = User(
        email=payload['email'],
        first_name=payload['first_name'],
        last_name=payload['last_name'])
    try:
        user.save()
    except Exception as error:
        abort(400, str(error))
    return user.email