import os
class Config(object):
    DEBUG = False

    SECRET_KEY = os.environ['SECRET_KEY']
    BASE_URL = 'http://localhost:5001'

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(DevelopmentConfig):
    TESTING = True
