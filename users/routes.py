from app import api
from .resources import UsersResource

api.add_resource(UsersResource, "/api/users")
