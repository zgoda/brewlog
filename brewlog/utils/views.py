from flask import request, session, url_for
from flask_login import current_user
from werkzeug.exceptions import Forbidden


def get_user_object(klass, object_id=None, user=None, raise_403=True):
    """Get object (model) of specified class related to user. If the object
    does not pertain to specified user, :exc:`werkzeug.exceptions.Forbidden`
    may be raised.

    :param klass: requested object class
    :type klass: class
    :param object_id: object identifier, defaults to None
    :type object_id: mixed, optional
    :param user: user object; if not specified :obj:`current_user` is used,
                 defaults to None
    :type user: :class:`models.users.BrewerProfile`, optional
    :param raise_403: whether to raise Forbidden, defaults to True
    :type raise_403: bool, optional
    :raises Forbidden: if user is not an owner of the object
    :return: requested object
    :rtype: mixed
    """

    if object_id is None:
        return
    if user is None:
        user = current_user
    obj = klass.query.get_or_404(object_id)
    if obj.user != user:
        if raise_403:
            raise Forbidden()
        return
    return obj


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
