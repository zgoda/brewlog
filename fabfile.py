from fabric.api import env, cd, run, prefix, sudo


#env.hosts = ['root@vps65311.ovh.net']
env.hosts = ['root@vm']


def clearenv():
    with cd('/opt'):
        run('rm -rf b/venv')


def initenv():
    run('mkdir -p /opt/b')
    with cd('/opt/b'):
        run('virtualenv --python=/usr/bin/python2.7 venv')
        run('git clone https://github.com/zgoda/brew-log.git brewlog')
        with prefix('. venv/bin/activate'):
            run('pip install -U ipython ipdb pip setuptools')
            run('pip install -U -r brewlog/requirements.pip')


def copyconfigs():
    sudo('rm -f /etc/nginx/sites-enabled/default')
    sudo('cp -f brewlog/conf/nginx.conf /etc/nginx/sites-available/brewlog')
    sudo('ln -sf /etc/nginx/sites-available/brewlog /etc/nginx/sites-enabled/brewlog')
    sudo('cp -f brewlog/conf/uwsgi.ini /etc/uwsgi/apps-available/brewlog.ini')
    sudo('ln -sf /etc/uwsgi/apps-available/brewlog.ini /etc/uwsgi/apps-enabled/brewlog.ini')


def install():
    clearenv()
    initenv()
    copyconfigs()
