from flask import Blueprint, request, jsonify
from src.controllers.produto_controller import ProdutoController

produto_bp = Blueprint("produtos", __name__)

@produto_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    body, status = ProdutoController.listar_produtos()
    return jsonify(body), status

@produto_bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    body, status = ProdutoController.buscar_produtos(termo, categoria, preco_min, preco_max)
    return jsonify(body), status

@produto_bp.route("/produtos/<int:id>", methods=["GET"])
def buscar_produto(id):
    body, status = ProdutoController.buscar_produto(id)
    return jsonify(body), status

@produto_bp.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    body, status = ProdutoController.criar_produto(dados)
    return jsonify(body), status

@produto_bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    dados = request.get_json()
    body, status = ProdutoController.atualizar_produto(id, dados)
    return jsonify(body), status

@produto_bp.route("/produtos/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    body, status = ProdutoController.deletar_produto(id)
    return jsonify(body), status
