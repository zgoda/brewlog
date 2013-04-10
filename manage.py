from flask.ext.script import Server, Manager, Shell

from brewlog import app


manager = Manager(app)
manager.add_command('runserver', Server(port=8080))
manager.add_command('shell', Shell())

if __name__ == '__main__':
    manager.run()
