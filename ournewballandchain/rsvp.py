import datetime

from flask import request, redirect, url_for, render_template, flash, Blueprint, current_app as app
from .forms import RSVPForm, RSVPFreeForm
from .models import RSVP, Invite, db
from .utils import rsvp_notify


rsvp = Blueprint('rsvp', __name__, template_folder='templates', static_folder='static')

@rsvp.route('/form', methods=['GET', 'POST'])
def rsvp_form():
    invite = None

    code = request.args.get('code')
    qr_used = 'qr_used' in request.args
    
    if code:
        invite = Invite.query.filter_by(rsvp_code=code).first()

    form = RSVPForm() if invite else RSVPFreeForm()

    if form.validate_on_submit():
        name = invite.name if invite else form.name.data

        app.logger.info('RSVP for %s from %s, attending: %s guests: %s' % 
            (name, request.remote_addr, form.attending.data, form.guests.data)
        )

        rsvp = RSVP(
                name=name,
                invite_id=invite.id if invite else None,
                email=form.email.data,
                guests=form.guests.data,
                guest_names=form.guest_names.data,
                attending=form.attending.data,
                timestamp=datetime.datetime.utcnow(),
                note=form.note.data,
                code_used='code' in request.args,
                qr_used=qr_used
        )
        db.session.add(rsvp)
        db.session.commit()

        app.logger.info('RSVP by %s', rsvp.name)
        rsvp_notify(rsvp, app.config['MANDRILL_API_KEY'], app.config['NOTIFY_EMAILS'])
        return redirect(url_for('.static', filename='rsvp_success.html'))

    template = 'rsvp_form_prefill.html' if invite else 'rsvp_form.html'
    return render_template(template, invite=invite, form=form,
        header_file=url_for('.static', filename='img/rsvp_banner.png'))
