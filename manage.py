import os
import unittest

from flask.ext.script import Server, Manager, Shell

from brewlog import make_app
from brewlog.db import init_db, clear_db


manager = Manager(make_app)
manager.add_option('-e', '--env', dest='env', default='dev')

manager.add_command('runserver', Server(port=8080))

manager.add_command('shell', Shell())

@manager.command
def initdb():
    "Initialize empty database if does not exist"
    init_db()

@manager.command
def cleardb():
    "Clear all database tables"
    clear_db()

@manager.command
def test():
    suite = unittest.TestLoader().discover('brewlog/tests', pattern='test_*.py')
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    manager.run()
