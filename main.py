from flask import Flask, jsonify
from flask_restful import Resource, Api, fields, marshal_with

app = Flask(__name__)

import config

import models

from models import * 
import routes

api = Api(app)

category_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String
}

class CategoryAPI(Resource):
    @marshal_with(category_fields)
    def get(self):
        categories = Category.query.all()
        return categories


api.add_resource(CategoryAPI, '/api/category')