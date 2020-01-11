from flask_login import current_user

from ..utils.views import (
    AccessManagerBase, OwnerAccessRuleBase, PermissionBase,
    PublicAccessRuleBase,
)


class PublicAccessRule(PublicAccessRuleBase):

    def check(self):
        return self.obj == current_user or self.obj.is_public


class PublicAccessPermission(PermissionBase):

    rule_class = PublicAccessRule


class OwnerAccessRule(OwnerAccessRuleBase):

    def check(self):
        return self.obj == current_user


class OwnerAccessPermission(PermissionBase):

    rule_class = OwnerAccessRule


class AccessManager(AccessManagerBase):

    primary = PublicAccessPermission
    secondary = OwnerAccessPermission
