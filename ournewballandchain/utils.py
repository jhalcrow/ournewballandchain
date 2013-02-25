from flask import current_app
from .models import Invite

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

def lookup_invite(name, code):
    '''
    Looks up an invite based on a name and an rsvp code. If code is provided
    we try to match based on that first, but if there's no match found that
    way we fall back on matching by name.
    '''
    if code:
        invite = Invite.query.filter_by(rsvp_code=code).first()
        if invite:
            return invite
        else:
            current_app.logger.warning('%s used code %s, but it is invalid' % (name, code))
    else:
        name_matches = Invite.query.filter(Invite.name.ilike('%' + name + '%')).all()
        if name_matches and len(name_matches) == 1:
            return name_matches[1]
        else:
            current_app.logger.warning('Unable to find match for %s' % name)

def send_thanks(email):
    pass


def rsvp_notify(rsvp, invite):
    '''
    Sends an email about someone RSVPing
    '''
    if rsvp.email:
        send_thanks(rsvp.email)
 