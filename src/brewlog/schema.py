from marshmallow import Schema, fields
from flask import url_for


class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class BrewerySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    user = fields.Nested(UserSchema, only=['id', 'name'])


class BrewSchema(Schema):
    id = fields.Int()
    name = fields.Method('item_name')
    brewery = fields.Nested(BrewerySchema, only=['id', 'name'])
    url = fields.Method('item_url')
    date_brewed = fields.Date()

    def item_url(self, obj):
        return url_for('brew.details', brew_id=obj.id)

    def item_name(self, obj):
        if obj.code:
            return f'#{obj.code} {obj.name}'
        return obj.name


class BrewActionSchema(Schema):
    id = fields.Int()
    fg = fields.Float()
    volume = fields.Float()
    carbonation = fields.Str()
    date = fields.Date()
    notes = fields.Str()
    name = fields.Str()
    temperature = fields.Float()


brew_schema = BrewSchema()
brew_action_schema = BrewActionSchema()
