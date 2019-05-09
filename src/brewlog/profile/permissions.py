# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import abort, request
from flask_login import current_user
from permission import Permission, Rule


class PublicAccessRule(Rule):

    def __init__(self, user):
        self.user = user
        super().__init__()

    def check(self):
        return self.user == current_user or self.user.is_public

    def deny(self):
        abort(404)


class PublicAccessPermission(Permission):

    def __init__(self, user):
        self.user = user
        super().__init__()

    def rule(self):
        return PublicAccessRule(self.user)


class OwnerAccessRule(Rule):

    def __init__(self, user):
        self.user = user
        super().__init__()

    def check(self):
        return self.user == current_user

    def deny(self):
        abort(403)


class OwnerAccessPermission(Permission):

    def __init__(self, user):
        self.user = user
        super().__init__()

    def rule(self):
        return OwnerAccessRule(self.user)


class AccessManager:

    def __init__(self, user):
        self.user = user

    def check(self, require_owner=False):
        perms = [PublicAccessPermission(self.user)]
        if request.method == 'POST' or require_owner:
            perms.append(OwnerAccessPermission(self.user))
        for perm in perms:
            if not perm.check():
                perm.deny()
