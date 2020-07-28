from marshmallow import Schema, fields
from flask import url_for


class UserSchema(Schema):
    id = fields.Int()  # noqa: A003
    name = fields.Str()


class BrewerySchema(Schema):
    id = fields.Int()  # noqa: A003
    name = fields.Str()
    user = fields.Nested(UserSchema, only=['id', 'name'])


class BrewSchema(Schema):
    id = fields.Int()  # noqa: A003
    name = fields.Str()
    brewery = fields.Nested(BrewerySchema, only=['id', 'name'])
    url = fields.Method('item_url')

    def item_url(self, obj):
        return url_for('brew.details', brew_id=obj.id)


brew_schema = BrewSchema()
