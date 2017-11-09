from flask_marshmallow import Schema
from flask_mongoengine import Document
from mongoengine import fields


class User(Document):
    email = fields.EmailField(required=True, unique=True)
    first_name = fields.StringField(required=True, min_length=2)
    last_name = fields.StringField(required=True, min_length=2)
    view_count = fields.IntField(default=0)
    is_valid = fields.BooleanField(default=True)

    def update_view(self):
        self.view_count += 1


class UserSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ('email', 'first_name', 'last_name', 'view_count', 'is_valid')
        model = User
        model_build_obj = True
