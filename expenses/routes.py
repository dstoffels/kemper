from app import api
from .resources import ExpensesResource, ExpenseResource

api.add_resource(ExpensesResource, "/api/expenses")
api.add_resource(ExpenseResource, "/api/expenses/<int:expense_id>")
