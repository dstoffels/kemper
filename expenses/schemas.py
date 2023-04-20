from marshmallow import Schema, fields, post_load
from .models import Expense
from users.schemas import User
from categories.schemas import Category
from marshmallow import ValidationError


class CategoryIdField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        category = Category.query.get(value)
        if not category:
            raise ValidationError(f"Invalid category id: {value}")
        return category.id


class UserIdField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        user = User.query.get(value)
        if not user:
            raise ValidationError(f"Invalid user id: {value}")
        return user.id


class ExpenseSchema(Schema):
    id = fields.Integer(dump_only=True)
    timestamp = fields.DateTime(dump_only=True, required=True)
    category_id = CategoryIdField(required=True)
    description = fields.String(required=True)
    vendor = fields.String(required=True)
    amount = fields.Float(required=True)
    is_balanced = fields.Boolean()
    user_id = UserIdField(required=True)

    @post_load
    def create_or_update(self, data, **kwargs):
        if "id" in data:
            expense_id = data.get("id")
            expense = Expense.query.get(expense_id)
            for key, val in data.items():
                setattr(expense, key, val)
            return expense
        else:
            return Expense(**data)

    class Meta:
        model = Expense
