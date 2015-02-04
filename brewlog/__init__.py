import os

from werkzeug.utils import ImportStringError
from flask import Flask, render_template, get_flashed_messages, session, request
from flask_babelex import Babel, gettext as _
from flask_login import LoginManager, current_user
from flask_flatpages import FlatPages
from flask_sqlalchemy import SQLAlchemy

from brewlog.templates import setup_template_extensions


login_manager = LoginManager()
babel = Babel()
pages = FlatPages()
db = SQLAlchemy()


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

    db.init_app(app)

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
    login_manager.login_view = 'auth.select'
    login_manager.login_message = _('Please log in to access this page')
    login_manager.login_message_category = 'warning'

    if not app.testing:
        @babel.localeselector
        def get_locale():
            lang = session.get('lang')
            if lang is None:
                lang = request.accept_languages.best_match(['pl', 'en'])
            return lang

    babel.init_app(app)

    pages.init_app(app)
    pages.get('foo')  # preload all static pages

    from brewlog.auth.providers import oauth
    oauth.init_app(app)

    # register blueprints
    from brewlog.home import home_bp
    app.register_blueprint(home_bp)
    from brewlog.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from brewlog.profile import profile_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')
    from brewlog.brewery import brewery_bp
    app.register_blueprint(brewery_bp, url_prefix='/brewery')
    from brewlog.brew import brew_bp
    app.register_blueprint(brew_bp, url_prefix='/brew')
    from brewlog.tasting import tasting_bp
    app.register_blueprint(tasting_bp, url_prefix='/tastingnote')

    setup_template_extensions(app)

    return app


@login_manager.user_loader
def get_user(userid):
    from models.users import BrewerProfile
    return BrewerProfile.query.get(userid)
