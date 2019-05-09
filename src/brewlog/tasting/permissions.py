# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import abort
from flask_login import current_user
from permission import Permission, Rule

from ..brew.permissions import PublicAccessPermission


class OwnerOrAuthorRule(Rule):

    def __init__(self, note):
        self.note = note
        super().__init__()

    def check(self):
        return current_user in [self.note.author, self.note.brew.brewery.brewer]

    def deny(self):
        abort(403)


class OwnerOrAuthorPermission(Permission):

    def __init__(self, note):
        self.note = note
        super().__init__()

    def rule(self):
        return OwnerOrAuthorRule(self.note)


class AccessManager:

    def __init__(self, note):
        self.note = note

    @staticmethod
    def check_create(brew):
        perm = PublicAccessPermission(brew)
        if not perm.check():
            perm.deny()

    def check(self):
        perms = [
            PublicAccessPermission(self.note.brew),
            OwnerOrAuthorPermission(self.note),
        ]
        for perm in perms:
            if not perm.check():
                perm.deny()
