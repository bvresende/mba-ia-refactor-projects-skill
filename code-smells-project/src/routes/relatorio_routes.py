from flask import Blueprint, jsonify
from src.controllers.relatorio_controller import RelatorioController

relatorio_bp = Blueprint("relatorios", __name__)

@relatorio_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    body, status = RelatorioController.relatorio_vendas()
    return jsonify(body), status

@relatorio_bp.route("/health", methods=["GET"])
def health_check():
    body, status = RelatorioController.health_check()
    return jsonify(body), status

@relatorio_bp.route("/", methods=["GET"])
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health"
        }
    }), 200
