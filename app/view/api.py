from flask import abort, request
from flask_restful import Resource

from app.model import User, UserSchema


class UserApi(Resource):

    def get(self, email):
        user = User.objects.get_or_404(email=email)
        user_schema = UserSchema()
        return user_schema.dump(user).data

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
