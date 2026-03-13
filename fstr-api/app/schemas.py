from marshmallow import Schema, fields, validate, post_load, ValidationError
from datetime import datetime


class UserSchema(Schema):
    email = fields.Email(required=True)
    fam = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    otc = fields.Str(allow_none=True, validate=validate.Length(max=100))
    phone = fields.Str(required=True, validate=validate.Length(min=1, max=20))


class CoordSchema(Schema):
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    height = fields.Int(required=True, validate=validate.Range(min=0))


class ImageSchema(Schema):
    data = fields.Str(required=True)  # base64
    title = fields.Str(allow_none=True)


class LevelSchema(Schema):
    winter = fields.Str(allow_none=True)
    summer = fields.Str(allow_none=True)
    autumn = fields.Str(allow_none=True)
    spring = fields.Str(allow_none=True)


class PerevalSubmitSchema(Schema):
    beauty_title = fields.Str(allow_none=True)
    title = fields.Str(required=True)
    other_titles = fields.Str(allow_none=True)
    connect = fields.Str(allow_none=True)
    add_time = fields.DateTime(required=True, format='%Y-%m-%d %H:%M:%S')
    user = fields.Nested(UserSchema, required=True)
    coords = fields.Nested(CoordSchema, required=True)
    level = fields.Nested(LevelSchema, required=True)
    images = fields.List(fields.Nested(ImageSchema), required=True, validate=validate.Length(min=1))

    @post_load
    def check_images(self, data, **kwargs):
        if not data.get('images'):
            raise ValidationError('At least one image is required')
        return data