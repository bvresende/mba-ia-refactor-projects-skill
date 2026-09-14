# Architecture Audit Report — code-smells-project

## Metadados do Projeto

- **Projeto:** `code-smells-project`
- **Stack:** Python 3.14 + Flask 3.1.1
- **Data da Auditoria:** 2026-09-10
- **Escopo Analisado:** 4 arquivos analisados (`app.py`, `controllers.py`, `models.py`, `database.py`) | ~784 linhas de código

---

## Sumário Executivo de Achados

| Severidade | Total Encontrado |
| :--- | :---: |
| **CRITICAL** | 3 |
| **HIGH** | 3 |
| **MEDIUM** | 2 |
| **LOW** | 2 |
| **TOTAL** | **10** |

---

## Detalhamento dos Findings

### [CRITICAL] AP-01: Arbitrary SQL Execution Backdoor (ID: CS-01)

- **Arquivo e Linhas:** `app.py:59-78`
- **Descrição do Problema:**
  O endpoint `/admin/query` aceita strings SQL brutas via JSON no corpo da requisição (`dados.get("sql")`) e executa-as diretamente no banco de dados via `cursor.execute(query)` sem qualquer validação ou autenticação. Além disso, o endpoint `/admin/reset-db` (`app.py:47-57`) deleta todas as tabelas sem autenticação.
- **Impacto Arquitetural / Segurança:**
  Permite destruição total do banco de dados, exfiltração arbitrária e injeção remota por qualquer agente não autorizado.
- **Recomendação de Refatoração:**
  Remover os endpoints de backdoor e operações destrutivas da API pública (Receita T-06). Operações de banco devem ser tratadas via migrações ou seeds seguras.

---

### [CRITICAL] AP-02: Mass SQL Injection via String Concatenation (ID: CS-02)

- **Arquivo e Linhas:** `models.py:28, 48-50, 58-60, 68, 92, 109-111, 126-129, 140, 149-150, 155, 158-160, 163-165, 174, 188, 192, 279-281, 289-299`
- **Descrição do Problema:**
  Quase todas as operações no banco de dados SQLite utilizam concatenação direta de strings (`+` ou interpolação) com valores recebidos dos usuários, incluindo login (`email` e `senha`), busca de produtos (`termo`, `categoria`, `preco`), criação e atualização de entidades.
- **Impacto Arquitetural / Segurança:**
  Vulnerabilidade a bypass de autenticação (ex: `' OR '1'='1`), corrupção de dados e vazamento de tabelas completas.
- **Recomendação de Refatoração:**
  Parametrizar todas as instruções SQL utilizando placeholders `?` do SQLite (Receita T-02).

---

### [CRITICAL] AP-03: Hardcoded Credentials & Plaintext Passwords (ID: CS-03)

- **Arquivo e Linhas:** `app.py:7` e `database.py:76-83`
- **Descrição do Problema:**
  A chave de sessão `SECRET_KEY` está hardcoded como `"minha-chave-super-secreta-123"`. Além disso, senhas de usuários administradores e clientes são semeadas em texto puro (`"admin123"`, `"123456"`, `"senha123"`).
- **Impacto Arquitetural / Segurança:**
  Comprometimento de tokens de sessão e credenciais armazenadas sem qualquer proteção criptográfica.
- **Recomendação de Refatoração:**
  Mover segredos para `config/settings.py` com leitura de variáveis de ambiente e aplicar hashing de senha seguro (Receitas T-01 e T-05).

---

### [HIGH] AP-05: God File & Layer Coupling (ID: CS-04)

- **Arquivo e Linhas:** `models.py:1-315` e `controllers.py:1-293`
- **Descrição do Problema:**
  O arquivo `models.py` não é uma camada de modelos pura: ele implementa transações complexas, regras de estoque, cálculos de faturamento e regras de negócio de 4 domínios distintos (Produtos, Usuários, Pedidos e Relatórios). Da mesma forma, `controllers.py` agrupa todos os controladores em um único arquivo de 300 linhas com lógica de notificação fictícia embutida.
- **Impacto Arquitetural / Segurança:**
  Violação massiva do Princípio da Responsabilidade Única (SRP), impossibilidade de testes unitários isolados e alto acoplamento.
- **Recomendação de Refatoração:**
  Decompor em camadas MVC por domínio: `models/`, `controllers/` e `routes/` específicos para `produto`, `usuario`, `pedido` e `relatorio` (Receita T-03).

---

### [HIGH] AP-06: Sensitive Data Exposure in API Endpoints (ID: CS-05)

- **Arquivo e Linhas:** `controllers.py:289` e `models.py:83, 99`
- **Descrição do Problema:**
  O endpoint `/health` expõe publicamente a chave `SECRET_KEY`, ambiente e caminho interno do banco. As funções `get_todos_usuarios` e `get_usuario_por_id` retornam a chave `senha` no dicionário serializado.
- **Impacto Arquitetural / Segurança:**
  Vazamento de informações críticas para qualquer cliente consumidor da API.
- **Recomendação de Refatoração:**
  Sanitizar respostas da API excluindo campos de senha e removendo segredos do health check (Receita T-05).

---

### [HIGH] AP-07: Mutable Global State & Thread Unsafety (ID: CS-06)

- **Arquivo e Linhas:** `database.py:4, 8-10`
- **Descrição do Problema:**
  Uma variável global `db_connection = None` é instanciada com `sqlite3.connect(db_path, check_same_thread=False)`.
- **Impacto Arquitetural / Segurança:**
  O compartilhamento de uma única conexão SQLite entre múltiplas threads em servidores WSGI (Gunicorn/uWSGI) causa race conditions, travamento de locks e inconsistência de dados.
- **Recomendação de Refatoração:**
  Gerenciar conexões por requisição utilizando o contexto de aplicação do Flask (`flask.g`) com teardown automático.

---

### [MEDIUM] AP-08: N+1 Queries in Iterative Loops (ID: CS-06)

- **Arquivo e Linhas:** `models.py:139-166` e `models.py:187-200`
- **Descrição do Problema:**
  Ao criar pedidos ou buscar pedidos de usuários, o código realiza consultas SQL iterativas para cada item e para cada produto relacionado (`cursor2.execute`, `cursor3.execute`), gerando múltiplos round-trips ao banco.
- **Impacto Arquitetural / Segurança:**
  Gargalo severo de performance e latência excessiva em tabelas maiores.
- **Recomendação de Refatoração:**
  Utilizar junções SQL (`JOIN`) para carregar pedidos e itens em consultas consolidadas (Receita T-07).

---

### [MEDIUM] AP-09: Duplicação de Error Handling & Falta de Middleware Global (ID: CS-07)

- **Arquivo e Linhas:** `controllers.py:10-12, 60-62, 95-96, 125-126, 185-186`
- **Descrição do Problema:**
  Todos os métodos do controlador repetem blocos idênticos de `try/except Exception as e:` que executam `print()` e retornam um JSON de erro genérico com status 500. Não existe um middleware centralizado (Global Error Handler) para captura padronizada de falhas no Flask.
- **Impacto Arquitetural / Segurança:**
  Duplicação massiva de código boilerplate, inconsistência de formatos de erro e ausência de captura centralizada de exceções inesperadas.
- **Recomendação de Refatoração:**
  Implementar manipuladores de erro centralizados via `@app.errorhandler` em `src/middlewares/error_handler.py` (Receita T-09).

---

### [LOW] AP-10: Magic Numbers in Business Logic (ID: CS-08)

- **Arquivo e Linhas:** `models.py:256-263`
- **Descrição do Problema:**
  Faixas de desconto e percentuais de faturamento (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) declarados como literais mágicos dispersos na função de relatório.
- **Impacto Arquitetural / Segurança:**
  Dificuldade de manutenção e alteração de regras comerciais.
- **Recomendação de Refatoração:**
  Extrair para constantes nomeadas em `config/constants.py` ou serviço de precificação.

---

### [LOW] AP-10: Inconsistência no Registro de Rotas e Logs Informais (ID: CS-09)

- **Arquivo e Linhas:** `app.py:11-30, 32-45, 56`, `controllers.py:8, 57, 106`
- **Descrição do Problema:**
  Mistura despadronizada de abordagens de roteamento (`app.add_url_rule()` em bloco e `@app.route()` pontuais) e uso de `print()` informais em stdout (`"Listando X produtos"`, `"!!! BANCO DE DADOS RESETADO !!!"`) em vez de um sistema de logging estruturado e configurável.
- **Impacto Arquitetural / Segurança:**
  Dificuldade de rastreamento de requisições em produção e falta de uniformidade semântica no código.
- **Recomendação de Refatoração:**
  Padronizar a organização das rotas através de Blueprints e adotar logging estruturado com níveis adequados.

---

## Recomendações Prioritárias para a Fase 3 (Refatoração)

1. Decompor `models.py` e `controllers.py` em estrutura MVC com pastas `src/models/`, `src/controllers/`, `src/routes/`, `src/config/`, `src/middlewares/`.
2. Parametrizar 100% das queries SQL eliminando todas as vulnerabilidades de injeção.
3. Isolar `SECRET_KEY` em `config/settings.py` e remover backdoors `/admin/query`.
4. Implementar gerenciamento thread-safe de banco via `flask.g` com teardown context.
5. Manter rigorosa paridade em todos os contratos de endpoints HTTP existentes.

---

## Status do Gate de Aprovação (HITL)

- **Fase 2 concluída com sucesso.**
- **Relatório exportado para:** `reports/audit-project-1.md`
- **Aguardando aprovação do usuário para prosseguir para a Fase 3 (Refatoração).**
