import os

from werkzeug.utils import ImportStringError
from flask import Flask, render_template, session, request, send_from_directory
from flask_babelex import gettext as _

from .ext import login_manager, babel, pages, db, csrf, bootstrap
from .templates import setup_template_extensions


def make_app(env):
    app = Flask(__name__)
    configure_app(app, env)
    configure_hooks(app, env)
    configure_blueprints(app, env)
    configure_extensions(app, env)
    configure_logging(app, env)
    configure_error_handlers(app, env)
    setup_template_extensions(app)
    return app


def configure_app(app, env):
    app.config.from_object('brewlog.config')
    env_config = 'brewlog.config_%s' % env
    try:
        app.config.from_object(env_config)
    except ImportStringError:
        # no special configuration for this environment
        pass
    if os.environ.get('BREWLOG_CONFIG', ''):
        app.config.from_envvar('BREWLOG_CONFIG')
    if app.config['DEBUG']:
        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(os.path.join(app.root_path, 'static'),
                'favicon.ico', mimetype='image/vnd.microsoft.icon')


def configure_hooks(app, env):
    @app.context_processor
    def inject():
        return {
            'DEV': app.config['DEBUG'],
            'TESTING': app.config['TESTING'],
        }


def configure_blueprints(app, env):
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


def configure_extensions(app, env):
    db.init_app(app)

    csrf.init_app(app)

    bootstrap.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.select'
    login_manager.login_message = _('Please log in to access this page')
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def get_user(userid):
        from models.users import BrewerProfile
        return BrewerProfile.query.get(userid)

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


def configure_logging(app, env):
    pass


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
