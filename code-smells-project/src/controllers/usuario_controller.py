from src.models.usuario_model import UsuarioModel

class UsuarioController:
    @staticmethod
    def listar_usuarios():
        usuarios = UsuarioModel.get_todos()
        return {"dados": usuarios, "sucesso": True}, 200

    @staticmethod
    def buscar_usuario(usuario_id):
        usuario = UsuarioModel.get_por_id(usuario_id)
        if usuario:
            return {"dados": usuario, "sucesso": True}, 200
        return {"erro": "Usuário não encontrado"}, 404

    @staticmethod
    def criar_usuario(dados):
        if not dados:
            return {"erro": "Dados inválidos"}, 400

        nome = dados.get("nome", "").strip()
        email = dados.get("email", "").strip()
        senha = dados.get("senha", "").strip()
        tipo = dados.get("tipo", "cliente")

        if not nome or not email or not senha:
            return {"erro": "Nome, email e senha são obrigatórios"}, 400

        novo_id = UsuarioModel.criar(nome, email, senha, tipo)
        return {"dados": {"id": novo_id}, "sucesso": True}, 201

    @staticmethod
    def login(dados):
        if not dados:
            return {"erro": "Dados inválidos"}, 400

        email = dados.get("email", "").strip()
        senha = dados.get("senha", "").strip()

        if not email or not senha:
            return {"erro": "Email e senha são obrigatórios"}, 400

        usuario = UsuarioModel.autenticar(email, senha)
        if usuario:
            return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}, 200
        return {"erro": "Email ou senha inválidos", "sucesso": False}, 401
