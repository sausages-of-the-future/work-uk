import json
from wtforms import Form, TextField, RadioField, DateField, validators

class StartOrganisationForm(Form):
    organisation_type = RadioField('Organisation type', choices=[], validators=[validators.required()])
    name = TextField(validators=[validators.required()])

