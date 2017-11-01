from flask_marshmallow import Schema
from flask_mongoengine import Document
from mongoengine import EmbeddedDocument
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


class Content(EmbeddedDocument):
    text = fields.StringField()
    lang = fields.StringField(max_length=3)


class Post(Document):
    title = fields.StringField(max_length=120, required=True)
    author = fields.ReferenceField(User)
    tags = fields.ListField(fields.StringField(max_length=30))
    content = fields.EmbeddedDocumentField(Content)
