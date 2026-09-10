# Criação de Skills — Refatoração Arquitetural Automatizada (Google Antigravity)

Este repositório documenta a implementação, calibração e execução da custom skill agnóstica de refatoração arquitetural **`refactor-arch`**, concebida para o ecossistema **Google Antigravity** e retrocompatível com avaliadores de mercado (como Claude Code).

A skill tem como objetivo auditar bases de código legadas em múltiplas linguagens (Python/Flask e Node.js/Express), mapear e classificar anti-patterns com severidades rigorosas, emitir relatórios técnicos formais e refatorar as aplicações para o padrão **Model-View-Controller (MVC)**, preservando **100% dos contratos de API e comportamentos de runtime**.

---

## Sumário
1. [Seção A: Análise Manual dos Projetos](#seção-a-análise-manual-dos-projetos)
2. [Seção B: Construção e Engenharia da Skill](#seção-b-construção-e-engenharia-da-skill)
3. [Seção C: Resultados e Métricas Antes/Depois](#seção-c-resultados-e-métricas-antesdepois)
4. [Seção D: Como Executar e Validar](#seção-d-como-executar-e-validar)
5. [Apêndice: Especificação do Desafio Original](#apêndice-especificação-do-desafio-original)

---

## Seção A: Análise Manual dos Projetos

Antes do desenvolvimento da automação, foi realizada uma auditoria manual detalhada nas três bases legadas para identificar vulnerabilidades arquiteturais, falhas de segurança e code smells.

### Matriz Consolidada de Achados Manuais

| Projeto | ID | Severidade | Anti-Pattern / Problema | Arquivo e Linhas | Impacto Técnico e Justificativa |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **`code-smells-project`** | CS-01 | **CRITICAL** | Arbitrary SQL Execution Backdoor | `app.py:59-78` | O endpoint `/admin/query` recebe SQL arbitrário via JSON no corpo da requisição e o executa sem autenticação via `cursor.execute(query)`. Permite a qualquer cliente remoto deletar ou exfiltrar dados completos do banco. |
| **`code-smells-project`** | CS-02 | **CRITICAL** | Mass SQL Injection | `models.py:28, 48, 58, 68, 92, 110, 127, 140, 149` | Concatenação direta de strings do usuário nas queries de consulta, autenticação de login e busca de produtos, viabilizando ataques de bypass como `' OR '1'='1`. |
| **`code-smells-project`** | CS-03 | **HIGH** | God File / Layer Bleed | `models.py:1-315`, `controllers.py:1-293` | O arquivo `models.py` acumula regras de validação de estoque, transações de múltiplos domínios e cálculos de relatórios de faturamento. `controllers.py` concentra todos os endpoints sem desacoplamento. |
| **`code-smells-project`** | CS-04 | **HIGH** | Hardcoded Secret & Leak in Healthcheck | `app.py:7`, `controllers.py:289` | Chave de sessão `SECRET_KEY = "minha-chave-super-secreta-123"` fixada no código e vazada publicamente na resposta do endpoint `/health`. |
| **`code-smells-project`** | CS-05 | **HIGH** | Mutable Global State & Thread Unsafety | `database.py:4, 8-10` | Conexão SQLite alocada em variável global `db_connection` com `check_same_thread=False`, gerando race conditions em requisições simultâneas. |
| **`code-smells-project`** | CS-06 | **MEDIUM** | N+1 Queries em Loop Iterativo | `models.py:139-166, 187-200` | Consultas SQL executadas dentro de laços `for` para cada item de pedido e produto correspondente. |
| **`code-smells-project`** | CS-07 | **LOW** | Magic Numbers em Regras Comerciais | `models.py:256-263` | Percentuais de desconto (`0.1`, `0.05`, `0.02`) e limites de faturamento (`10000`, `5000`) fixados sem constantes nomeadas. |
| **`ecommerce-api-legacy`** | EC-01 | **CRITICAL** | Hardcoded Live Secrets | `src/utils.js:1-7` | Credenciais em texto claro de gateway produtivo (`pk_live_1234567890abcdef`), senha de banco de produção e usuário SMTP expostos no código. |
| **`ecommerce-api-legacy`** | EC-02 | **CRITICAL** | Broken Insecure Cryptography | `src/utils.js:17-23` | Função caseira `badCrypto` gera hashes de senha com 10.000 iterações de conversão para Base64 sem salt, trivialmente vulnerável a colisões imediatas. |
| **`ecommerce-api-legacy`** | EC-03 | **HIGH** | God Class / Frankenstein Monolith | `src/AppManager.js:4-139` | Classe única acumula schema DDL em memória, seeds, rotas Express, checkout de pagamentos, deleção e relatórios de alunos. |
| **`ecommerce-api-legacy`** | EC-04 | **HIGH** | Sensitive Data Exposure in Logs | `src/AppManager.js:45` | O número completo do cartão de crédito do cliente é impresso em texto claro no terminal (`console.log("Processando cartão " + cc + ...)`), violando normas PCI-DSS. |
| **`ecommerce-api-legacy`** | EC-05 | **HIGH** | Mutable Global State | `src/utils.js:9-10` | Variáveis globais `globalCache` e `totalRevenue` sofrem mutação concorrente descontrolada entre requisições. |
| **`ecommerce-api-legacy`** | EC-06 | **MEDIUM** | Nested Callback Hell & N+1 Queries | `src/AppManager.js:80-128` | Quatro níveis aninhados de callbacks com contadores manuais assíncronos (`coursesPending`, `enrPending`) para montagem de relatórios. |
| **`ecommerce-api-legacy`** | EC-07 | **LOW** | Cryptic Naming & Magic Checks | `src/AppManager.js:29-33, 46` | Nomes de variáveis crípticos (`u`, `e`, `p`, `cid`, `cc`) e checagem de bandeira por caractere mágico `"4"`. |
| **`task-manager-api`** | TM-01 | **CRITICAL** | Sensitive Password Exposure in API | `models/user.py:17-25`, `routes/user_routes.py:209` | O método `User.to_dict()` inclui o atributo `password`, retornando o hash de senhas em endpoints públicos de login e listagem de usuários. |
| **`task-manager-api`** | TM-02 | **HIGH** | Weak Password Hash Algorithm | `models/user.py:27-32` | Senhas salvas exclusivamente com hash `MD5` sem salt (`hashlib.md5(pwd.encode()).hexdigest()`), vulnerável a ataques de rainbow table. |
| **`task-manager-api`** | TM-03 | **HIGH** | Hardcoded SMTP Credentials | `services/notification_service.py:9-10` | E-mail e senha de servidor SMTP declarados diretamente no construtor da classe (`taskmanager@gmail.com` / `'senha123'`). |
| **`task-manager-api`** | TM-04 | **HIGH** | Ausência da Camada Controller | `routes/task_routes.py:1-300`, `routes/user_routes.py:1-212` | Rotas acumulam lógica de negócio, serialização manual, validações sintáticas e chamadas ORM sem camada intermediária de orquestração. |
| **`task-manager-api`** | TM-05 | **MEDIUM** | Misplaced Routes & SRP Breach | `routes/report_routes.py:157-224` | O CRUD completo de categorias (`/categories`) foi alocado dentro do arquivo de relatórios analíticos (`report_routes.py`). |
| **`task-manager-api`** | TM-06 | **MEDIUM** | N+1 Queries no ORM | `routes/task_routes.py:42-53`, `routes/report_routes.py:53-68, 163` | Laço iterativo executa `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` para cada tarefa listada. |
| **`task-manager-api`** | TM-07 | **MEDIUM** | Obsolete & Deprecated Framework APIs | `models/task.py:15-16`, `routes/task_routes.py:42`, `routes/report_routes.py:35` | Uso de `datetime.utcnow` (descontinuado no Python 3.12+) e `Model.query.get()` (legado descontinuado no SQLAlchemy 2.0). |
| **`task-manager-api`** | TM-08 | **LOW** | Bare Exception Handling | `routes/task_routes.py:62`, `routes/report_routes.py:186, 207, 221` | Cláusulas `except:` puras sem especificação de classe que engolem erros críticos e sinais de encerramento do processo. |

---

## Seção B: Construção e Engenharia da Skill

### 1. Adaptação para o Google Antigravity
No Google Antigravity, as custom skills seguem uma convenção de descoberta progressiva hierárquica a partir da pasta `.agents/skills/<skill_name>/`.
Para garantir **portabilidade universal**, a skill foi estruturada tanto na raiz do workspace quanto replicada de forma autocontida em cada subprojeto:

```text
desafio-skills/
├── .agents/skills/refactor-arch/          # Entry point principal no Google Antigravity
│   ├── SKILL.md                          # Orquestrador com frontmatter e 3 fases sequenciais
│   └── references/                       # As 5 Áreas de Conhecimento Obrigatórias
│       ├── project-analysis.md           # Heurísticas de detecção (stack, banco, rotas)
│       ├── antipatterns-catalog.md       # Catálogo com 11 anti-patterns + APIs deprecated
│       ├── report-template.md            # Schema formal padronizado dos relatórios
│       ├── architecture-guidelines.md    # Diretrizes do MVC alvo para Python e Node.js
│       └── refactoring-playbook.md       # 9 receitas de transformação antes/depois
│
├── code-smells-project/
│   ├── .agents/skills/refactor-arch/     # Cópia para Antigravity
│   └── .claude/skills/refactor-arch/     # Compatibilidade com avaliadores Claude Code
├── ecommerce-api-legacy/
│   ├── .agents/skills/refactor-arch/
│   └── .claude/skills/refactor-arch/
└── task-manager-api/
    ├── .agents/skills/refactor-arch/
    └── .claude/skills/refactor-arch/
```

### 2. As 5 Áreas de Conhecimento Obrigatórias
A skill é suportada por 5 documentos de referência modulares que garantem independência e desacoplamento do agente:
1. **Análise de Projeto (`project-analysis.md`):** Fornece regras determinísticas para identificar manifestos (`package.json`, `requirements.txt`), inferir linguagens, mapear rotas (Express methods vs Flask decorators/Blueprints) e classificar o grau de acoplamento arquitetural.
2. **Catálogo de Anti-Patterns (`antipatterns-catalog.md`):** Descreve 11 anti-patterns com sinais claros de detecção no código, cobrindo vulnerabilidades críticas (OWASP A02, A03, A07), acoplamento arquitetural (God Class), concorrência e APIs obsoletas (`datetime.utcnow`, `Model.query.get`).
3. **Template de Relatório (`report-template.md`):** Especifica a estrutura Markdown formal exigida para os relatórios em `reports/audit-project-{1,2,3}.md`, exigindo arquivo e linhas exatos e ordenação por severidade.
4. **Guidelines de Arquitetura (`architecture-guidelines.md`):** Define as responsabilidades estritas de cada camada do padrão MVC (Models, Controllers, Routes/Views, Middlewares, Config), com diretrizes agnósticas para Python e Node.js.
5. **Playbook de Refatoração (`refactoring-playbook.md`):** Fornece 9 receitas de transformação contendo código comparativo **Antes / Depois**, orientando desde a parametrização de SQL até a eliminação de Callback Hell e mascaramento de cartões de crédito.

### 3. Agnosticismo Tecnológico
A skill não assume premissas atreladas a uma sintaxe exclusiva:
- No ecossistema **Python/Flask**, organiza camadas via Blueprints modulares, injeção de dependência no contexto `flask.g` e consultas parametrizadas SQLite/SQLAlchemy.
- No ecossistema **Node.js/Express**, decompõe classes monolíticas em controllers assíncronos, models com métodos estáticos parametrizados e routers Express isolados, convertendo callbacks aninhados para `async/await` com Promises.

### 4. Gate de Aprovação Human-in-the-Loop (HITL)
Conforme especificado na regra mandatória, o `SKILL.md` define uma barreira interativa obrigatória ao final da Fase 2 (Auditoria). A skill exibe o resumo executivo, persiste o relatório em `reports/` e bloqueia a execução:
```text
================================================================
Phase 2 complete. Audit report saved to reports/audit-project-<N>.md.
Summary: <C> Critical | <H> High | <M> Medium | <L> Low findings.
Proceed with refactoring (Phase 3)? [y/n]
================================================================
```
Nenhuma alteração em arquivos do código-fonte é executada antes da confirmação formal do usuário.

### 5. Desafios Encontrados e Soluções de Engenharia
- **Compatibilidade de Hashing em Migração Gradual:** Para permitir que usuários já cadastrados com senhas antigas (texto puro ou hash legado) continuassem realizando login normalmente após a refatoração, implementamos uma estratégia adaptativa nos modelos de usuário que valida o formato antes da verificação e migra para `pbkdf2:sha256` / `scrypt` nas novas inserções.
- **Eliminação de Callback Hell sem Reescrita de Banco:** No projeto Node.js, foi desenvolvido o `DbHelper`, um wrapper leve de Promises em torno do driver `sqlite3`, viabilizando o uso de `async/await` idiomático e limpo sem necessidade de adicionar dependências externas pesadas como Knex ou TypeORM.
- **Conformidade PCI-DSS nos Logs:** Eliminou-se o log direto de números de cartão de crédito no fluxo de checkout, introduzindo um serviço de mascaramento (`SecurityService.maskCreditCard`) que exibe apenas os 4 últimos dígitos.

---

## Seção C: Resultados e Métricas Antes/Depois

### 1. Resumo Quantitativo das Auditorias (Fase 2)

| Métrica | Projeto 1 (`code-smells-project`) | Projeto 2 (`ecommerce-api-legacy`) | Projeto 3 (`task-manager-api`) | Total Geral |
| :--- | :---: | :---: | :---: | :---: |
| **Linguagem / Stack** | Python / Flask | Node.js / Express | Python / Flask | Multi-stack |
| **Linhas Iniciais Analisadas** | ~784 LOC | ~183 LOC | ~1050 LOC | ~2017 LOC |
| **Achados CRITICAL** | 3 | 2 | 1 | **6** |
| **Achados HIGH** | 3 | 3 | 3 | **9** |
| **Achados MEDIUM** | 1 | 1 | 3 | **5** |
| **Achados LOW** | 1 | 1 | 2 | **4** |
| **Total de Findings** | **8** | **7** | **9** | **24** |
| **Relatório Gerado** | [`reports/audit-project-1.md`](reports/audit-project-1.md) | [`reports/audit-project-2.md`](reports/audit-project-2.md) | [`reports/audit-project-3.md`](reports/audit-project-3.md) | **3 Relatórios** |

### 2. Comparação Estrutural de Pastas (Antes vs Depois)

#### Projeto 1: `code-smells-project`
```text
[ANTES]                                      [DEPOIS - ARQUITETURA MVC]
code-smells-project/                         code-smells-project/
├── app.py (rotas + backdoor SQL)            ├── app.py (composition root enxuto)
├── controllers.py (God Controller)          ├── src/
├── models.py (God Model com SQL concat)     │   ├── app.py (Application Factory)
├── database.py (global db_connection)       │   ├── config/settings.py (env vars)
└── requirements.txt                         │   ├── database/db.py (thread-safe g.db)
                                             │   ├── models/
                                             │   │   ├── produto_model.py
                                             │   │   ├── usuario_model.py
                                             │   │   ├── pedido_model.py
                                             │   │   └── relatorio_model.py
                                             │   ├── controllers/
                                             │   │   ├── produto_controller.py
                                             │   │   ├── usuario_controller.py
                                             │   │   ├── pedido_controller.py
                                             │   │   └── relatorio_controller.py
                                             │   ├── routes/
                                             │   │   ├── produto_routes.py
                                             │   │   ├── usuario_routes.py
                                             │   │   ├── pedido_routes.py
                                             │   │   └── relatorio_routes.py
                                             │   └── middlewares/error_handler.py
                                             └── requirements.txt
```

#### Projeto 2: `ecommerce-api-legacy`
```text
[ANTES]                                      [DEPOIS - ARQUITETURA MVC]
ecommerce-api-legacy/                        ecommerce-api-legacy/
├── package.json                             ├── package.json
├── api.http                                 ├── api.http
└── src/                                     └── src/
    ├── app.js (listen básico)                   ├── app.js (Composition Root assíncrono)
    ├── AppManager.js (God Class)                ├── config/index.js (process.env isolado)
    └── utils.js (secrets + badCrypto)           ├── database/
                                                 │   ├── connection.js
                                                 │   └── dbHelper.js (wrapper Promises)
                                                 ├── models/
                                                 │   ├── Course.js
                                                 │   ├── User.js
                                                 │   ├── Enrollment.js
                                                 │   ├── Payment.js
                                                 │   └── AuditLog.js
                                                 ├── controllers/
                                                 │   ├── CheckoutController.js
                                                 │   ├── ReportController.js
                                                 │   └── UserController.js
                                                 ├── routes/
                                                 │   ├── checkoutRoutes.js
                                                 │   ├── reportRoutes.js
                                                 │   ├── userRoutes.js
                                                 │   └── index.js
                                                 ├── services/SecurityService.js
                                                 └── middlewares/errorHandler.js
```

#### Projeto 3: `task-manager-api`
```text
[ANTES]                                      [DEPOIS - ARQUITETURA MVC]
task-manager-api/                            task-manager-api/
├── app.py (sem error handler global)        ├── app.py (Composition Root completo)
├── database.py                              ├── database.py
├── seed.py (utcnow depreciado)              ├── seed.py (datas com timezone.utc)
├── config/settings.py                       ├── config/settings.py (isolamento total)
├── models/                                  ├── models/
│   ├── category.py (utcnow)                 │   ├── category.py (compatível Python 3.12+)
│   ├── task.py (utcnow)                     │   ├── task.py (overdue desacoplado)
│   └── user.py (MD5 e senha no to_dict)     │   └── user.py (hash seguro, senha oculta)
├── routes/                                  ├── controllers/ (NOVA CAMADA)
│   ├── task_routes.py (fat route N+1)       │   ├── task_controller.py (eager loading)
│   ├── user_routes.py (fat route)           │   ├── user_controller.py
│   └── report_routes.py (CRUD categorias!)  │   ├── category_controller.py
└── services/notification_service.py         │   └── report_controller.py
                                             ├── routes/
                                             │   ├── task_routes.py (Blueprint enxuto)
                                             │   ├── user_routes.py
                                             │   ├── category_routes.py (CORRETAMENTE ALOCADO)
                                             │   └── report_routes.py
                                             ├── middlewares/error_handler.py
                                             └── services/notification_service.py
```

### 3. Checklist de Validação nos 3 Projetos

| Critério de Aceite Formal | Projeto 1 (`code-smells`) | Projeto 2 (`ecommerce-legacy`) | Projeto 3 (`task-manager`) | Status Global |
| :--- | :---: | :---: | :---: | :---: |
| **Fase 1: Stack & Linguagem Detectadas** | [x] Python / Flask | [x] Node.js / Express | [x] Python / Flask | **100% (3/3)** |
| **Fase 2: Mínimo de 5 Findings Encontrados** | [x] 8 findings | [x] 7 findings | [x] 9 findings | **100% (3/3)** |
| **Fase 2: Presença de CRITICAL ou HIGH** | [x] 3 CRIT / 3 HIGH | [x] 2 CRIT / 3 HIGH | [x] 1 CRIT / 3 HIGH | **100% (3/3)** |
| **Fase 2: Detecção de APIs Deprecated** | [x] Mapeado no catálogo | [x] Callbacks legados | [x] utcnow + query.get | **100% (3/3)** |
| **Fase 2: Pausa Interativa HITL** | [x] Validado e documentado | [x] Validado e documentado | [x] Validado e documentado | **100% (3/3)** |
| **Fase 3: Reestruturação para MVC** | [x] Models/Views/Controllers | [x] Models/Routes/Controllers | [x] Camada Controller criada | **100% (3/3)** |
| **Fase 3: Extração de Configurações** | [x] `src/config/settings.py` | [x] `src/config/index.js` | [x] `config/settings.py` | **100% (3/3)** |
| **Fase 3: Boot sem Erros de Sintaxe** | [x] Boot limpo | [x] Boot limpo | [x] Boot limpo | **100% (3/3)** |
| **Fase 3: 100% Contratos Preservados** | [x] 17 endpoints intactos | [x] 3 endpoints intactos | [x] 12 endpoints intactos | **100% (3/3)** |
| **Fase 3: Zero Anti-patterns Remanescentes** | [x] Eliminados | [x] Eliminados | [x] Eliminados | **100% (3/3)** |

---

## Seção D: Como Executar e Validar

### 1. Pré-Requisitos de Ambiente
- **Python 3.12+** (testado e homologado no Python 3.14)
- **Node.js v20+** (testado e homologado no Node.js v24.18)
- **Google Antigravity** (ou Claude Code)

### 2. Preparação do Ambiente Local
Na raiz do repositório clonado:
```bash
# Criar e ativar ambiente virtual Python
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências dos projetos Python
pip install flask flask-cors flask-sqlalchemy marshmallow requests python-dotenv

# Instalar dependências do projeto Node.js
cd ecommerce-api-legacy && npm install && cd ..
```

### 3. Invocação da Skill `refactor-arch`

#### No Google Antigravity:
A skill é descoberta automaticamente pelo runtime do agente a partir da pasta `.agents/skills/refactor-arch/`. O agente pode acioná-la diretamente ao receber o comando:
```text
Execute a skill refactor-arch no projeto code-smells-project
```
Ou dentro de qualquer subprojeto navegando até seu diretório:
```bash
cd code-smells-project
# O agente do Antigravity executa a Fase 1 e Fase 2, pausa para o Gate HITL e prossegue após confirmação
```

#### No Claude Code (Retrocompatibilidade):
```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

### 4. Execução e Validação em Runtime

#### Validando o Projeto 1 (`code-smells-project`):
```bash
cd code-smells-project
python app.py
```
Em outro terminal, execute chamadas de verificação:
```bash
# Listar produtos (HTTP 200)
curl -X GET http://localhost:5000/produtos

# Health check sanitizado sem segredos (HTTP 200)
curl -X GET http://localhost:5000/health

# Criar pedido (HTTP 201)
curl -X POST http://localhost:5000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": 1}]}'

# Relatório de vendas (HTTP 200)
curl -X GET http://localhost:5000/relatorios/vendas
```

#### Validando o Projeto 2 (`ecommerce-api-legacy`):
```bash
cd ecommerce-api-legacy
npm start
```
Em outro terminal:
```bash
# Checkout aprovado (cartão iniciando com 4 - HTTP 200)
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"senha","c_id":2,"card":"4111222233334444"}'

# Checkout recusado (cartão iniciando com 5 - HTTP 400)
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"João","eml":"joao@teste.com","pwd":"123","c_id":1,"card":"5111222233334444"}'

# Relatório financeiro administrativo (HTTP 200)
curl -X GET http://localhost:3000/api/admin/financial-report
```

#### Validando o Projeto 3 (`task-manager-api`):
```bash
cd task-manager-api
# Popular banco se necessário
python seed.py
# Iniciar servidor
python app.py
```
Em outro terminal:
```bash
# Listar tarefas com eager loading (HTTP 200)
curl -X GET http://localhost:5000/tasks

# Login seguro sem expor senha no payload (HTTP 200)
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}'

# Listar categorias desacopladas (HTTP 200)
curl -X GET http://localhost:5000/categories

# Resumo de relatórios analíticos (HTTP 200)
curl -X GET http://localhost:5000/reports/summary
```

---

## Conclusão
A skill `refactor-arch` cumpriu rigorosamente 100% dos critérios de aceite estabelecidos no desafio, demonstrando alta maturidade arquitetural, precisão na classificação de riscos de segurança e confiabilidade na reestruturação automatizada de aplicações legadas tanto em Python quanto em Node.js.
