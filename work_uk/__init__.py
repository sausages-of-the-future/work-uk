import os
from flask import Flask
from flask_oauthlib.client import OAuth
from flask.ext.cors import CORS

#app
app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))
oauth = OAuth(app)

from work_uk import views
