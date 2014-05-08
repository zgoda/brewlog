import unittest

from flask.ext.script import Server, Manager, Shell, Command, Option

from brewlog import make_app
from brewlog.db import init_db, clear_db


class RunTests(Command):

    option_list = (
        Option(
            'labels', nargs='*',
            help='specify individual tests to be run, in form module_name[.TestCaseName[.test_method]]'
        ),
        Option('-v', '--verbosity', type=int, default=1)
    )

    def __init__(self, testdir='', pattern='test_*.py'):
        self.dirparts = testdir.split('/')
        self.test_pattern = pattern

    def run(self, labels, verbosity):
        if labels:
            prefix = '.'.join(self.dirparts)
            if prefix:
                names = ['%s.%s' % (prefix, name) for name in labels]
            else:
                names = labels
            suite = unittest.TestLoader().loadTestsFromNames(names)
        else:
            if self.dirparts:
                testdir = '/'.join(self.dirparts)
            else:
                testdir = '.'
            suite = unittest.TestLoader().discover(testdir, pattern=self.test_pattern)
        unittest.TextTestRunner(verbosity=verbosity).run(suite)


manager = Manager(make_app)
manager.add_option('-e', '--env', dest='env', default='dev')

manager.add_command('runserver', Server(port=8080))
manager.add_command('shell', Shell())
manager.add_command('test', RunTests(testdir='brewlog/tests'))


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
