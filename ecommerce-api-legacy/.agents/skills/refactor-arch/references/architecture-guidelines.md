# Diretrizes Arquiteturais para o Padrão MVC

Este documento estabelece as regras e restrições arquiteturais para a reestruturação das aplicações para o padrão **Model-View-Controller (MVC)** durante a **Fase 3 (Refactoring)** da skill `refactor-arch`.

---

## 1. Visão Geral da Arquitetura Alvo

A meta de refatoração é migrar qualquer monolito ou base desestruturada para uma separação clara de responsabilidades, organizada em camadas estritas e desacopladas:

```text
src/ (ou raiz estruturada)
├── config/             # Configurações do ambiente, segredos e constantes
├── models/             # Abstração de dados, entidades, schemas e persistência
├── controllers/        # Orquestração do fluxo de negócio e casos de uso
├── routes/ (ou views/) # Definição de endpoints HTTP e mapeamento de requisições
├── middlewares/        # Tratamento centralizado de erros, logs e segurança
└── app.py (ou app.js)  # Composition Root (bootstrapping e injeção)
```

---

## 2. Responsabilidades por Camada

### 2.1 Camada Model (`models/`)
- **O que FAZ:**
  - Define o schema dos dados (tabelas, colunas, relacionamentos e tipos).
  - Encapsula operações de banco de dados (CRUD, transações, queries parametrizadas).
  - Define métodos de serialização segura (ex: `to_dict()`) com sanitização obrigatória de campos confidenciais (exclusão de `password`, `hash`, etc.).
  - Aplica regras de invariância de dados e validações intrínsecas da entidade.
- **O que NÃO FAZ:**
  - NUNCA acessa objetos de requisição/resposta HTTP (`request`, `req`, `res`, `jsonify`).
  - NUNCA contém lógicas de orquestração externa (como envio de e-mails ou chamadas HTTP a gateways).

### 2.2 Camada Controller (`controllers/`)
- **O que FAZ:**
  - Orquestra o fluxo de execução entre modelos, serviços e regras de negócio.
  - Recebe dados limpos da camada de rotas e aciona os métodos adequados dos models.
  - Realiza validações de regras de negócio (ex: checagem de saldo, estoque disponível, transição de status).
  - Retorna estruturas de dados puras ou tuplas com status code para a camada de visualização/rotas.
- **O que NÃO FAZ:**
  - NUNCA executa queries SQL diretas ou chamadas de banco de baixo nível (`cursor.execute()`, `db.run()`).
  - NUNCA acopla acoplamentos desnecessários com o protocolo HTTP além do estritamente necessário.

### 2.3 Camada Routes / Views (`routes/` ou `views/`)
- **O que FAZ:**
  - Declara os endpoints da API (caminhos de URL e verbos HTTP: `GET`, `POST`, `PUT`, `DELETE`).
  - Extrai dados da requisição (`params`, `query`, `body`, headers).
  - Executa validações sintáticas preliminares (ex: campos obrigatórios presentes, formatos básicos).
  - Delega a execução para a função correspondente do Controller.
  - Serializa o retorno em formato padronizado (JSON) e responde com o código HTTP adequado (200, 201, 400, 404, 500).
- **O que NÃO FAZ:**
  - NUNCA contém regras de negócio ou lógica transacional.
  - NUNCA consulta o banco de dados diretamente.

### 2.4 Camada de Configuração (`config/`)
- **Regras:**
  - Nenhuma credencial ou chave secreta pode estar hardcoded no código.
  - Lê de variáveis de ambiente (`os.getenv` em Python, `process.env` em Node.js) com defaults seguros para desenvolvimento local.
  - Centraliza caminhos de arquivo, portas e parâmetros operacionais.

### 2.5 Camada de Middlewares (`middlewares/`)
- **Regras:**
  - Tratamento centralizado de exceções (Global Error Handler), eliminando blocos `try/except` idênticos e callbacks com tratamento repetitivo.
  - Logging estruturado de requisições e respostas.

---

## 3. Diretrizes Específicas por Tecnologia

### 3.1 Python / Flask
- Utilizar **Blueprints** para cada domínio funcional (`produto_bp`, `usuario_bp`, `pedido_bp`, `task_bp`, `category_bp`, `report_bp`).
- Conexões de banco SQLite devem ser desacopladas do ciclo de vida global:
  - Usar `flask.g` para abrir conexão por requisição e fechá-la no teardown (`@app.teardown_appcontext`), ou utilizar o `Flask-SQLAlchemy` gerenciado.
- Adotar `datetime.now(timezone.utc)` para manipulação temporal compatível com Python 3.12+.
- Utilizar `db.session.get(Model, id)` para consultas por chave primária no SQLAlchemy 2.0.

### 3.2 Node.js / Express
- Decompor o `AppManager` monolítico em classes ou módulos funcionais de domínio:
  - `controllers/CheckoutController.js`, `controllers/ReportController.js`, `controllers/UserController.js`.
  - `models/Course.js`, `models/User.js`, `models/Enrollment.js`, `models/Payment.js`.
  - `routes/checkoutRoutes.js`, `routes/reportRoutes.js`, `routes/userRoutes.js`.
- Migrar callbacks aninhados (Callback Hell) para **Promises e Async/Await**, garantindo tratamento de erros assíncrono limpo via `next(err)`.
- Gerenciar conexão SQLite de forma segura, garantindo integridade referencial com foreign keys ativadas.

---

## 4. Regra de Ouro: Preservação Estrita de Contratos de API
A refatoração arquitetural para o padrão MVC **JAMAIS** pode quebrar consumidores da API:
1. Todas as rotas existentes devem permanecer ativas nos mesmos caminhos de URL.
2. Todos os verbos HTTP originais (`GET`, `POST`, `PUT`, `DELETE`) devem ser mantidos.
3. As propriedades dos payloads JSON de entrada e saída devem manter rigorosa paridade estrutural.
4. Os códigos de status HTTP (200, 201, 400, 401, 404, 500) devem ser preservados em cenários de sucesso e erro.
