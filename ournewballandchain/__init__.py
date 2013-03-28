import os
from flask import Flask

from .models import db, Invite, RSVP
import rsvp


class DefaultConfig(object):
    DEBUG = False
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'

class TestConfig(DefaultConfig):
    DEBUG = True
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


def create_app(config=None):

    app = Flask(__name__)
    app.config.from_object(config)
    if 'WEDDING_CONFIG' in os.environ:
        app.config.from_envvar('WEDDING_CONFIG')

    db.init_app(app)
    db.create_all(app=app)
    from ournewballandchain.rsvp import rsvp as rsvp_blueprint
    app.register_blueprint(rsvp_blueprint)

    return app