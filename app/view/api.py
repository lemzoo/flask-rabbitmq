from flask import abort, request
from flask_restful import Resource

from app.events.events import EVENTS as event_managers

from app.model import User, UserSchema


class UserApi(Resource):

    def get(self, email):
        user = User.objects.get_or_404(email=email)
        user_schema = UserSchema()
        user_dump = user_schema.dump(user).data
        event_managers.utilisateur.cree.send(user_dump)
        return user_dump

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
        return user_schema.dump(user).data
