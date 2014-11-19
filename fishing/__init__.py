from flask import Flask
from flask_oauthlib.client import OAuth
from flask.ext.qrcode import QRcode

#app
app = Flask(__name__)
app.config.from_object('config')
oauth = OAuth(app)
QRcode(app)

from fishing import views
