"""
BrewLog, homebrewer's log application
=====================================
"""

from setuptools import setup, find_packages

setup(
    name='BrewLog',
    version='0.4',
    long_sescription=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=open('requirements.pip').read().strip().split('\n')
)

