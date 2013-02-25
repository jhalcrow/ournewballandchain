import os
from flask import Flask
from .models import db
from ournewballandchain.rsvp import rsvp


class DefaultConfig(object):
    DEBUG = False
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'

class TestConfig(DefaultConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


def create_app(config=None):

    app = Flask(__name__)
    app.config.from_object('ournewballandchain.DefaultConfig')
    app.config.from_envvar('WEDDING_CONFIG')
    if config:
        app.config.from_object(config)

    db.init_app(app)
    db.create_all(app=app)

    app.register_blueprint(rsvp)

    return app