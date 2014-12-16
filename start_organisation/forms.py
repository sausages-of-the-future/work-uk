import json
from wtforms import Form, TextField, TextAreaField, RadioField, DateField, validators

class StartOrganisationTypeForm(Form):
    organisation_type = RadioField('Organisation type', choices=[], validators=[validators.required()])

class StartOrganisationDetailsForm(Form):
    name = TextField('Organisation name', validators=[validators.required()])
    activities = TextAreaField('Main business activities', validators=[validators.required()])
