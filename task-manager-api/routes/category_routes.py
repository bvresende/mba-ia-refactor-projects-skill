from flask import Blueprint, request, jsonify
from controllers.category_controller import CategoryController

category_bp = Blueprint('categories', __name__)

@category_bp.route('/categories', methods=['GET'])
def get_categories():
    body, status = CategoryController.get_categories()
    return jsonify(body), status

@category_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    body, status = CategoryController.create_category(data)
    return jsonify(body), status

@category_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    data = request.get_json()
    body, status = CategoryController.update_category(cat_id, data)
    return jsonify(body), status

@category_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    body, status = CategoryController.delete_category(cat_id)
    return jsonify(body), status
