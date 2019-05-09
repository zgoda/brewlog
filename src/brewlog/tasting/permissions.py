# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_login import current_user

from ..brew.permissions import PublicAccessPermission
from ..utils.views import AccessManagerBase, OwnerAccessRuleBase, PermissionBase


class OwnerOrAuthorRule(OwnerAccessRuleBase):

    def check(self):
        return current_user in [self.obj.author, self.obj.brew.brewery.brewer]


class OwnerOrAuthorPermission(PermissionBase):

    rule_class = OwnerOrAuthorRule


class AccessManager(AccessManagerBase):

    @staticmethod
    def check_create(brew):
        perm = PublicAccessPermission(brew)
        if not perm.check():
            perm.deny()

    def check(self):
        perms = [
            PublicAccessPermission(self.obj.brew),
            OwnerOrAuthorPermission(self.obj),
        ]
        for perm in perms:
            if not perm.check():
                perm.deny()
