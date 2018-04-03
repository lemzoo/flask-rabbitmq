from flask import abort, request
from flask_restful import Resource

from app.events.events import EVENTS as event_managers

from app.model import User, UserSchema


class UserRegistrationAPI(Resource):
    """API for registration or listing user"""

    def get(self):
        raise NotImplementedError('GET a list of user is not implemented')

    def post(self):
        payload = request.get_json()
        user_schema = UserSchema()

        user, errors = user_schema.load(payload)
        if errors:
            abort(400, str(errors))

        user = User(**payload)

        try:
            user.save()
        except Exception as error:
            abort(400, str(error))
        user_dump = user_schema.dump(user).data
        event_managers.user.create.send(**user_dump)
        return user_schema.dump(user).data


class UserAPI(Resource):
    """API for viewing a single user"""

    def get(self, email):
        user = User.objects.get_or_404(email=email)
        user.update_view()
        user.save()

        user_schema = UserSchema()
        user_dump = user_schema.dump(user).data
        event_managers.user.read.send(**user_dump)
        return user_dump

    def patch(self, email):
        raise NotImplementedError('API `PATCH` is in construction')

    def delete(self, email):
        raise NotImplementedError('API `DELETE` is in construction')
