from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entered_name = db.Column(db.String)
    email = db.Column(db.String(120))
    entered_code = db.Column(db.Boolean)
    guests = db.Column(db.Integer)
    attending = db.Column(db.Boolean, default=False)
    invite_id = db.Column(db.Integer, db.ForeignKey('invite.id'))
    timestamp = db.Column(db.DateTime)
    qr_used = db.Column(db.Boolean)

class Invite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    rsvp_code = db.Column(db.String, unique=True)

    rsvps = db.relationship('RSVP', backref='invite')


