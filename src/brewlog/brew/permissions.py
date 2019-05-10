# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_login import current_user

from ..utils.views import (
    AccessManagerBase, OwnerAccessRuleBase, PermissionBase,
    PublicAccessRuleBase,
)


class OwnerAccessRule(OwnerAccessRuleBase):

    def check(self):
        return self.obj.brewery.brewer == current_user


class OwnerAccessPermission(PermissionBase):

    rule_class = OwnerAccessRule


class PublicAccessRule(PublicAccessRuleBase):

    def check(self):
        return (self.obj.is_public and self.obj.brewery.brewer.is_public) \
            or self.obj.brewery.brewer == current_user


class PublicAccessPermission(PermissionBase):

    rule_class = PublicAccessRule


class AccessManager(AccessManagerBase):

    primary = PublicAccessPermission
    secondary = OwnerAccessPermission
