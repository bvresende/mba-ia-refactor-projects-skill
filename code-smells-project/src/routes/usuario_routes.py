from flask import Blueprint, request, jsonify
from src.controllers.usuario_controller import UsuarioController

usuario_bp = Blueprint("usuarios", __name__)

@usuario_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    body, status = UsuarioController.listar_usuarios()
    return jsonify(body), status

@usuario_bp.route("/usuarios/<int:id>", methods=["GET"])
def buscar_usuario(id):
    body, status = UsuarioController.buscar_usuario(id)
    return jsonify(body), status

@usuario_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    dados = request.get_json()
    body, status = UsuarioController.criar_usuario(dados)
    return jsonify(body), status

@usuario_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    body, status = UsuarioController.login(dados)
    return jsonify(body), status
