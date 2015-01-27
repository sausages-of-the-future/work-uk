import os
from flask import Flask
from flask_oauthlib.client import OAuth

#app
app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))
oauth = OAuth(app)

from redis import Redis
import urllib
url = urllib.parse.urlparse(app.config.get('REDISCLOUD_URL', 'redis://user:@localhost:6379'))
redis_client = Redis(host=url.hostname, port=url.port, password=url.password)

from work_uk import views
