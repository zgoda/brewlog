from flask import request, session, url_for


def next_redirect(fallback_endpoint, *args, **kwargs):
    """Find redirect url. The order of search is request params, session and
    finally url for fallback endpoint is returned if none found. Args and
    kwargs are passed intact to endpoint.

    :param fallback_endpoint: full endpoint specification
    :type fallback_endpoint: str
    :return: HTTP path to redirect to
    :rtype: str
    """

    return request.args.get('next') or session.pop('next', None) or url_for(fallback_endpoint, *args, **kwargs)
