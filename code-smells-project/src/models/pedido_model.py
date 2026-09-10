from src.database.db import get_db

class PedidoModel:
    @staticmethod
    def criar_pedido(usuario_id, total, itens):
        """Cria um pedido e seus itens dentro de uma transação parametrizada atômica."""
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total)
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"])
            )

        db.commit()
        return pedido_id

    @staticmethod
    def get_pedidos_usuario(usuario_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
        pedidos_rows = cursor.fetchall()
        return PedidoModel._carregar_itens_para_pedidos(db, pedidos_rows)

    @staticmethod
    def get_todos():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM pedidos")
        pedidos_rows = cursor.fetchall()
        return PedidoModel._carregar_itens_para_pedidos(db, pedidos_rows)

    @staticmethod
    def atualizar_status(pedido_id, novo_status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _carregar_itens_para_pedidos(db, pedidos_rows):
        if not pedidos_rows:
            return []

        resultado = []
        cursor = db.cursor()

        for row in pedidos_rows:
            pedido_id = row["id"]
            cursor.execute("""
                SELECT ip.produto_id, p.nome AS produto_nome, ip.quantidade, ip.preco_unitario
                FROM itens_pedido ip
                LEFT JOIN produtos p ON p.id = ip.produto_id
                WHERE ip.pedido_id = ?
            """, (pedido_id,))
            itens_rows = cursor.fetchall()

            itens = []
            for item in itens_rows:
                itens.append({
                    "produto_id": item["produto_id"],
                    "produto_nome": item["produto_nome"] if item["produto_nome"] else "Desconhecido",
                    "quantidade": item["quantidade"],
                    "preco_unitario": item["preco_unitario"]
                })

            resultado.append({
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": itens
            })

        return resultado
