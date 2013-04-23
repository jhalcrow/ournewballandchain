from flask.ext.wtf import Form, TextField, Required, BooleanField, IntegerField, TextAreaField, ValidationError, Optional
from flask.ext.wtf.html5 import EmailField, IntegerRangeField

class RSVPForm(Form):
    email = EmailField("Email (if you want to get updates from us)")
    attending = BooleanField("Attending", default=True, validators=[Optional()])
    guests = IntegerField("Number of Guests (including yourself)", default=1, validators=[Optional()])
    guest_names = TextField("Names of your guests")
    note = TextAreaField("Anything you'd like to add")

    def validate_guests(form, field):
        if form.attending.data:
            if field.data >= 10:
                raise ValidationError(
                    '''Sorry, that's too many people.
                    Contact Kate or Jonathan if you really want to bring %s guests'''
                     % field.data)
            if not field.data or field.data <= 0:
                raise ValidationError('Please enter the number of people attending including yourself.')


class RSVPFreeForm(RSVPForm):
    name = TextField("Name", validators=[Required()])
 
