# Configuration files

Adapt these to your setup. My suggestion is to create instance directory in someone's home dir and then put instance configuration files in `config` subdirectory there but of course YMMV. Example directory structure that I'm using in my Brewlog deployment:

```shell
~$ tree -d -L 2
.
└── brewlog
    ├── config
    ├── logs
    ├── static -> venv/lib/python3.8/site-packages/brewlog/static
    └── venv
```

## brewlog.nginx.conf

Base Nginx configuration file, goes to `/etc/nginx/sites-available`. It does not include any SSL/HTTPS configuration as this is managed automatically by [ACME Certbot](https://certbot.eff.org/). Just launch your site unsecured and allow Certbot do its work.

To simplify things a bit I usually create symlink to application static content distributed in installation package in instance root directory.

## brewlog.ini

uWSGI configuration file. Place it where it's set in service startup script. Consider `~/brewlog/config`.

## brewlog.service

systemd service unit file. This goes to `/etc/systemd/system` on Debian and Ubuntu.

## environment

Environment data file to be used with systemd unit. It should go to the directory where user specified in systemd unit file has r+x permissions. Consider `~/brewlog/config`.
