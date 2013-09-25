import os

from werkzeug.utils import ImportStringError
from flask import Flask, render_template, get_flashed_messages
from flask_babel import Babel, gettext as _, format_date
from flask_login import LoginManager, current_user
from flask_mail import Mail

from brewlog.db import init_engine, session
from brewlog.templates import setup_template_extensions
from brewlog.urls import rules


login_manager = LoginManager()
babel = Babel()
mail = Mail()

def make_app(env):
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
        session.remove()

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.context_processor
    def inject():
        return {
            'DEV': app.config['DEBUG'],
            'user': current_user,
            'flashes': get_flashed_messages(),
        }

    login_manager.init_app(app)
    login_manager.login_view = 'auth-select-provider'
    login_manager.login_message = _('Please log in to access this page')
    login_manager.login_message_category = 'info'
    babel.init_app(app)
    mail.init_app(app)
    
    rules.register(app)

    setup_template_extensions(app)

    return app


@login_manager.user_loader
def get_user(userid):
    from models import BrewerProfile
    return BrewerProfile.query.get(userid)

