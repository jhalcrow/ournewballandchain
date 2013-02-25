from flask import request, redirect, url_for, render_template, flash, Blueprint
from .forms import RSVPForm, RSVPFreeForm
from .models import RSVP, Invite

rsvp = Blueprint('rsvp', __name__, template_folder='templates')

@rsvp.route('/rsvp', methods=['GET', 'POST'])
def rsvp_form():
    form = RSVPFreeForm()
    if form.validate_on_submit():
        app.logger.info('RSVP for %s from %s, attending: %s guests: %s' % 
            (form.name.data, request.remote_addr, form.attending.data, form.guests.data)
        )

        rsvp = RSVP(
                entered_name=form.name.data,
                email=form.email.data,
                entered_code=form.rsvp_code.data,
                guests=form.guests.data,
                attending=form.attending.data,
                timestamp=datetime.datetime.utcnow(),
                qr_used=False
                )
        iv = lookup_invite(form.name.data, form.rsvp_code.data)
        if iv:
            app.logger.info('Invite matched, entry of %s for %s', form.name.data, iv.name)
            rsvp.invite_id = iv.id

        db.session.add(rsvp)
        db.session.commit()

        app.logger.info('RSVP by %s', rsvp.name)
        rsvp_notify(rsvp, invite)
        return redirect('/static/rsvp_success.html')

    return render_template('rsvp_form.html', form=form)

@rsvp.route('/rsvp/<code>', methods=['GET'])
def rsvp_prefill(code):
    form = RSVPForm()
    iv = Invite.query.filter_by(rsvp_code=code).first()
    if not iv:
        app.logger.info("Unable to find invite for code %s", code)
        flash("Sorry, unable to locate your RSVP. Please try this form instead.")
        return redirect(url_for('rsvp_form'))
    if form.validate_on_submit():
        rsvp = RSVP(
            email=form.email.data,
            entered_code=code,
            guests=form.guests.data,
            attending=form.attending.data,
            timestamp=datetime.datetime.utcnow(),
            invite_id=iv.id,
            qr_used=True
            )
        db.session.add(rsvp)
        db.session.commit()

        app.logger.info("QR RSVP by %s", iv.name)
        rsvp_notify(rsvp, invite)
        return redirect('/static/rsvp_success.html')

    return render_template('rsvp_form_prefill.html', form=form, invite=iv)
   