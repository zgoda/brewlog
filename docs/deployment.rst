Application deployment
======================

Application is WSGI based so it should be deployable with any supporting setup
with no specific requirements. I prefer PostgreSQL, uWSGI and Nginx but it
should work with any database supported by SQLAlchemy, any WSGI application
server and any web server that supports WSGI. Example setup configuration
using my preferred software is provided with source code.

OAuth2
------

Application identifies users with remote services providing OAuth2. By default
only Facebook, Github and Google are configured but it may be extended to use
other identity providers. Unfortunately responses from providers vary so
wildly that it has to be done by means of fork (or pull request, if someone is
kind enough to share code).

SSL
---

Because the app uses OAuth2 for user identification, it's really necessary to
run it secured with SSL or the providers will refuse to issue authentication
codes.
