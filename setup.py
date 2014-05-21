"""
BrewLog, homebrewer's log application
=====================================
"""

from setuptools import setup, find_packages

setup(
    name='BrewLog',
    version='0.6',
    author='Jarek Zgoda',
    author_email='jarek.zgoda@gmail.com',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='http://github.com/zgoda/brewlog',
    install_requires=(
        'Babel',
        'Flask',
        'Flask-Babel',
        'Flask-Script',
        'Flask-OAuthlib',
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
        'oauthlib',
        'MarkupSafe',
        'translitcodec',
        'python-dateutil',
        'six',
        'alembic',
        'mako',
        'Flask-Testing',
        'twill',
        'fixture',
    )
)
