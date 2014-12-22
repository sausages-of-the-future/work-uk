import json
from wtforms import Form, TextField, TextAreaField, RadioField, DateField, validators

class StartOrganisationTypeForm(Form):
    organisaiton_types = [
        ("public-limited-company", "Public Limited Company"),
        ("private-limited-company", "Private company limited by guarantee"),
        ("ordinary-business-partnership", "Ordinary Business Partnership"),
        ("limited-partnership", "Limited Partnership"),
        ("limited-liability-partnership", "Limited Liability Partnership"),
        ("unincorperated-association", "Unincorperated Association"),
        ("charity", "Charity"),
        ("charitable-incorperated-organisation", "Charitable Incorperated Organisation"),
        ("cooperative", "Co-operative"),
        ("industrial-and-provident-society", "Industrial and Provident Society"),
        ("community-interest-company", "Community Interest Company")
    ]
    organisation_type = RadioField('Organisation type', choices=organisaiton_types, validators=[validators.required()])

class StartOrganisationDetailsForm(Form):
    name = TextField('Organisation name', validators=[validators.required()])
    activities = TextAreaField('Main business activities', validators=[validators.required()])
