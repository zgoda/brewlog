import os
from logging.config import dictConfig
from typing import Optional

from flask import render_template, send_from_directory
from werkzeug.utils import ImportStringError

from .assets import all_css, all_js
from .auth import auth_bp
from .brew import brew_bp
from .brewery import brewery_bp
from .ext import (
    assets, babel, csrf, db, huey, login_manager, migrate, pages,
)
from .fermentation import ferm_bp
from .home import home_bp
from .profile import profile_bp
from .tasks import send_email  # noqa: F401
from .tasting import tasting_bp
from .templates import setup_template_extensions
from .utils.app import Brewlog


def make_app(env: Optional[str] = None) -> Brewlog:
    if os.environ.get('FLASK_ENV') == 'production':
        configure_logging()
    extra = {}
    extra.update({
        'instance_path': os.getenv('INSTANCE_PATH'),
    })
    app = Brewlog(**extra)
    configure_app(app, env)
    configure_extensions(app)
    with app.app_context():
        configure_assets(app)
        configure_blueprints(app)
        configure_error_handlers(app)
        setup_template_extensions(app)
    return app


def configure_app(app: Brewlog, env: Optional[str] = None):
    app.config.from_object('brewlog.config')
    if env is not None:
        try:
            app.config.from_object(f'brewlog.config_{env}')
        except ImportStringError:
            pass
    if app.debug or app.testing:
        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(
                os.path.join(app.root_path, 'static'),
                'favicon.ico',
                mimetype='image/vnd.microsoft.icon',
            )
        huey.immediate = True


def configure_blueprints(app: Brewlog):
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(brewery_bp, url_prefix='/brewery')
    app.register_blueprint(brew_bp, url_prefix='/brew')
    app.register_blueprint(tasting_bp, url_prefix='/tastingnote')
    app.register_blueprint(ferm_bp, url_prefix='/ferm')


def configure_extensions(app: Brewlog):
    db.init_app(app)
    migrate.init_app(app, db)
    assets.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.select'
    login_manager.login_message = 'Zaloguj się by otworzyć tę stronę'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def get_user(user_id):
        from .models.users import BrewerProfile
        return BrewerProfile.query.get(user_id)

    babel.init_app(app)

    pages.init_app(app)


def configure_assets(app: Brewlog):
    bundles = {
        'css_all': all_css,
        'js_all': all_js,
    }
    assets.register(bundles)


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


def configure_error_handlers(app: Brewlog):
    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500
