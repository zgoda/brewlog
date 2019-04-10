from flask_sqlalchemy.model import Model as BaseModel


class MappedModelMixin:

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }


class Model(BaseModel, MappedModelMixin):
    pass
