from marshmallow import Schema, fields


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


brew_schema = BrewSchema()
