from flask import Flask, request
from flask_mongoengine import MongoEngine

from app import view

app = Flask(__name__)

# Load the default configuration
app.config.from_pyfile('default-config.cfg')

db = MongoEngine(app)


@app.route('/user/<string:email>', methods=['GET'])
def get(email):
    return view.get(email)


@app.route('/user', methods=['POST'])
def post():
    payload = request.get_json()
    return view.post(payload)


if __name__ == "__main__":
    app.run(debug=True)
