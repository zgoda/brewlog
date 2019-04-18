# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import os
from logging.config import dictConfig

from flask import render_template, request, send_from_directory, session
from flask_babel import gettext as _
from werkzeug.utils import ImportStringError

from .auth import auth_bp
from .brew import brew_bp
from .brewery import brewery_bp
from .ext import babel, bootstrap, csrf, db, login_manager, oauth, pages
from .fermentation import ferm_bp
from .home import home_bp
from .profile import profile_bp
from .tasting import tasting_bp
from .templates import setup_template_extensions
from .utils.app import Brewlog


def make_app(env=None):
    if os.environ.get('FLASK_ENV', '') != 'development':
        configure_logging()
    app = Brewlog(__name__.split('.')[0])
    configure_app(app, env)
    configure_extensions(app, env)
    with app.app_context():
        configure_blueprints(app, env)
        configure_error_handlers(app, env)
        setup_template_extensions(app)
    return app


def configure_app(app, env):
    app.config.from_object('brewlog.config')
    if env is not None:
        try:
            app.config.from_object(f'brewlog.config_{env}')
        except ImportStringError:
            pass
    config_local = os.environ.get('BREWLOG_CONFIG_LOCAL')
    if config_local:
        app.logger.info(f'local configuration loaded from {config_local}')
        app.config.from_envvar('BREWLOG_CONFIG_LOCAL')
    config_secrets = os.environ.get('BREWLOG_CONFIG_SECRETS')
    if config_secrets:
        app.logger.info(f'secrets loaded from {config_secrets}')
        app.config.from_envvar('BREWLOG_CONFIG_SECRETS')
    if app.config['DEBUG']:
        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(
                os.path.join(app.root_path, 'static'),
                'favicon.ico',
                mimetype='image/vnd.microsoft.icon',
            )


def configure_blueprints(app, env):
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(brewery_bp, url_prefix='/brewery')
    app.register_blueprint(brew_bp, url_prefix='/brew')
    app.register_blueprint(tasting_bp, url_prefix='/tastingnote')
    app.register_blueprint(ferm_bp, url_prefix='/ferm')


def configure_extensions(app, env):
    db.init_app(app)
    csrf.init_app(app)
    oauth.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.select'
    login_manager.login_message = _('Please log in to access this page')
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def get_user(user_id):
        from .models.users import BrewerProfile
        return BrewerProfile.query.get(user_id)

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


def configure_logging():
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })


def configure_error_handlers(app, env):
    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500
