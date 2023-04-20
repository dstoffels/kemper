from marshmallow import Schema, fields, post_load
from .models import Category
from users.schemas import UserSchema


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()

    @post_load
    def create(self, data, **kwargs):
        return Category(**data)

    class Meta:
        model = Category
