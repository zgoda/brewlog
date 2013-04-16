from setuptools import setup, find_packages

setup(
    name='BrewLog',
    version='0.1',
    long_sescription=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
    install_requires=[
        'pytz',
        'Flask',
        'Flask-Babel',
        'Flask-Script',
        'Flask-WTForms',
        'Flask-OAuth',
        'Markdown',
        'SQLAlchemy'
    ]
)

