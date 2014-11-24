import os
from flask import Flask
from flask_oauthlib.client import OAuth

#app
app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))
oauth = OAuth(app)

from fishing import views
