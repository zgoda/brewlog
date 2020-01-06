from flask.cli import FlaskGroup
from dotenv import load_dotenv, find_dotenv

from . import make_app
from .ext import db


def create_app(info):
    return make_app('dev')


cli = FlaskGroup(create_app=create_app)
cli.help = 'This is a management script for the Brewlog application.'


@cli.command('initdb', short_help='Initialize missing database objects')
def initdb():
    db.create_all()


@cli.command('cleardb', short_help='Remove all database objects')
def cleardb():
    db.drop_all()


@cli.command('recreatedb', short_help='Recreate all database objects from scratch')
def recreatedb():
    db.drop_all()
    db.create_all()


def main():
    load_dotenv(find_dotenv())
    cli()
