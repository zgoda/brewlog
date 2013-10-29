import os

PROPAGATE_EXCEPTIONS = True

PG_HOST = os.environ['OPENSHIFT_POSTGRESQL_DB_HOST']
PG_PORT = os.environ['OPENSHIFT_POSTGRESQL_DB_PORT']
PG_USER_NAME = os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME']
PG_PASSWORD = os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD']
PG_DB_NAME = 'brewlog'

SQLALCHEMY_DATABASE_URI = 'postgresql://%(PG_USER_NAME)s:%(PG_PASSWORD)s@%(PG_HOST)s:%(PG_PORT)s/%(PG_DB_NAME)s' % locals()
PROD_SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI

UPLOAD_DIR = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'uploads')
