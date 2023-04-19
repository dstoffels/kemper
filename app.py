from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import post_load, fields, ValidationError
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ
from datetime import datetime

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("SQLALCHEMY_DATABASE_URI")

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    entries = db.relationship("Entry", backref="user", lazy=True)

    def __repr__(self) -> str:
        return self.username


class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, unique=True)

    @post_load
    def create_or_update(self, data, **kwargs):
        if "user_id" in kwargs:
            user_id = kwargs.get("user_id")
            user = Entry.query.get_or_404(user_id)
            # how can I more easily apply the incoming data to override the existing data of the entry?
            for key, val in data.items():
                setattr(user, key, val)
            return user
        else:
            return User(**data)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    CATEGORIES = ["Supplies", "Repairs", "Taxes & Licenses", "Misc"]
    category = db.Column(db.String(64), default="Misc")
    description = db.Column(db.String(256), default="")
    vendor = db.Column(db.String(256), default="")
    amount = db.Column(db.Numeric(precision=2, asdecimal=True), default=0.00)
    is_balanced = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self) -> str:
        return f"{self.timestamp}: {self.description} - ${self.amount}"


class EntrySchema(ma.Schema):
    id = fields.Integer()
    timestamp = fields.DateTime(dump_only=True, required=True)
    category = fields.String(
        default="Misc", validate=lambda x: x in ["Supplies", "Repairs", "Taxes & Licenses", "Misc"]
    )
    description = fields.String(required=True, default="")
    vendor = fields.String(required=True, default="")
    amount = fields.Float(required=True, places=2)
    is_balanced = fields.Boolean(default=False)
    user_id = fields.Integer(required=True)

    @post_load
    def create_or_update(self, data, **kwargs):
        if "id" in data:
            entry_id = data.get("id")
            entry = Entry.query.get_or_404(entry_id)
            # how can I more easily apply the incoming data to override the existing data of the entry?
            for key, val in data.items():
                setattr(entry, key, val)
            return entry
        else:
            return Entry(**data)


# Schemas (serializers)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
entry_schema = EntrySchema()
entries_schema = EntrySchema(many=True)


# Resources
class UsersResource(Resource):
    def post(self):
        try:
            new_user = user_schema.load(request.get_json())
            db.session.add(new_user)
            db.session.commit()
            return user_schema.dump(new_user), 201
        except ValidationError as err:
            return err.messages, 400

    def get(self):
        all_users = User.query.all()
        return users_schema.dump(all_users), 200


class EntriesResource(Resource):
    def post(self):
        try:
            new_entry = entry_schema.load(request.get_json())
            db.session.add(new_entry)
            db.session.commit()
            return entry_schema.dump(new_entry), 201
        except ValidationError as err:
            return err.messages, 400

    def get(self):
        all_entries = Entry.query.all()
        return entries_schema.dump(all_entries), 200


class EntryResource(Resource):
    def patch(self, entry_id):
        try:
            data = request.get_json()
            data["id"] = entry_id
            entry = entry_schema.load(data, partial=True)
            db.session.commit()
            return entry_schema.dump(entry), 200
        except ValidationError as err:
            return err.messages, 400

    def delete(self, entry_id):
        entry = Entry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        return "", 204

    def get(self, entry_id):
        entry = Entry.query.get_or_404(entry_id)
        return entry_schema.dump(entry), 200


# Routes
api.add_resource(UsersResource, "/api/users")
api.add_resource(EntriesResource, "/api/entries")
api.add_resource(EntryResource, "/api/entries/<int:entry_id>")
