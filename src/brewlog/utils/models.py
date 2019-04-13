# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_sqlalchemy.model import Model as BaseModel


class MappedModelMixin:

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }


class Model(BaseModel, MappedModelMixin):
    pass
