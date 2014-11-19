from flask import Flask
from flask_oauthlib.client import OAuth

#app
app = Flask(__name__)
app.config.from_object('config')
oauth = OAuth(app)

from fishing import views
