from src.models.produto_model import ProdutoModel

class ProdutoController:
    @staticmethod
    def listar_produtos():
        produtos = ProdutoModel.get_todos()
        return {"dados": produtos, "sucesso": True}, 200

    @staticmethod
    def buscar_produto(produto_id):
        produto = ProdutoModel.get_por_id(produto_id)
        if produto:
            return {"dados": produto, "sucesso": True}, 200
        return {"erro": "Produto não encontrado", "sucesso": False}, 404

    @staticmethod
    def criar_produto(dados):
        if not dados:
            return {"erro": "Dados inválidos"}, 400
        if "nome" not in dados:
            return {"erro": "Nome é obrigatório"}, 400
        if "preco" not in dados:
            return {"erro": "Preço é obrigatório"}, 400
        if "estoque" not in dados:
            return {"erro": "Estoque é obrigatório"}, 400

        nome = dados["nome"]
        descricao = dados.get("descricao", "")
        preco = dados["preco"]
        estoque = dados["estoque"]
        categoria = dados.get("categoria", "geral")

        if preco < 0:
            return {"erro": "Preço não pode ser negativo"}, 400
        if estoque < 0:
            return {"erro": "Estoque não pode ser negativo"}, 400
        if len(nome) < 2:
            return {"erro": "Nome muito curto"}, 400
        if len(nome) > 200:
            return {"erro": "Nome muito longo"}, 400

        categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
        if categoria not in categorias_validas:
            return {"erro": f"Categoria inválida. Válidas: {categorias_validas}"}, 400

        novo_id = ProdutoModel.criar(nome, descricao, preco, estoque, categoria)
        return {"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}, 201

    @staticmethod
    def atualizar_produto(produto_id, dados):
        produto_existente = ProdutoModel.get_por_id(produto_id)
        if not produto_existente:
            return {"erro": "Produto não encontrado"}, 404

        if not dados:
            return {"erro": "Dados inválidos"}, 400
        if "nome" not in dados:
            return {"erro": "Nome é obrigatório"}, 400
        if "preco" not in dados:
            return {"erro": "Preço é obrigatório"}, 400
        if "estoque" not in dados:
            return {"erro": "Estoque é obrigatório"}, 400

        nome = dados["nome"]
        descricao = dados.get("descricao", "")
        preco = dados["preco"]
        estoque = dados["estoque"]
        categoria = dados.get("categoria", "geral")

        if preco < 0:
            return {"erro": "Preço não pode ser negativo"}, 400
        if estoque < 0:
            return {"erro": "Estoque não pode ser negativo"}, 400

        ProdutoModel.atualizar(produto_id, nome, descricao, preco, estoque, categoria)
        return {"sucesso": True, "mensagem": "Produto atualizado"}, 200

    @staticmethod
    def deletar_produto(produto_id):
        produto = ProdutoModel.get_por_id(produto_id)
        if not produto:
            return {"erro": "Produto não encontrado"}, 404

        ProdutoModel.deletar(produto_id)
        return {"sucesso": True, "mensagem": "Produto deletado"}, 200

    @staticmethod
    def buscar_produtos(termo, categoria, preco_min, preco_max):
        p_min = float(preco_min) if preco_min is not None else None
        p_max = float(preco_max) if preco_max is not None else None
        resultados = ProdutoModel.buscar(termo, categoria, p_min, p_max)
        return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200
