# Architecture Audit Report — task-manager-api

## Metadados do Projeto
- **Projeto:** `task-manager-api`
- **Stack:** Python 3.14 + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
- **Data da Auditoria:** 2026-09-10
- **Escopo Analisado:** 9 arquivos analisados (`app.py`, `database.py`, `models/*`, `routes/*`, `services/*`, `utils/*`) | ~1050 linhas de código

---

## Sumário Executivo de Achados

| Severidade | Total Encontrado |
| :--- | :---: |
| **CRITICAL** | 1 |
| **HIGH** | 3 |
| **MEDIUM** | 3 |
| **LOW** | 2 |
| **TOTAL** | **9** |

---

## Detalhamento dos Findings

### [CRITICAL] AP-06: Sensitive Data Exposure in API Payloads (ID: TM-01)
- **Arquivo e Linhas:** `models/user.py:17-25` e `routes/user_routes.py:209`
- **Descrição do Problema:**
  O método `User.to_dict()` expõe o atributo `password` no dicionário retornado. Consequentemente, endpoints públicos como `POST /login`, `GET /users/<id>` e `POST /users` enviam o hash da senha do usuário diretamente na resposta JSON para o cliente.
- **Impacto Arquitetural / Segurança:**
  Vazamento flagrante de credenciais de usuários e administradores da aplicação.
- **Recomendação de Refatoração:**
  Sanitizar o método de serialização `to_dict()` para excluir o campo `password` das respostas por padrão (Receita T-05).

---

### [HIGH] AP-04: Broken / Insecure Cryptographic Hash (ID: TM-02)
- **Arquivo e Linhas:** `models/user.py:27-32`
- **Descrição do Problema:**
  O armazenamento e validação de senhas são realizados com o algoritmo `MD5` (`hashlib.md5(pwd.encode()).hexdigest()`), sem uso de salt ou custo computacional iterativo.
- **Impacto Arquitetural / Segurança:**
  O algoritmo MD5 é criptograficamente vulnerável a colisões e ataques de dicionário através de rainbow tables em frações de segundo.
- **Recomendação de Refatoração:**
  Migrar para algoritmos modernos e seguros suportados pelo `werkzeug.security` (`generate_password_hash` / `check_password_hash`) (Receita T-05).

---

### [HIGH] AP-03: Hardcoded Credentials & Plaintext Secrets (ID: TM-03)
- **Arquivo e Linhas:** `app.py:13` e `services/notification_service.py:9-10`
- **Descrição do Problema:**
  A chave de sessão `SECRET_KEY` está fixada no `app.py` (`'super-secret-key-123'`), e as credenciais do servidor SMTP (`taskmanager@gmail.com` / `'senha123'`) estão declaradas no construtor da classe `NotificationService`.
- **Impacto Arquitetural / Segurança:**
  Vazamento de credenciais de e-mail e segredos de assinatura em repositórios de código.
- **Recomendação de Refatoração:**
  Isolar configurações no módulo `config/settings.py` alimentado por variáveis de ambiente (Receita T-01).

---

### [HIGH] AP-05: Missing Controller Layer & Fat Routes (ID: TM-04)
- **Arquivo e Linhas:** `routes/task_routes.py:1-300` e `routes/user_routes.py:1-212`
- **Descrição do Problema:**
  Embora o projeto possua separação de pastas (`models/`, `routes/`), não existe a camada `controllers/`. As funções de rota acumulam regras de negócio, validações de formato, serialização manual em dicionários e chamadas de persistência diretamente no contexto HTTP.
- **Impacto Arquitetural / Segurança:**
  Acoplamento severo entre regras de domínio e a camada de transporte Flask, impossibilitando reuso e testes unitários.
- **Recomendação de Refatoração:**
  Introduzir a camada `controllers/` (`TaskController`, `UserController`, `CategoryController`, `ReportController`) e manter os Blueprints focados exclusivamente em roteamento e status HTTP (Receita T-03).

---

### [MEDIUM] AP-09: Misplaced Routes & Single Responsibility Breach (ID: TM-05)
- **Arquivo e Linhas:** `routes/report_routes.py:157-224`
- **Descrição do Problema:**
  As rotas de gerenciamento de categorias (`GET /categories`, `POST /categories`, `PUT /categories/<id>`, `DELETE /categories/<id>`) foram implementadas dentro de `report_routes.py`.
- **Impacto Arquitetural / Segurança:**
  Dificuldade de localização de endpoints, confusão semântica de domínios e quebra do princípio da responsabilidade única.
- **Recomendação de Refatoração:**
  Extrair as operações de categoria para seu próprio Blueprint e Controller (`category_routes.py` e `CategoryController`).

---

### [MEDIUM] AP-08: N+1 Database Queries in Iterations (ID: TM-06)
- **Arquivo e Linhas:** `routes/task_routes.py:42-53`, `routes/report_routes.py:53-68, 163`
- **Descrição do Problema:**
  No endpoint `GET /tasks`, para cada tarefa é executada uma query `User.query.get(t.user_id)` e `Category.query.get(t.category_id)`. Em `summary_report()`, consultas são disparadas iterativamente por usuário e por categoria.
- **Impacto Arquitetural / Segurança:**
  Sobrecarga exponencial do banco de dados proporcional ao volume de registros.
- **Recomendação de Refatoração:**
  Utilizar eager loading (`joinedload`) no SQLAlchemy ou junções relacionais diretas (Receita T-07).

---

### [MEDIUM] AP-11: Deprecated Framework APIs (ID: TM-07)
- **Arquivo e Linhas:** `models/task.py:15-16`, `models/user.py:14`, `routes/task_routes.py:42`, `routes/report_routes.py:35`
- **Descrição do Problema:**
  Uso intensivo de `datetime.utcnow` (descontinuado no Python 3.12+) e da interface legada `Model.query.get()` (descontinuada no padrão SQLAlchemy 2.0).
- **Impacto Arquitetural / Segurança:**
  Emissão de warnings de descontinuação e incompatibilidade futura com versões recentes das bibliotecas.
- **Recomendação de Refatoração:**
  Substituir por `datetime.now(timezone.utc)` e `db.session.get(Model, id)` (Receita T-08).

---

### [LOW] AP-10: Bare Exception Handling (ID: TM-08)
- **Arquivo e Linhas:** `routes/task_routes.py:62`, `routes/report_routes.py:186, 207, 221`, `routes/user_routes.py:130, 149`
- **Descrição do Problema:**
  Uso de cláusulas `except:` puras engolindo exceções de sistema (`KeyboardInterrupt`, `SystemExit`) e mascarando bugs sem rastreamento de stack trace.
- **Impacto Arquitetural / Segurança:**
  Dificuldade extrema de depuração em produção.
- **Recomendação de Refatoração:**
  Adotar tratamento centralizado de exceções via Global Error Handler (Receita T-09).

---

### [LOW] AP-10: In-Memory Volatile Notification State (ID: TM-09)
- **Arquivo e Linhas:** `services/notification_service.py:6, 31-36, 43-48`
- **Descrição do Problema:**
  O histórico de notificações é armazenado em uma lista em memória volátil da classe (`self.notifications = []`), sendo perdido a cada reinicialização ou requisição em workers distintos.
- **Impacto Arquitetural / Segurança:**
  Perda de dados de notificação entre processos concorrentes.
- **Recomendação de Refatoração:**
  Isolar o serviço de notificações com suporte a logger ou persistência.

---

## Recomendações Prioritárias para a Fase 3 (Refatoração)
1. Criar a camada `controllers/` desacoplando as rotas de regras de negócio.
2. Mover as rotas de categorias para `category_routes.py` e `CategoryController`.
3. Sanitizar `to_dict()` para remover senhas de respostas da API e atualizar para hash seguro.
4. Isolar credenciais SMTP e `SECRET_KEY` em `config/settings.py`.
5. Substituir APIs deprecated (`datetime.now(timezone.utc)` e `db.session.get`).
6. Resolver queries N+1 usando `joinedload`.

---

## Status do Gate de Aprovação (HITL)
- **Fase 2 concluída com sucesso.**
- **Relatório exportado para:** `reports/audit-project-3.md`
- **Aguardando aprovação do usuário para prosseguir para a Fase 3 (Refatoração).**
