from src.database.db import get_db

class ProdutoModel:
    @staticmethod
    def get_todos():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_por_id(produto_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def criar(nome, descricao, preco, estoque, categoria):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id)
        )
        db.commit()
        return True

    @staticmethod
    def deletar(produto_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        db.commit()
        return True

    @staticmethod
    def atualizar_estoque(produto_id, quantidade_decremento):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade_decremento, produto_id)
        )
        db.commit()
        return True

    @staticmethod
    def buscar(termo="", categoria=None, preco_min=None, preco_max=None):
        db = get_db()
        cursor = db.cursor()

        query = "SELECT * FROM produtos WHERE 1=1"
        params = []

        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            termo_like = f"%{termo}%"
            params.extend([termo_like, termo_like])
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
