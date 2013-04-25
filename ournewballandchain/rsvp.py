import datetime

from flask import request, redirect, url_for, render_template, flash, Blueprint, current_app as app
from .forms import RSVPForm, RSVPFreeForm
from .models import RSVP, Invite, db
from .utils import rsvp_notify


rsvp = Blueprint('rsvp', __name__, template_folder='templates', static_folder='static')

@rsvp.route('/rsvp/', methods=['GET', 'POST'])
def rsvp_form():
    form = RSVPFreeForm()
    if form.validate_on_submit():
        app.logger.info('RSVP for %s from %s, attending: %s guests: %s' % 
            (form.name.data, request.remote_addr, form.attending.data, form.guests.data)
        )

        rsvp = RSVP(
                name=form.name.data,
                email=form.email.data,
                guests=form.guests.data,
                guest_names=form.guest_names.data,
                attending=form.attending.data,
                timestamp=datetime.datetime.utcnow(),
                note=form.note.data,
                code_used=False,
                qr_used=False
        )
        db.session.add(rsvp)
        db.session.commit()

        app.logger.info('Regular RSVP by %s', rsvp.name)
        rsvp_notify(rsvp, app.config['MANDRILL_API_KEY'], app.config['NOTIFY_EMAILS'])
        return redirect(url_for('.static', filename='rsvp_success.html'))

    return render_template('rsvp_form.html', form=form, header_file=url_for('.static', filename='img/rsvp_banner.png'))

@rsvp.route('/rsvp/<code>', methods=['GET', 'POST'])
def rsvp_prefill(code):
    qr_used = 'qr_used' in request.args

    form = RSVPForm()
    invite = Invite.query.filter_by(rsvp_code=code).first()

    if not invite:
        app.logger.warning("Unable to find invite for code %s", code)
        return redirect(url_for('.rsvp_form'))
    if form.validate_on_submit():
        rsvp = RSVP(
            name=invite.name,
            email=form.email.data,
            guests=form.guests.data,
            guest_names=form.guest_names.data,
            attending=form.attending.data,
            timestamp=datetime.datetime.utcnow(),
            invite_id=invite.id,
            note=form.note.data,
            code_used=True,
            qr_used=qr_used
        )
        db.session.add(rsvp)
        db.session.commit()

        app.logger.info("QR RSVP by %s", invite.name)
        rsvp_notify(rsvp, app.config['MANDRILL_API_KEY'], app.config['NOTIFY_EMAILS'])
        return redirect(url_for('.static', filename='rsvp_success.html'))

    return render_template('rsvp_form_prefill.html', form=form, invite=invite, header_file=url_for('.static', filename='img/rsvp_banner.png'))
   