import os
from flask import Flask

from .models import db, Invite, RSVP
import rsvp


class DefaultConfig(object):
    DEBUG = False
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    MANDRILL_API_KEY = ''
    RSVP_PREFIX = '/rsvp'
    NOTIFY_EMAILS = []
    STATIC_URL_PATH = '/static'

class TestConfig(DefaultConfig):
    DEBUG = True
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class ProductionConfig(DefaultConfig):
    RSVP_PREFIX='/'
    STATIC_URL_PATH='/'



def create_app(config=None):

    app = Flask(__name__)
    app.config.from_object(config)
    if 'WEDDING_CONFIG' in os.environ:
        app.config.from_envvar('WEDDING_CONFIG')

    db.init_app(app)
    db.create_all(app=app)
    from ournewballandchain.rsvp import rsvp as rsvp_blueprint

    rsvp_prefix = app.config['RSVP_PREFIX']
    if 'STATIC_URL_PATH' in app.config:
        rsvp_blueprint.static_url_path = app.config['STATIC_URL_PATH']
        app.static_url_path = app.config['STATIC_URL_PATH']
    else:
        rsvp_blueprint.static_url_path='/static'
    app.register_blueprint(rsvp_blueprint, url_prefix=rsvp_prefix)


    return app