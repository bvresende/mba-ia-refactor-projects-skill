# Catálogo de Anti-Patterns e Code Smells Arquiteturais

Este catálogo define os anti-patterns, falhas de segurança e code smells que a skill `refactor-arch` deve auditar na **Fase 2 (Architecture Audit)**. Cada anti-pattern possui classificação de severidade rigorosa, heurísticas de detecção no código-fonte e recomendação de remediação.

---

## Tabela Resumo do Catálogo

| ID | Anti-Pattern | Severidade | Categoria Primária |
| :--- | :--- | :--- | :--- |
| **AP-01** | Arbitrary SQL Execution / Remote Backdoor | **CRITICAL** | Segurança / Backdoor |
| **AP-02** | SQL Injection via String Concatenation | **CRITICAL** | Segurança / OWASP A03 |
| **AP-03** | Hardcoded Secrets & Credentials Exposure | **CRITICAL** | Segurança / OWASP A07 |
| **AP-04** | Broken / Insecure Cryptographic Hash | **CRITICAL** | Segurança / OWASP A02 |
| **AP-05** | God Class / God File (Monolithic Coupling) | **HIGH** | Arquitetura / SRP |
| **AP-06** | Sensitive Data Exposure in API Payloads | **HIGH** | Segurança / Privacidade |
| **AP-07** | Mutable Global State & Concurrency Race Condition | **HIGH** | Arquitetura / Concorrência |
| **AP-08** | N+1 Queries in Iterative Loops | **MEDIUM** | Performance / Banco de Dados |
| **AP-09** | Architectural Layer Bleed & Misplaced Responsibilities | **MEDIUM** | Arquitetura / MVC |
| **AP-10** | Magic Numbers & Hardcoded Business Constants | **LOW** | Qualidade / Manutenibilidade |
| **AP-11** | Obsolete & Deprecated Framework APIs | **LOW / MEDIUM** | Obsolescência Tecnológica |

---

## 1. Detalhamento dos Anti-Patterns

### [CRITICAL] AP-01: Arbitrary SQL Execution / Remote Backdoor

- **Sinais de Detecção:**
  - Rotas recebendo queries em formato texto bruto do cliente via `request.get_json().get('sql')` ou `req.body.query` e passando diretamente para `cursor.execute(query)` ou `db.run(query)`.
  - Ausência de autenticação ou autorização em endpoints de execução de DDL/DML destrutivos (ex: `/admin/query`, `/admin/reset-db`).
- **Impacto:** Destruição completa da base de dados, roubo em massa e escalação remota de privilégios.
- **Recomendação:** Remover o endpoint inseguro completamente ou substituí-lo por operações controladas via scripts administrativos/migrações.

---

### [CRITICAL] AP-02: SQL Injection via String Concatenation

- **Sinais de Detecção:**
  - Montagem de instruções SQL através de concatenação (`+`), interpolação ou f-strings com parâmetros não sanitizados:
    - Python: `cursor.execute("SELECT * FROM users WHERE id = " + str(id))` ou `f"SELECT ... WHERE nome = '{nome}'"`
    - Node.js: `db.get("SELECT ... WHERE email = '" + email + "'")`
- **Impacto:** Violação de integridade, contorno de autenticação (ex: `' OR '1'='1`) e exfiltração de dados.
- **Recomendação:** Utilizar queries parametrizadas (placeholders `?` no SQLite, `%s` no Postgres) ou abstrações seguras de ORM.

---

### [CRITICAL] AP-03: Hardcoded Secrets & Credentials Exposure

- **Sinais de Detecção:**
  - Chaves de criptografia, segredos de sessão (`SECRET_KEY`), senhas de banco de dados ou chaves de gateway de pagamento (`pk_live_`, `sk_live_`) gravadas estaticamente em arquivos de código.
- **Impacto:** Comprometimento do ambiente e vazamento em repositórios de versionamento.
- **Recomendação:** Isolar todas as variáveis de configuração em um módulo `config/` que consulte variáveis de ambiente (`os.getenv`, `process.env`).

---

### [CRITICAL] AP-04: Broken / Insecure Cryptographic Hash

- **Sinais de Detecção:**
  - Armazenamento de senhas em texto puro (`admin123`, `senha123`).
  - Hashing de senhas utilizando algoritmos criptograficamente quebrados (`MD5`, `SHA1`) sem salt, ou funções caseiras (ex: loops manuais com `Buffer.from(pwd).toString('base64')`).
- **Impacto:** Quebra trivial de senhas através de rainbow tables ou ataques de dicionário.
- **Recomendação:** Utilizar bibliotecas criptográficas padronizadas da indústria (`werkzeug.security` com PBKDF2/scrypt ou `bcrypt`).

---

### [HIGH] AP-05: God Class / God File (Monolithic Coupling)

- **Sinais de Detecção:**
  - Arquivo ou classe única centralizando criação de tabelas (DDL), sementes (DML), registro de rotas, manipulação de conexões, regras de negócio e formatação de resposta (`AppManager.js`, `models.py` com múltiplos domínios).
  - Classes ou módulos com alta complexidade ciclomática e mais de 300 linhas de responsabilidades mistas.
- **Impacto:** Impossibilidade de realizar testes de unidade isolados, alto risco de regressão a cada alteração e impossibilidade de paralelismo de desenvolvimento.
- **Recomendação:** Decompor em camadas estritas seguindo o padrão MVC: Models específicos por domínio, Controllers de orquestração e Routers modulares.

---

### [HIGH] AP-06: Sensitive Data Exposure in API Payloads

- **Sinais de Detecção:**
  - Métodos de serialização (`to_dict()`, `JSON.stringify()`) que incluem campos de credenciais (`password`, `senha`, `token_secreto`) no JSON de resposta.
  - Endpoints de saúde (`/health`) que retornam dados confidenciais de infraestrutura (chaves secretas, caminhos de arquivo, credenciais).
- **Impacto:** Vazamento de informações sigilosas para usuários finais e atacantes.
- **Recomendação:** Implementar data mappers / schemas de serialização explícitos (ex: `fields_to_exclude=['password']`) e sanitizar outputs de monitoramento.

---

### [HIGH] AP-07: Mutable Global State & Concurrency Race Condition

- **Sinais de Detecção:**
  - Conexões de banco de dados alocadas em variáveis globais com `check_same_thread=False` sem controle de pool ou locks thread-safe.
  - Objetos globais mutáveis (`globalCache = {}`, `totalRevenue = 0`) manipulados diretamente por requisições concorrentes.
- **Impacto:** Race conditions, corrupção de memória de banco em ambientes multithread (Gunicorn/uWSGI) e dados inconsistentes entre requisições.
- **Recomendação:** Utilizar conexões vinculadas ao ciclo de vida da requisição (ex: `flask.g` ou pool de conexões gerenciado) e serviços com injeção de dependência.

---

### [MEDIUM] AP-08: N+1 Queries in Iterative Loops

- **Sinais de Detecção:**
  - Execução de consultas SQL ou chamadas ORM dentro de loops iterativos (`for`, `forEach`, `while`) para obter registros filhos de uma lista pai:
    - Ex: Buscar itens de pedido para cada pedido em loop, ou buscar autor de cada tarefa via `User.query.get(task.user_id)`.
  - Aninhamento excessivo de callbacks para montagem de relatórios relacionais.
- **Impacto:** Degradação severa de performance e latência excessiva no banco de dados.
- **Recomendação:** Utilizar cláusulas `JOIN`, eager loading (`joinedload` no SQLAlchemy) ou queries agregadas com `GROUP BY`.

---

### [MEDIUM] AP-09: Architectural Layer Bleed & Misplaced Responsibilities

- **Sinais de Detecção:**
  - Rotas de CRUD de uma entidade alocadas no arquivo de rotas de outra entidade ou de relatórios (ex: CRUD de categorias dentro de `report_routes.py`).
  - Lógica de domínio pesada (como validação de estoque, regras de precificação e envio de notificações) implementada diretamente dentro de funções de rota ou views HTTP.
  - Models executando parsing de objetos de requisição HTTP (`flask.request`).
- **Impacto:** Dificuldade de localização de regras, duplicação de lógica e violação de SRP.
- **Recomendação:** Realocar endpoints para seus respectivos blueprints/routers de domínio e transferir a orquestração para Controllers dedicados.

---

### [LOW] AP-10: Magic Numbers & Hardcoded Business Constants

- **Sinais de Detecção:**
  - Números e faixas de negócio fixos distribuídos no meio do código (ex: taxas de desconto `0.1`, `0.05`, `0.02`, limites de faturamento `10000`, `5000`, bandeiras de cartão `"4"`).
- **Impacto:** Dificuldade de atualização de regras comerciais e perda de clareza semântica.
- **Recomendação:** Isolar valores numéricos em constantes nomeadas ou enums corporativos.

---

### [LOW / MEDIUM] AP-11: Obsolete & Deprecated Framework APIs

- **Sinais de Detecção e Equivalentes Modernos:**

| Stack | API Deprecated / Obsoleta | Razão da Descontinuação | Equivalente Moderno Recomendado |
| :--- | :--- | :--- | :--- |
| **Python Standard** | `datetime.utcnow()` | Descontinuado no Python 3.12+ (sem fuso horário explícito). | `datetime.now(timezone.utc)` |
| **SQLAlchemy** | `Model.query.get(id)` | Descontinuado no padrão SQLAlchemy 2.0 (Query legado). | `db.session.get(Model, id)` |
| **Node.js Express** | Callback Hell aninhado sem Promises | Código ilegível e propenso a vazamento de erros. | `async / await` com Promises ou wrappers |
| **Python Flask** | `except:` puro (Bare except) | Captura `KeyboardInterrupt` e `SystemExit`, escondendo bugs. | `except Exception as e:` com logging estruturado |
