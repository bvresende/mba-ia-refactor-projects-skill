from flask import Blueprint, request, jsonify
from controllers.task_controller import TaskController

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    body, status = TaskController.get_tasks()
    return jsonify(body), status

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    body, status = TaskController.get_task(task_id)
    return jsonify(body), status

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    body, status = TaskController.create_task(data)
    return jsonify(body), status

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    body, status = TaskController.update_task(task_id, data)
    return jsonify(body), status

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    body, status = TaskController.delete_task(task_id)
    return jsonify(body), status

@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    q = request.args.get('q', '')
    task_status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')
    body, status = TaskController.search_tasks(q, task_status, priority, user_id)
    return jsonify(body), status

@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    body, status = TaskController.get_stats()
    return jsonify(body), status
