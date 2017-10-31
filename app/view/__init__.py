from flask_restful import Api

from app.view.api import UserApi

api = Api()

api.add_resource(UserApi, '/user', '/user/<string:email>')


__all__ = ('api',)
