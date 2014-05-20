import os

from werkzeug.utils import ImportStringError
from flask import Flask, render_template, get_flashed_messages, session, request
from flask.ext.babel import Babel, gettext as _
from flask.ext.login import LoginManager, current_user
from flask.ext.flatpages import FlatPages

from brewlog.db import init_engine, session as dbsession
from brewlog.templates import setup_template_extensions
from brewlog.routes import routes


login_manager = LoginManager()
babel = Babel()
pages = FlatPages()


def make_app(env):  # pragma: no cover
    app = Flask(__name__)
    app.config.from_object('brewlog.config')
    env_config = 'brewlog.config_%s' % env
    try:
        app.config.from_object(env_config)
    except ImportStringError:
        # no special configuration for this environment
        pass
    if os.environ.get('BREWLOG_CONFIG', ''):
        app.config.from_evvar('BREWLOG_CONFIG')
    init_engine(app.config['%s_SQLALCHEMY_DATABASE_URI' % env.upper()])

    @app.teardown_request
    def shutdown_session(exception=None):
        dbsession.remove()

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.context_processor
    def inject():
        return {
            'DEV': app.config['DEBUG'],
            'TESTING': app.config['TESTING'],
            'user': current_user,
            'flashes': get_flashed_messages(with_categories=True),
        }

    login_manager.init_app(app)
    login_manager.login_view = 'auth-select-provider'
    login_manager.login_message = _('Please log in to access this page')
    login_manager.login_message_category = 'warning'

    babel.init_app(app)

    @babel.localeselector
    def get_locale():
        lang = session.get('lang')
        if lang is None:
            lang = request.accept_languages.best_match(['pl', 'en'])
        return lang

    pages.init_app(app)
    pages.get('foo')  # preload all static pages

    routes.register(app)

    setup_template_extensions(app)

    return app


@login_manager.user_loader
def get_user(userid):
    import models.calendar
    from models.users import BrewerProfile
    return BrewerProfile.query.get(userid)
