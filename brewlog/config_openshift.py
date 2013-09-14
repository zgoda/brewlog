import os

PROPAGATE_EXCEPTIONS = True

MYSQL_HOST = os.environ['OPENSHIFT_MYSQL_DB_HOST']
MYSQL_PORT = os.environ['OPENSHIFT_MYSQL_DB_PORT']
MYSQL_USER_NAME = 'brewlog'
MYSQL_PASSWORD = 'brewlog'
MYSQL_DB_NAME = 'brewlog'

SQLALCHEMY_DATABASE_URI = 'mysql://%(MYSQL_USER_NAME)s:%(MYSQL_PASSWORD)s@%(MYSQL_HOST)s:%(MYSQL_PORT)s/%(MYSQL_DB_NAME)s?charset=utf8' % locals()
PROD_SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI

UPLOAD_DIR = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'uploads')
