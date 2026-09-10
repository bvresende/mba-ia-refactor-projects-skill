from src.models.pedido_model import PedidoModel
from src.models.produto_model import ProdutoModel

class PedidoController:
    @staticmethod
    def criar_pedido(dados):
        if not dados:
            return {"erro": "Dados inválidos"}, 400

        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])

        if not usuario_id:
            return {"erro": "Usuario ID é obrigatório"}, 400
        if not itens or len(itens) == 0:
            return {"erro": "Pedido deve ter pelo menos 1 item"}, 400

        total = 0.0
        itens_processados = []

        for item in itens:
            prod_id = item.get("produto_id")
            qtd = item.get("quantidade", 0)

            if not prod_id or qtd <= 0:
                return {"erro": f"Item inválido no pedido: {item}", "sucesso": False}, 400

            produto = ProdutoModel.get_por_id(prod_id)
            if not produto:
                return {"erro": f"Produto {prod_id} não encontrado", "sucesso": False}, 400
            if produto["estoque"] < qtd:
                return {"erro": f"Estoque insuficiente para {produto['nome']}", "sucesso": False}, 400

            subtotal = produto["preco"] * qtd
            total += subtotal
            itens_processados.append({
                "produto_id": prod_id,
                "quantidade": qtd,
                "preco_unitario": produto["preco"]
            })

        pedido_id = PedidoModel.criar_pedido(usuario_id, round(total, 2), itens_processados)

        return {
            "dados": {"pedido_id": pedido_id, "total": round(total, 2)},
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso"
        }, 201

    @staticmethod
    def listar_pedidos_usuario(usuario_id):
        pedidos = PedidoModel.get_pedidos_usuario(usuario_id)
        return {"dados": pedidos, "sucesso": True}, 200

    @staticmethod
    def listar_todos_pedidos():
        pedidos = PedidoModel.get_todos()
        return {"dados": pedidos, "sucesso": True}, 200

    @staticmethod
    def atualizar_status_pedido(pedido_id, dados):
        novo_status = dados.get("status", "") if dados else ""
        status_validos = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

        if novo_status not in status_validos:
            return {"erro": "Status inválido"}, 400

        PedidoModel.atualizar_status(pedido_id, novo_status)
        return {"sucesso": True, "mensagem": "Status atualizado"}, 200
