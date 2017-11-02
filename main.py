from os.path import abspath, dirname

from flask import Flask
from flask_mongoengine import MongoEngine


class CoreApp(Flask):
    """
    CoreApp is a regular :class:`Flask` app
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_path = abspath(dirname(__file__) + '/..')
        self.db = MongoEngine()

    def bootstrap(self):
        self.db.init_app(self)


def create_app(config=None):
    """
    Build the app build don't initilize it, useful to get back the default
    app config, correct it, then call ``bootstrap_app`` with the new config
    """
    app = CoreApp(__name__)

    if config:
        app.config.update(config)
    app.config.from_pyfile('default-config.cfg')

    return app


def bootstrap_app(app=None, config=None):
    """
    Create and initilize the sief app
    """

    if not app:
        app = create_app(config)
    elif config:
        app.config.update(config)

    from app.view import api

    app.bootstrap()

    api.prefix = app.config['API_PREFIX']
    api.init_app(app)

    return app
