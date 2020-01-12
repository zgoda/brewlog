from flask_login import current_user

from ..utils.views import (
    AccessManagerBase, OwnerAccessRuleBase, PermissionBase,
    PublicAccessRuleBase,
)


class OwnerAccessRule(OwnerAccessRuleBase):

    def check(self) -> bool:
        return self.obj.brewery.brewer == current_user


class OwnerAccessPermission(PermissionBase):

    rule_class = OwnerAccessRule


class PublicAccessRule(PublicAccessRuleBase):

    def check(self) -> bool:
        return (self.obj.is_public and self.obj.brewery.brewer.is_public) \
            or self.obj.brewery.brewer == current_user


class PublicAccessPermission(PermissionBase):

    rule_class = PublicAccessRule


class AccessManager(AccessManagerBase):

    primary = PublicAccessPermission
    secondary = OwnerAccessPermission
