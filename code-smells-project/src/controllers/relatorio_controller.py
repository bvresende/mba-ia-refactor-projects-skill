from src.models.relatorio_model import RelatorioModel
from src.database.db import get_db

class RelatorioController:
    @staticmethod
    def relatorio_vendas():
        relatorio = RelatorioModel.gerar_relatorio_vendas()
        return {"dados": relatorio, "sucesso": True}, 200

    @staticmethod
    def health_check():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0] or 0

        # Sanitizado: segredos internos removidos
        return {
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": produtos,
                "usuarios": usuarios,
                "pedidos": pedidos
            },
            "versao": "1.0.0",
            "ambiente": "producao"
        }, 200
