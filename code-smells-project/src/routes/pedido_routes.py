from flask import Blueprint, request, jsonify
from src.controllers.pedido_controller import PedidoController

pedido_bp = Blueprint("pedidos", __name__)

@pedido_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json()
    body, status = PedidoController.criar_pedido(dados)
    return jsonify(body), status

@pedido_bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    body, status = PedidoController.listar_todos_pedidos()
    return jsonify(body), status

@pedido_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    body, status = PedidoController.listar_pedidos_usuario(usuario_id)
    return jsonify(body), status

@pedido_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    dados = request.get_json()
    body, status = PedidoController.atualizar_status_pedido(pedido_id, dados)
    return jsonify(body), status
