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
        'Markdown',
        'MySQL-python',
        'SQLAlchemy',
        'Werkzeug',
        'itsdangerous',
        'Jinja2',
        'wtforms',
        'pytz==2013d',
        'speaklater',
        'requests',
        'oauth2',
        'httplib2',
        'MarkupSafe',
        'translitcodec',
        'alembic',
        'mako',
        'Flask-Testing',
        'twill',
        'fixture',
    )
)

