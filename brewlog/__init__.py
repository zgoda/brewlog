from flask import Flask, render_template, get_flashed_messages
from flaskext.babel import Babel, lazy_gettext as _
from flask_login import LoginManager, current_user
import peewee as pw


app = Flask(__name__)
app.config.from_object('brewlog.config')

# i18n
app.config['BABEL_DEFAULT_LOCALE'] = 'pl'
babel = Babel(app)

# database
db = pw.SqliteDatabase(*app.config['DB_CONNECTION_ARGS'], **app.config['DB_CONNECTION_KWARGS'])

class Model(pw.Model):

    class Meta:
        database = db

# login infrastructure
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth-select-provider'
login_manager.login_message = _('Please log in to access this page')
login_manager.login_message_category = 'info'

@login_manager.user_loader
def get_user(userid):
    from users.models import BrewerProfile
    return BrewerProfile.select().where(BrewerProfile.id == userid)

# register url map
from brewlog.urls import rules
for url, kwargs in rules:
    app.add_url_rule(url, **kwargs)


def init_db():
    from users.models import BrewerProfile
    from brewing.models import Brewery, Brew, TastingNote, AdditionalFermentationStep
    BrewerProfile.create_table()
    Brewery.create_table()
    Brew.create_table()
    TastingNote.create_table()
    AdditionalFermentationStep.create_table()


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.context_processor
def inject():
    return {
        'user': current_user,
        'flashes': get_flashed_messages(),
    }


