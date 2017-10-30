from flask import Flask
from flask.ext.mongoengine import mongoengine
from flask_mongoengine import MongoEngine
from flask import request, abort

import json


app = Flask(__name__)

# Load the default configuration
app.config.from_pyfile('default-config.cfg')

db = MongoEngine(app)


@app.route('/user/<string:email>', methods=['GET'])
def get(email):
    user = User.objects.get_or_404(email=email)
    return json.dumps({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    })


@app.route('/user', methods=['POST'])
def post():
    payload = request.get_json()
    user = User(
        email=payload['email'],
        first_name=payload['first_name'],
        last_name=payload['last_name'])
    try:
        user.save()
    except Exception as error:
        abort(400, str(error))
    return user.email


class User(db.Document):
    email = db.StringField(required=True, unique=True)
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

    def save_or_abort(self, abort=abort, if_match=None):
        try:
            if if_match is True:
                self.document.save(
                    save_condition={"doc_version": self.document.doc_version})
            elif if_match:
                self.document.save(save_condition={"doc_version": if_match})
            else:
                self.document.save()
        except mongoengine.ValidationError as exc:
            errors = exc.to_dict()
            if errors:
                # ValidationErrors issued in the clean function are wrapped
                # in a useless NON_FIELD_ERRORS
                non_field_errors = errors.pop(
                    mongoengine.base.NON_FIELD_ERRORS, {})
                if isinstance(non_field_errors, dict):
                    errors.update(non_field_errors)
                    abort(400, **errors)
                else:
                    abort(400, non_field_errors)
            else:
                abort(400, exc.message)
        except mongoengine.errors.NotUniqueError as exc:
            abort(400, parse_error_e11000(exc))
        except mongoengine.errors.FieldDoesNotExist as exc:
            abort(400, str(exc))


if __name__ == "__main__":
    app.run(debug=True)
