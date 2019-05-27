# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from .app import make_app  # noqa

from ._version import get_version
__version__ = get_version()
del get_version
