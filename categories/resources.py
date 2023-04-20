from flask import request
from flask_restful import Resource
from .models import Category
from .schemas import CategorySchema
from app import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

expense_schema = CategorySchema()
expenses_schema = CategorySchema(many=True)


class CategoriesResource(Resource):
    def get(self):
        categories = Category.query.all()
        return expenses_schema.dump(categories)

    def post(self):
        try:
            form_data = request.get_json()
            category = expense_schema.load(form_data)
            db.session.add(category)
            db.session.commit()
            return expense_schema.dump(category)
        except ValidationError as err:
            return err.messages, 400
        except IntegrityError as err:
            db.session.rollback()
            return {"error": "Category name already exists"}, 400
