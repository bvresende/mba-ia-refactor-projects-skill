from flask import Blueprint, jsonify
from controllers.report_controller import ReportController

report_bp = Blueprint('reports', __name__)

@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    body, status = ReportController.summary_report()
    return jsonify(body), status

@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    body, status = ReportController.user_report(user_id)
    return jsonify(body), status
