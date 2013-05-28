import os

from flask.ext.script import Server, Manager, Shell

from brewlog import app


manager = Manager(app)

manager.add_command('runserver', Server(port=8080))

manager.add_command('shell', Shell())

@manager.command
def initdb():
    "Initialize empty database if does not exist"
    import brewlog
    brewlog.init_db()

@manager.command
def cleardb():
    "Clear all database tables"
    import brewlog
    brewlog.clear_db()

@manager.command
def test():
    here = os.path.abspath(os.path.dirname(__file__))
    testing_cfg = os.path.join(here, 'brewlog', 'config_testing.py')
    app.config.from_pyfile(testing_cfg)
    import unittest
    #print 'tests disabled until ready'
    suite = unittest.TestLoader().discover('brewlog/tests', pattern='test_*.py')
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    manager.run()
