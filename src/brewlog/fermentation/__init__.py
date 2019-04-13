# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import Blueprint

ferm_bp = Blueprint('ferm', __name__)

from . import views  # noqa
