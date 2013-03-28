import datetime

from flask import request, redirect, url_for, render_template, flash, Blueprint, current_app as app
from .forms import RSVPForm, RSVPFreeForm
from .models import RSVP, Invite, db
from .utils import rsvp_notify


rsvp = Blueprint('rsvp', __name__, template_folder='templates')

@rsvp.route('/rsvp', methods=['GET', 'POST'])
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
                attending=form.attending.data,
                timestamp=datetime.datetime.utcnow(),
                note=form.note.data,
                qr_used=False
        )
        db.session.add(rsvp)
        db.session.commit()

        app.logger.info('Regular RSVP by %s', rsvp.name)
        rsvp_notify(rsvp, None)
        return redirect('/static/rsvp_success.html')

    return render_template('rsvp_form.html', form=form)

@rsvp.route('/rsvp/<code>', methods=['GET', 'POST'])
def rsvp_prefill(code):
    form = RSVPForm()
    invite = Invite.query.filter_by(rsvp_code=code).first()
    if not invite:
        app.logger.info("Unable to find invite for code %s", code)
        flash("Sorry, unable to locate your RSVP. Please try this form instead.")
        return redirect(url_for('.rsvp_form'))
    if form.validate_on_submit():
        rsvp = RSVP(
            email=form.email.data,
            guests=form.guests.data,
            attending=form.attending.data,
            timestamp=datetime.datetime.utcnow(),
            invite_id=invite.id,
            note=form.note.data,
            qr_used=True
        )
        db.session.add(rsvp)
        db.session.commit()

        app.logger.info("QR RSVP by %s", invite.name)
        rsvp_notify(rsvp, invite)
        return redirect('/static/rsvp_success.html')

    return render_template('rsvp_form_prefill.html', form=form, invite=invite)
   