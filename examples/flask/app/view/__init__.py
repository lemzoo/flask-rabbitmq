from flask_restful import Api

from examples.flask.app.view import UserRegistrationAPI, UserAPI

api = Api()

api.add_resource(UserRegistrationAPI, '/user')
api.add_resource(UserAPI, '/user/<string:email>')


__all__ = ('api',)
