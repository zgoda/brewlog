# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from ..ext import db


def update_steps_gravity(step):
    if step.fg is not None:
        next_step = step.next_step()
        if next_step:
            next_step.og = step.fg
            db.session.add(next_step)
