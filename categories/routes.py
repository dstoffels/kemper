from app import api
from .resources import CategoriesResource

api.add_resource(CategoriesResource, "/api/categories")
