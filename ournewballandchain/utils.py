import json
import logging
import requests
from flask import current_app
from .models import Invite

logger = logging.getLogger(__name__)

def edit_distance(s1, s2):
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()

    if not s1 or not s2:
        return max(len(s1), len(s2))

    scores = {(0,0) : 0}
    for i in range(1, len(s1) + 1):
        scores[i, 0] = 0
    for j in range(1, len(s2) + 1):
        scores[0, j] = 0
    for i in range(1, len(s1) + 1):
        ci = s1[i - 1]
        for j in range(1, len(s2) + 1):
            cj = s2[j - 1]
            score_up = scores[i-1, j] + 1
            score_left = scores[i, j-1] + 1
            score_swap = scores[i-1, j-1]
            if ci != cj:
                score_swap += 1
            scores[i, j] = min(score_up, score_left, score_swap)
    return scores[len(s1), len(s2)]

def lookup_invite(name):
    '''
    Looks up an invite based on a name and an rsvp code. If code is provided
    we try to match based on that first, but if there's no match found that
    way we fall back on matching by name.
    '''

    name_matches = Invite.query.filter(Invite.name.ilike('%' + name + '%')).all()
    if name_matches and len(name_matches) == 1:
        return name_matches[1]
    else:
        current_app.logger.warning('Unable to find match for %s' % name)

MANDRILL_URL = 'https://mandrillapp.com/api/1.0/'
from_email = 'rsvps@ournewballandchain.com'

def send_thanks(rsvp):
    attending_body = '''
    Thank you for filling out the RSVP form.

    We can't wait to see you June 8th!

    --Kate & Jonathan
    '''

    not_attending_body = '''
    Thank you for filling out the RSVP form.

    We're sorry that you can't make it!

    --Kate & Jonathan
    '''

def notify_us(rsvp, api_key, our_emails):
    '''
    Sends an email to us letting us know that someone has RSVPed
    '''
    attending_str = ('' if rsvp.attending else 'not ') + 'attending'
    subject = 'Wedding RSVP: %s is %s' % (rsvp.name, attending_str)
    body = '''\
Name: %(name)s
Email: %(email)s
Number of Guests: %(guests)s
Guest Names: %(guest_names)s
Note: %(note)s

QR Code Used: %(qr_used)s
Manual Code Used: %(code_used)s
    ''' % rsvp.__dict__

    mandrill_req = {
        'key': api_key,
        'message': {
            'html': body,
            'text': body,
            'subject': subject,
            'from_email': 'rsvps@ournewballandchain.com',
            'from_name': 'RSVP Robot',
            'to': [{'email': email} for email in our_emails],
        },
        'async': False
    }

    http_resp = requests.post(
        'https://mandrillapp.com/api/1.0/messages/send.json',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(mandrill_req)
    )

    resp_value = http_resp.json()
    handle_mandrill_response(resp_value)



def handle_mandrill_response(response):

    if isinstance(response, dict):
        if 'status' in response and 'name' in response and 'message' in response:
            logger.error("Error sending response %(status)s %(name)s - %(message)s", response)
        else:
            logger.error("Unexpected response from Mandrill - %s" % response)
    else:
        for resp in response:
            if '_id' not in resp or 'status' not in resp or 'email' not in resp:
                logger.error("Unexpected response from Mandrill - %s" % resp)
            elif resp['status'] in ['sent', 'queued']:
                logger.info("Notification sent to %(email)s, status: %(status)s, _id: %(_id)s" % resp)
            else:
                logger.error("Error sending to %(email)s, status: %(status)s, _id: %(_id)s", resp)


def rsvp_notify(rsvp, invite):
    '''
    Sends an email about someone RSVPing
    '''
    if rsvp.email:
        send_thanks(rsvp)
    notify_us(rsvp, invite)
 