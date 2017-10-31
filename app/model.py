from flask_mongoengine import Document
from mongoengine import EmbeddedDocument
from mongoengine import fields


class User(Document):
    email = fields.StringField(required=True, unique=True)
    first_name = fields.StringField(max_length=50)
    last_name = fields.StringField(max_length=50)


class Content(EmbeddedDocument):
    text = fields.StringField()
    lang = fields.StringField(max_length=3)


class Post(Document):
    title = fields.StringField(max_length=120, required=True)
    author = fields.ReferenceField(User)
    tags = fields.ListField(fields.StringField(max_length=30))
    content = fields.EmbeddedDocumentField(Content)
