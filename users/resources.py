from flask import request
from flask_restful import Resource
from .schemas import User, UserSchema
from app import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UsersResource(Resource):
    def get(self):
        categories = User.query.all()
        return users_schema.dump(categories)

    def post(self):
        try:
            form_data = request.get_json()
            category = user_schema.load(form_data)
            db.session.add(category)
            db.session.commit()
            return user_schema.dump(category), 201
        except ValidationError as err:
            return err.messages, 400
        except IntegrityError as err:
            db.session.rollback()
            return {"error": "User name already exists"}, 400
