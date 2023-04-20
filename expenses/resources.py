from flask import request
from flask_restful import Resource
from .schemas import Expense, ExpenseSchema
from app import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)


class ExpensesResource(Resource):
    def get(self):
        categories = Expense.query.all()
        return expenses_schema.dump(categories)

    def post(self):
        try:
            form_data = request.get_json()
            category = expense_schema.load(form_data)
            db.session.add(category)
            db.session.commit()
            return expense_schema.dump(category), 201
        except ValidationError as err:
            return err.messages, 400
        # except IntegrityError as err:
        #     db.session.rollback()
        #     return {"error": "Category name already exists"}, 400


class ExpenseResource(Resource):
    def patch(self, expense_id):
        data = request.get_json()
        data["id"] = expense_id
        expense = expense_schema.load(data)
        db.session.commit()
        return expense_schema.dump(expense)

    def delete(self, expense_id):
        expense = Expense.query.get(expense_id)
        db.session.delete(expense)
        db.session.commit()
        return "", 204

    def get(self, expense_id):
        expense = Expense.query.get(expense_id)
        return expense_schema.dump(expense)
