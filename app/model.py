from flask_marshmallow import Schema
from flask_mongoengine import Document
from mongoengine import fields


class User(Document):
    email = fields.EmailField(required=True, unique=True)
    first_name = fields.StringField(required=True, min_length=2)
    last_name = fields.StringField(required=True, min_length=2)


class UserSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ('email', 'first_name', 'last_name')
        model = User
        model_build_obj = True
