import os

from brewlog.config.base import Config

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'brewlog.db')

class DevConfig(Config):
    DEBUG = True
    DATABASE_URI = 'sqlite://%s' % DB_PATH
