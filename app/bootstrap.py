from flask import Flask
from flask_mongoengine import MongoEngine


app = Flask(__name__)

# Load the default configuration
app.config.from_pyfile('default-config.cfg')

db = MongoEngine(app)


@app.route('/user')
def get(email):
    user = User.objects.get_or_404(email=email)
    return user.email


class User(db.Document):
    email = db.StringField(required=True)
    first_name = db.StringField(max_length=50)
    last_name = db.StringField(max_length=50)


class Content(db.EmbeddedDocument):
    text = db.StringField()
    lang = db.StringField(max_length=3)


class Post(db.Document):
    title = db.StringField(max_length=120, required=True)
    author = db.ReferenceField(User)
    tags = db.ListField(db.StringField(max_length=30))
    content = db.EmbeddedDocumentField(Content)


if __name__ == "__main__":
    app.run()
