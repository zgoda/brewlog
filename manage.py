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

if __name__ == '__main__':
    manager.run()
