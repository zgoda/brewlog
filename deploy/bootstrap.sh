#! /usr/bin/env bash

# at the very beginning
locale-gen en_US en_US.UTF-8 pl_PL pl_PL.UTF-8
dpkg-reconfigure locales

# system
apt-get update && apt-get -y upgrade
apt-get install -y htop mc git python-virtualenv postgresql nginx python-dev libpq-dev

# virtual env
VENV_DIR=/opt/venv
virtualenv $VENV_DIR
source $VENV_DIR/bin/activate
pip install -U ipython

# source and deps
DEPLOY_DIR=/opt/dist
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR
git clone https://github.com/zgoda/brew-log.git brewlog
cd brewlog
pip install -U -r requirements.pip

# postgresql etc
cat << EOF | su - postgres -c psql
CREATE USER brewlog WITH PASSWORD 'brewlog';
CREATE DATABASE brewlog WITH OWNER brewlog;
EOF

echo "SQLALCHEMY_DATABASE_URI = 'postgresql://brewlog:brewlog@localhost/brewlog'" >> brewlog/config_local.py
echo "DEBUG = False" >> brewlog/config_local.py

python manage.py --env=prod initdb
