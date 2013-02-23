from flask import Flask, request, redirect, url_for, render_template
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

db = SQLAlchemy(app)

class Invite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String(120), unique=True)
    rsvp_code = db.Column(db.String, unique=True)
    guests = db.Column(db.Integer)
    rsvped = db.Column(db.Boolean, default=False)



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


@app.route('/rsvp', methods=['GET'])
def rsvp_form():
    return render_template('rsvp_form.html')

@app.route('/rsvp', methods=['POST'])
def rsvp():
    app.logger.info("WTF")
    name = request.form['NAME']
    email = request.form['EMAIL']
    guests = int(request.form['GUESTS'])
    rsvp_code = None # request.form['CODE']
    attending = request.form['ATTENDING']

    iv = None
    if not rsvp_code and not name:
        flash("Please enter your name or RSVP code.")
    if not guests:
        flash("Please enter the number of guests (including yourself).")

    if rsvp_code:
        iv = Invite.query.filter_by(id=rsvp_code)
    else:
        similar = [iv for iv in Invite.query.all() 
                if edit_distance(iv.name, name) < cutoff]
        similar.sort(key=lambda iv: edit_distance(iv.name, name))

        if similar and similar[0].name == name:
            iv = similar[0]
        if name and len(similar) > 0:
            flash("Unable to find you on the list, please try again or contact Jonathan or Kate.")
    
    if not iv or not guests:
        return redirect(url_for('rsvp_form'))

    flash("Thank you for your RSVP.")
    app.logger.info('RSVP for %s from %s' % (iv.name, request.remote_addr))
    rsvp = RSVP(invite_id = iv.id, guests=guests, note=request.form('NOTE'))
    db.session.add(rsvp)
    db.session.commit()

@app.route('/rsvp/<code>', methods=['GET'])
def rsvp_prefill(code):
    iv = Invite.query.filter_by(rsvp_code=code)
    if not iv:
        flash("Sorry, unable to locate your RSVP. Please try this form instead.")
        return redirect(url_for('rsvp_form'))

    return render_template('rsvp_form_prefill.html', invite=iv)
    


if __name__== '__main__':

    db.create_all()
    app.run(debug =True)







