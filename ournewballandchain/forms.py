from flask.ext.wtf import Form, TextField, Required, BooleanField, IntegerField, ValidationError
from flask.ext.wtf.html5 import EmailField, IntegerRangeField

class RSVPForm(Form):
    email = EmailField("Email (if you want to get updates from us)")
    attending = BooleanField("Attending", validators=[Required()])
    guests = IntegerField("Number of Guests (including yourself)")
    note = TextField("Anything you'd like to add")

    def validate_guests(form, field):
        if field.data >= 10:
            raise ValidationError(
                '''Sorry, that's too many people.
                Contact Kate or Jonathan if you really want to bring %s guests'''
                 % field.data)
        if form.attending.data and field.data <= 0:
            raise ValidationError('Please enter the number of people attending including yourself.')


class RSVPFreeForm(RSVPForm):
    name = TextField("Name", validators=[Required()])
 
