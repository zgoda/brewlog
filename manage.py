import os
import unittest

from flask.ext.script import Server, Manager, Shell, Command, Option

from brewlog import make_app
from brewlog.db import init_db, clear_db


class TestCommand(Command):

    option_list = (
        Option('labels', nargs='*',
            help='specify individual tests to be run, in form module_name[.TestCaseName[.test_method]]'),
    )

    def run(self, labels):
        if labels:
            names = ['brewlog.tests.%s' % name for name in labels]
            suite = unittest.TestLoader().loadTestsFromNames(names)
        else:
            suite = unittest.TestLoader().discover('brewlog/tests', pattern='test_*.py')
        unittest.TextTestRunner(verbosity=2).run(suite)


manager = Manager(make_app)
manager.add_option('-e', '--env', dest='env', default='dev')

manager.add_command('runserver', Server(port=8080))

manager.add_command('shell', Shell())

manager.add_command('test', TestCommand())

@manager.command
def initdb():
    "Initialize empty database if does not exist"
    init_db()

@manager.command
def cleardb():
    "Clear all database tables"
    clear_db()

if __name__ == '__main__':
    manager.run()
