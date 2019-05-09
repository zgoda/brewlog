# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import request
from flask_login import current_user
from permission import Permission

from ..utils.views import (
    AccessManagerBase, OwnerAccessRuleBase, PublicAccessPermissionBase,
    PublicAccessRuleBase,
)


class PublicAccessRule(PublicAccessRuleBase):

    def check(self):
        return self.obj == current_user or self.obj.is_public


class PublicAccessPermission(PublicAccessPermissionBase):

    rule_class = PublicAccessRule


class OwnerAccessRule(OwnerAccessRuleBase):

    def check(self):
        return self.obj == current_user


class OwnerAccessPermission(Permission):

    def __init__(self, user):
        self.user = user
        super().__init__()

    def rule(self):
        return OwnerAccessRule(self.user)


class AccessManager(AccessManagerBase):

    def check(self, require_owner=False):
        perms = [PublicAccessPermission(self.obj)]
        if request.method == 'POST' or require_owner:
            perms.append(OwnerAccessPermission(self.obj))
        for perm in perms:
            if not perm.check():
                perm.deny()
