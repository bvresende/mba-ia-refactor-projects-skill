from src.database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

class UsuarioModel:
    @staticmethod
    def get_todos():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_por_id(usuario_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def criar(nome, email, senha, tipo="cliente"):
        db = get_db()
        cursor = db.cursor()
        senha_hash = generate_password_hash(senha)
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def autenticar(email, senha):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, senha, tipo FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        if not row:
            return None

        stored_pass = row["senha"]
        is_valid = False
        if stored_pass.startswith(("pbkdf2:", "scrypt:")):
            is_valid = check_password_hash(stored_pass, senha)
        else:
            # Compatibilidade com seed em plain text
            is_valid = (stored_pass == senha)

        if is_valid:
            return {
                "id": row["id"],
                "nome": row["nome"],
                "email": row["email"],
                "tipo": row["tipo"]
            }
        return None
