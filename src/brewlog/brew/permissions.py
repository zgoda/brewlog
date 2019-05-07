# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import abort
from flask_login import current_user
from permission import Permission, Rule


class OwnerAccessRule(Rule):

    def __init__(self, brew):
        self.brew = brew
        super().__init__()

    def check(self):
        return self.brew.brewery.brewer == current_user

    def deny(self):
        abort(403)


class OwnerAccessPermission(Permission):

    def __init__(self, brew):
        self.brew = brew
        super().__init__()

    def rule(self):
        return OwnerAccessRule(self.brew)


class PublicAccessRule(Rule):

    def __init__(self, brew):
        self.brew = brew
        super().__init__()

    def check(self):
        return (self.brew.is_public and self.brew.brewery.brewer.is_public) \
            or self.brew.brewery.brewer == current_user

    def deny(self):
        abort(404)


class PublicAccessPermission(Permission):

    def __init__(self, brew):
        self.brew = brew
        super().__init__()

    def rule(self):
        return PublicAccessRule(self.brew)
