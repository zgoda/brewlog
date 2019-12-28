import codecs
import re
from os import path

from setuptools import find_packages, setup

# parts below shamelessly stolen from pypa/pip
here = path.abspath(path.dirname(__file__))


def read(*parts):
    with codecs.open(path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


base_reqs = [
    'Flask',
    'Flask-Babel',
    'Flask-Login',
    'Flask-FlatPages',
    'Flask-SQLAlchemy',
    'Flask-WTF',
    'Bootstrap-Flask',
    'Flask-Migrate',
    'SQLAlchemy-Utils',
    'Authlib[client]',
    'Markdown',
    'WTForms-Alchemy',
    'WTForms-Components',
    'permission',
    'psycopg2-binary',
]

test_reqs = [
    'pytest',
    'pytest-mock',
    'pytest-cov',
    'pytest-flask',
    'pytest-factoryboy',
    'pyfakefs',
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
    'doc8',
    'rope',
    'Sphinx',
    'pip',
    'setuptools',
    'wheel',
    'flask-shell-ipython',
    'watchdog',
    'termcolor',
    'python-dotenv',
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
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=base_reqs,
    setup_requires=(
        'babel',
    ),
    extras_require={
        'prod': ['uwsgi'],
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
