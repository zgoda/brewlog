import collections
from typing import Optional
from urllib.parse import urljoin, urlparse

from flask import abort, request, session, url_for
from itsdangerous.exc import BadSignature, SignatureExpired
from itsdangerous.url_safe import URLSafeTimedSerializer
from permission import Permission, Rule


def next_redirect(fallback_endpoint: str, *args, **kwargs) -> str:
    """Find redirect url. The order of search is request params, session and
    finally url for fallback endpoint is returned if none found. Args and
    kwargs are passed intact to endpoint.

    :param fallback_endpoint: full endpoint specification
    :type fallback_endpoint: str
    :return: HTTP path to redirect to
    :rtype: str
    """
    for c in [request.args.get('next'), session.pop('next', None)]:
        if is_redirect_safe(c):
            return c
    return url_for(fallback_endpoint, *args, **kwargs)


def is_redirect_safe(target: Optional[str]) -> bool:
    """Check if redirect is safe, that is using HTTP protocol and is pointing
    to the same site.

    :param target: redirect target url
    :type target: str
    :return: flag signalling whether redirect is safe
    :rtype: bool
    """
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


class RuleBase(Rule):

    def __init__(self, obj):
        self.obj = obj
        super().__init__()


class PublicAccessRuleBase(RuleBase):

    def deny(self):
        abort(404)


class OwnerAccessRuleBase(RuleBase):

    def deny(self):
        abort(403)


class PermissionBase(Permission):

    rule_class = None

    def __init__(self, obj):
        self.obj = obj
        super().__init__()

    def rule(self):
        return self.rule_class(self.obj)


class AccessManagerBase:

    primary = None
    secondary = None

    def __init__(self, obj, secondary_condition):
        self.obj = obj
        self.perms = []
        if self.primary:
            self.perms.append(self.primary(obj))
        if self.secondary and secondary_condition:
            self.perms.append(self.secondary(obj))

    def check(self):
        for perm in self.perms:
            if not perm.check():
                perm.deny()


TokenCheckResult = collections.namedtuple(
    'TokenCheckResult', ['is_error', 'message', 'payload']
)


def check_token(token: str, secret: str, max_age: int) -> TokenCheckResult:
    """Check token validity, returns validation result with payload if token
    is valid.

    :param token: token to check
    :type token: str
    :param secret: secret that was used to generate token
    :type secret: str
    :param max_age: max age of token
    :type max_age: int
    :return: validation result
    :rtype: TokenCheckResult
    """
    serializer = URLSafeTimedSerializer(secret)
    payload = None
    is_error = True
    msg = None
    try:
        payload = serializer.loads(token, max_age=max_age)
        is_error = False
    except SignatureExpired as e:
        msg = f'przeterminowany token, był ważny 48 godz. od {e.date_signed}',
    except BadSignature:
        msg = 'błędny token'
    return TokenCheckResult(is_error, message=msg, payload=payload)
