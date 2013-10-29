"""
BrewLog, homebrewer's log application
=====================================
"""

from setuptools import setup, find_packages

setup(
    name='BrewLog',
    version='0.6',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=(
        'Babel',
        'Flask',
        'Flask-Babel',
        'Flask-Script',
        'Flask-WTF',
        'Flask-OAuth',
        'Flask-Login',
        'Flask-FlatPages',
        'PyYAML',
        'Markdown',
        'psycopg2',
        'SQLAlchemy',
        'Werkzeug',
        'itsdangerous',
        'Jinja2',
        'wtforms',
        'pytz>0a',
        'speaklater',
        'requests',
        'oauth2',
        'httplib2',
        'MarkupSafe',
        'translitcodec',
        'python-dateutil',
        'six',
        'blinker',
        'alembic',
        'mako',
        'Flask-Testing',
        'twill',
        'fixture',
    )
)

