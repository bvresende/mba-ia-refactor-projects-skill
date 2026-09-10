# Heurísticas de Análise e Descoberta de Projetos

Este documento fornece as diretrizes e regras heurísticas que a skill `refactor-arch` deve utilizar durante a **Fase 1 (Project Analysis)** para inspecionar, de forma agnóstica, qualquer base de código backend.

---

## 1. Detecção de Linguagem e Ecossistema

O agente deve inspecionar os arquivos de manifesto e extensões presentes na raiz e nos subdiretórios do projeto:

| Indicador no Repositório | Linguagem Detectada | Ecossistema / Runtime |
| :--- | :--- | :--- |
| `package.json`, `package-lock.json`, `yarn.lock`, `*.js`, `*.mjs` | **JavaScript / Node.js** | Node.js (CommonJS ou ES Modules) |
| `tsconfig.json`, `*.ts` | **TypeScript / Node.js** | Node.js / Deno / Bun |
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `*.py` | **Python** | CPython / PyPy (PEP 518/621) |
| `pom.xml`, `build.gradle`, `*.java` | **Java** | JVM |
| `go.mod`, `go.sum`, `*.go` | **Go** | Go runtime |

### Algoritmo de Priorização

1. Buscar arquivos de gerenciamento de dependências na raiz (`package.json`, `requirements.txt`, etc.).
2. Contabilizar a contagem de arquivos e extensões de código-fonte (`.py` vs `.js`).
3. Declarar a linguagem primária dominante.

---

## 2. Detecção de Frameworks Web

A identificação do framework é realizada por meio da análise das dependências declaradas e das chamadas de importação / inicialização:

### Python

- **Flask**:
  - Dependências: `flask`, `flask-cors`, `flask-sqlalchemy`
  - Código-fonte: `from flask import Flask`, `app = Flask(__name__)`, `Blueprint(...)`
- **FastAPI**:
  - Dependências: `fastapi`, `uvicorn`
  - Código-fonte: `from fastapi import FastAPI`, `app = FastAPI()`
- **Django**:
  - Dependências: `django`
  - Arquivos: `manage.py`, `wsgi.py`, `settings.py`

### Node.js / JavaScript

- **Express**:
  - Dependências: `express` no `package.json`
  - Código-fonte: `require('express')`, `const app = express()`
- **Fastify**:
  - Dependências: `fastify`
  - Código-fonte: `require('fastify')`
- **NestJS**:
  - Dependências: `@nestjs/core`, `@nestjs/common`

---

## 3. Detecção de Camada de Persistência e Banco de Dados

Identificar o driver de banco de dados ou ORM/ODM utilizado:

| Padrão no Código | Tecnologia de Banco | Modo de Acesso |
| :--- | :--- | :--- |
| `import sqlite3`, `sqlite3.connect(...)` | **SQLite** | Driver nativo / Raw SQL |
| `const sqlite3 = require('sqlite3')` | **SQLite** | Driver Node.js / Callback API |
| `from flask_sqlalchemy import SQLAlchemy`, `db.Model` | **SQLAlchemy** | ORM relacional |
| `const mongoose = require('mongoose')` | **MongoDB** | ODM |
| `const { Pool } = require('pg')`, `import psycopg2` | **PostgreSQL** | Driver relacional |
| `mysql2`, `pymysql` | **MySQL** | Driver relacional |

---

## 4. Mapeamento de Rotas e Endpoints

A skill deve mapear exaustivamente todas as rotas expostas pela aplicação para garantir paridade 100% dos contratos pós-refatoração:

### Em Flask

- Decorators diretos: `@app.route('/caminho', methods=['GET', 'POST', ...])`
- Registro manual de URL: `app.add_url_rule('/caminho', endpoint='...', view_func=..., methods=[...])`
- Blueprints: `@blueprint.route('/caminho', ...)` e `app.register_blueprint(blueprint)`

### Em Express

- Métodos diretos: `app.get('/path', handler)`, `app.post('/path', handler)`, `app.delete('/path', handler)`
- Routers modulares: `router.get(...)` montados via `app.use('/prefix', router)`

---

## 5. Mapeamento da Arquitetura Atual

A skill deve classificar a maturidade arquitetural inicial do projeto:

- **Monolítico Não Estruturado (God File / Monolith):** Toda a aplicação se concentra em 1 a 4 arquivos na raiz sem separação clara de responsabilidades (ex: rotas misturadas com SQL e regras de negócio no mesmo arquivo ou classe).
- **Parcialmente Estruturado (Fragmented / Layer-Leaking):** Existem diretórios como `models/`, `routes/`, `services/`, porém camadas vazam responsabilidades (ex: controllers inexistentes, rotas executando queries SQL diretamente, modelos executando validações de apresentação ou sem injeção de dependências).
- **MVC Bem Definido:** Camadas estritamente desacopladas em Models (dados/regras de entidade), Views/Routes (protocolo HTTP) e Controllers (orquestração de fluxo).

---

## 6. Output Esperado da Fase 1

Ao concluir a Fase 1, o agente deve gerar um bloco de resumo padronizado:

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <Python | JavaScript/Node.js | ...>
Framework:     <Flask X.Y | Express X.Y | ...>
Dependencies:  <Principais pacotes identificados>
Domain:        <Domínio inferido da aplicação: E-commerce, LMS, Task Manager, etc.>
Architecture:  <Classificação da arquitetura atual>
Source files:  <N> files analyzed (~<Total> lines of code)
Endpoints:     <Lista e total de rotas detectadas>
DB / Storage:  <SQLite | SQLAlchemy ORM | In-memory | ...>
================================
```
