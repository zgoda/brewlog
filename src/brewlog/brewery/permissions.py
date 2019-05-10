# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_login import current_user

from ..utils.views import (
    AccessManagerBase, OwnerAccessRuleBase, PermissionBase,
    PublicAccessRuleBase,
)


class PublicAccessRule(PublicAccessRuleBase):

    def check(self):
        return self.obj.brewer == current_user or self.obj.brewer.is_public


class PublicAccessPermission(PermissionBase):

    rule_class = PublicAccessRule


class OwnerAccessRule(OwnerAccessRuleBase):

    def check(self):
        return self.obj.brewer == current_user


class OwnerAccessPermission(PermissionBase):

    rule_class = OwnerAccessRule


class AccessManager(AccessManagerBase):

    primary = PublicAccessPermission
    secondary = OwnerAccessPermission
