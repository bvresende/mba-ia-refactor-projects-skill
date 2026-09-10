from src.database.db import get_db

# Constantes de regras comerciais (eliminação de Magic Numbers)
FAIXA_FATURAMENTO_TIER_1 = 10000.0
DESCONTO_TIER_1 = 0.10
FAIXA_FATURAMENTO_TIER_2 = 5000.0
DESCONTO_TIER_2 = 0.05
FAIXA_FATURAMENTO_TIER_3 = 1000.0
DESCONTO_TIER_3 = 0.02

class RelatorioModel:
    @staticmethod
    def gerar_relatorio_vendas():
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(total) FROM pedidos")
        faturamento_raw = cursor.fetchone()[0]
        faturamento = faturamento_raw if faturamento_raw is not None else 0.0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
        pendentes = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
        aprovados = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
        cancelados = cursor.fetchone()[0] or 0

        desconto = 0.0
        if faturamento > FAIXA_FATURAMENTO_TIER_1:
            desconto = faturamento * DESCONTO_TIER_1
        elif faturamento > FAIXA_FATURAMENTO_TIER_2:
            desconto = faturamento * DESCONTO_TIER_2
        elif faturamento > FAIXA_FATURAMENTO_TIER_3:
            desconto = faturamento * DESCONTO_TIER_3

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
        }
