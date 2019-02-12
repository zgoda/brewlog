from os import path

from setuptools import setup, find_packages

import versioneer


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='BrewLog',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Jarek Zgoda',
    author_email='jarek.zgoda@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='BSD',
    packages=find_packages(exclude=['docs', 'tests', 'secrets']),
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=(
        'Flask',
        'Flask-Babel',
        'Flask-Login',
        'Flask-FlatPages',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Flask-Bootstrap',
        'SQLAlchemy-Utils',
        'Authlib',
        'Markdown',
        'translitcodec',
        'python-dateutil',
        'WTForms-Alchemy',
    ),
    setup_requires=(
        'pytest-runner',
    ),
    tests_require=(
        'pytest',
        'pytest-mock',
        'pytest-cov',
        'pytest-flask',
        'fixture',
    ),
    extras_require={
        'prod': ['psycopg2', 'uwsgi']
    },
    python_requires='~=3.6',
)
