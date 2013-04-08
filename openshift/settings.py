import os

MYSQL_HOST = os.environ['OPENSHIFT_MYSQL_DB_HOST']
MYSQL_PORT = os.environ['OPENSHIFT_MYSQL_DB_PORT']
MYSQL_ROOT_USERNAME = os.environ['OPENSHIFT_MYSQL_DB_USERNAME']
MYSQL_USER_NAME = 'brewlog'
MYSQL_ROOT_PASSWORD = os.environ['OPENSHIFT_MYSQL_DB_PASSWORD']
MYSQL_PASSWORD = 'brewlog'
MYSQL_DATABASE_NAME = 'brewlog'
MYSQL_DB_URI = 'mysql://%(MYSQL_PASSWORD)s:%(MYSQL_USER_NAME)s@%(MYSQL_HOST)s:%(MYSQL_PORT)s/%(MYSQL_DATABASE_NAME)s' % locals()
