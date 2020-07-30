import ast
import codecs
import re
from os import path

from setuptools import find_packages, setup

# parts below shamelessly stolen from pypa/pip
here = path.abspath(path.dirname(__file__))


def read(*parts):
    with codecs.open(path.join(here, *parts), 'r', encoding='utf-8') as fp:
        return fp.read()


_version_re = re.compile(r"__version__\s+=\s+(.*)")


def find_version(*where):
    return str(ast.literal_eval(_version_re.search(read(*where)).group(1)))


base_reqs = [
    'Flask',
    'Flask-Babel',
    'Flask-Login',
    'Flask-FlatPages',
    'Flask-SQLAlchemy',
    'WTForms!=2.3.2',
    'Flask-WTF',
    'Flask-Assets',
    'webassets-rollup',
    'Flask-Migrate',
    'Marshmallow',
    'Markdown',
    'validators',
    'permission',
    'Werkzeug',
    'itsdangerous',
    'defusedxml',
    'huey',
    'requests',
    'python-dotenv',
]

test_reqs = [
    'pytest',
    'pytest-mock',
    'pytest-cov',
    'pytest-flask',
    'pytest-factoryboy',
    'pyfakefs',
    'fakeredis',
]


dev_reqs = [
    'ipdb',
    'flake8',
    'flake8-builtins',
    'flake8-bugbear',
    'flake8-mutable',
    'flake8-comprehensions',
    'pep8-naming',
    'dlint',
    'rstcheck',
    'rope',
    'isort',
    'pip',
    'setuptools',
    'wheel',
    'flask-shell-ipython',
    'watchdog',
] + test_reqs


long_description = read('README.md')

setup(
    name='brewlog',
    version=find_version('src', 'brewlog', '_version.py'),
    author='Jarek Zgoda',
    author_email='jarek.zgoda@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    url='http://github.com/zgoda/brewlog',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: Polish',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=base_reqs,
    extras_require={
        'prod': [
            'gunicorn'
            'psycopg2-binary',
        ],
        'test': test_reqs,
        'dev': dev_reqs,
    },
    entry_points={
        'console_scripts': [
            'brewlog=brewlog.cli:main',
        ],
    },
    python_requires='~=3.7',
)
