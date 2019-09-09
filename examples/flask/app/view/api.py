from flask import request
from flask_restful import Resource

from examples.flask.app.events import EVENTS as event_managers


class UserRegistrationAPI(Resource):
    """API for registration or listing user"""

    def get(self):
        raise NotImplementedError('API ‘GET‘ a list of user is not implemented')

    def post(self):
        payload = request.get_json()
        event_managers.user.create.send(**payload)
        return payload


class UserAPI(Resource):
    """API for viewing a single user"""

    def get(self, email):
        return NotImplementedError('API `GET` is in construction')

    def patch(self, email):
        raise NotImplementedError('API `PATCH` is in construction')

    def delete(self, email):
        raise NotImplementedError('API `DELETE` is in construction')
