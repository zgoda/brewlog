# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import abort, request, session, url_for
from permission import Permission, Rule


def next_redirect(fallback_endpoint, *args, **kwargs):
    """Find redirect url. The order of search is request params, session and
    finally url for fallback endpoint is returned if none found. Args and
    kwargs are passed intact to endpoint.

    :param fallback_endpoint: full endpoint specification
    :type fallback_endpoint: str
    :return: HTTP path to redirect to
    :rtype: str
    """

    return request.args.get('next') \
        or session.pop('next', None) \
        or url_for(fallback_endpoint, *args, **kwargs)


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
