from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String(254))
    guests = db.Column(db.Integer)
    guest_names = db.Column(db.String)
    attending = db.Column(db.Boolean, default=False)
    note = db.Column(db.String)
    invite_id = db.Column(db.Integer, db.ForeignKey('invite.id'))
    timestamp = db.Column(db.DateTime)
    qr_used = db.Column(db.Boolean)
    code_used = db.Column(db.Boolean)

class Invite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    rsvp_code = db.Column(db.String, unique=True)
    rsvps = db.relationship('RSVP', backref='invite')


