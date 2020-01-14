# Configuration files

Adapt these to your setup.

## brewlog.nginx.conf

Base Nginx configuration file, goes to `/etc/nginx/sites-available`. It does not include any SSL/HTTPS configuration as this is managed automatically by [ACME Certbot](https://certbot.eff.org/). Just launch your site unsecured and allow Certbot do its work.

## brewlog.ini

uWSGI configuration file. Place it where it's set in service startup script.

## brewlog.service

systemd service unit file. This goes to `/etc/systemd/system` on Debian and Ubuntu.
