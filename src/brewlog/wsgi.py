# Copyright 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import os

from brewlog import make_app

application = make_app(os.environ.get('ENV'))
