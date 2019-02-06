import os

__basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

DEBUG = True

PG_HOST = 'localhost'
PG_USER_NAME = 'brewlog'
PG_PASSWORD = 'brewlog'
PG_DB_NAME = 'brewlog'

# SQLALCHEMY_DATABASE_URI = 'postgresql://%(PG_USER_NAME)s:%(PG_PASSWORD)s@%(PG_HOST)s/%(PG_DB_NAME)s' % locals()

SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.abspath(os.path.join(__basedir, 'db.sqlite3'))
