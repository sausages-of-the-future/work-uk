import wtforms
from flask_wtf import Form
from wtforms import TextField, validators

class CheckCode(Form):
    code = TextField('Enter code', validators=[validators.required()])
