from marshmallow import Schema, fields, post_load
from .models import User


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)

    @post_load
    def create(self, data, **kwargs):
        return User(**data)

    class Meta:
        model = User
