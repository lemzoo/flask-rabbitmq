from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restful import Api

from app.view import api

app = Flask(__name__)
api.init_app(app)

api = Api(app)

# Load the default configuration
app.config.from_pyfile('default-config.cfg')

db = MongoEngine(app)


if __name__ == "__main__":
    app.run(debug=True)
