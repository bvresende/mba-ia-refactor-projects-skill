# Playbook de Refatoração Arquitetural (Receitas de Transformação)

Este playbook contém o catálogo de transformações concretas com exemplos de código **Antes / Depois** que a skill `refactor-arch` deve aplicar durante a **Fase 3 (Refactoring)** para eliminar dívidas técnicas e migrar projetos para o padrão MVC.

---

## 1. Receita T-01: Extração de Configurações Hardcoded para Módulo Dedicado

### Problema:
Credenciais e segredos embutidos diretamente no código-fonte, gerando vulnerabilidade de segurança e acoplamento de ambiente.

### Exemplo de Transformação:

**Antes (Python):**
```python
# app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
db_path = "loja.db"
```

**Depois (Python):**
```python
# config/settings.py
import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
    DB_PATH = os.getenv("DATABASE_PATH", "loja.db")

settings = Settings()
```

---

## 2. Receita T-02: Eliminação de SQL Injection via Queries Parametrizadas

### Problema:
Concatenação direta de strings de entrada do usuário em queries SQL, permitindo manipulação maliciosa.

### Exemplo de Transformação:

**Antes (Python/SQLite):**
```python
# models.py
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("INSERT INTO usuarios (nome, email) VALUES ('" + nome + "', '" + email + "')")
```

**Depois (Python/SQLite):**
```python
# models/produto_model.py
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)", (nome, email))
```

---

## 3. Receita T-03: Decomposição de God Class / God File para Camadas MVC

### Problema:
Arquivo único contendo inicialização de banco, DDL, registro de rotas, lógica transacional e respostas HTTP.

### Exemplo de Transformação:

**Antes (Node.js/Express):**
```javascript
// AppManager.js
class AppManager {
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => {
            this.db.get("SELECT * FROM courses WHERE id = ?", [req.body.c_id], (err, course) => {
                // Lógica de usuário, pagamento, matrícula e resposta tudo aqui dentro...
            });
        });
    }
}
```

**Depois (Node.js/Express MVC):**
```javascript
// routes/checkoutRoutes.js
const express = require('express');
const router = express.Router();
const CheckoutController = require('../controllers/CheckoutController');

router.post('/checkout', CheckoutController.processCheckout);
module.exports = router;

// controllers/CheckoutController.js
const Course = require('../models/Course');
const EnrollmentService = require('../services/EnrollmentService');

class CheckoutController {
    static async processCheckout(req, res, next) {
        try {
            const result = await EnrollmentService.execute(req.body);
            return res.status(200).json(result);
        } catch (error) {
            return next(error);
        }
    }
}
```

---

## 4. Receita T-04: Eliminação de Callback Hell com Async/Await e Promises

### Problema:
Aninhamento profundo de callbacks (Pyramid of Doom), dificultando leitura, manutenção e controle de erros.

### Exemplo de Transformação:

**Antes (Node.js):**
```javascript
this.db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
    if (err) return res.status(500).send("Erro");
    this.db.get("SELECT id FROM users WHERE email = ?", [e], (err, user) => {
        if (err) return res.status(500).send("Erro");
        this.db.run("INSERT INTO enrollments ...", (err) => {
            // Mais 2 níveis de aninhamento
        });
    });
});
```

**Depois (Node.js):**
```javascript
// database/dbHelper.js
const getAsync = (db, sql, params) => new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => err ? reject(err) : resolve(row));
});

// Em função async:
const course = await getAsync(db, "SELECT * FROM courses WHERE id = ? AND active = 1", [cid]);
if (!course) return res.status(404).send("Curso não encontrado");

const user = await getAsync(db, "SELECT id FROM users WHERE email = ?", [e]);
```

---

## 5. Receita T-05: Criptografia Segura de Senhas e Sanitização de Respostas

### Problema:
Uso de MD5, funções caseiras de hash ou vazamento de hashes de senhas no JSON de resposta.

### Exemplo de Transformação:

**Antes (Python):**
```python
# models/user.py
import hashlib
class User(db.Model):
    def set_password(self, pwd):
        self.password = hashlib.md5(pwd.encode()).hexdigest()

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'password': self.password}
```

**Depois (Python):**
```python
# models/user_model.py
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        # Compatibilidade com legados em migração gradual:
        if self.password.startswith(('pbkdf2:', 'scrypt:')):
            return check_password_hash(self.password, pwd)
        import hashlib
        return self.password == hashlib.md5(pwd.encode()).hexdigest()

    def to_dict(self, include_sensitive=False):
        data = {'id': self.id, 'name': self.name, 'email': self.email, 'role': self.role}
        if include_sensitive:
            data['password'] = self.password
        return data
```

---

## 6. Receita T-06: Remoção de Backdoors e Endpoints Inseguros

### Problema:
Endpoints que executam SQL arbitrário (`/admin/query`) ou limpam o banco sem autenticação (`/admin/reset-db`).

### Exemplo de Transformação:

**Antes:**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = request.get_json().get("sql", "")
    cursor.execute(query) # Vulnerabilidade crítica!
```

**Depois:**
```python
# O endpoint inseguro é completamente REMOVIDO da API pública.
# Operações de banco passam a ser executadas via scripts de migração ou consoles CLI protegidos.
```

---

## 7. Receita T-07: Resolução de N+1 Queries através de JOINs ou Eager Loading

### Problema:
Execução de query SQL dentro de loops iterativos sobre listas de registros pais.

### Exemplo de Transformação:

**Antes (Python SQLAlchemy):**
```python
tasks = Task.query.all()
for t in tasks:
    if t.user_id:
        user = User.query.get(t.user_id) # N+1 query para cada task!
```

**Depois (Python SQLAlchemy):**
```python
# Uso de joinedload para carregar relacionamento em consulta única:
from sqlalchemy.orm import joinedload
tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
for t in tasks:
    user_name = t.user.name if t.user else None
```

---

## 8. Receita T-08: Substituição de APIs Deprecated / Obsoletas

### Problema:
Uso de métodos depreciados que geram warnings e quebram compatibilidade em versões recentes das stacks.

### Exemplos de Transformação:

**1. `datetime.utcnow()` (Python 3.12+):**
```python
# Antes:
from datetime import datetime
created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Depois:
from datetime import datetime, timezone
created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```

**2. `Model.query.get(id)` (SQLAlchemy 2.0):**
```python
# Antes:
task = Task.query.get(task_id)

# Depois:
task = db.session.get(Task, task_id)
```

---

## 9. Receita T-09: Tratamento Centralizado de Erros (Global Error Handler)

### Problema:
Blocos `try/except` repetidos em todos os controladores com mensagens manuais e tratamentos inconsistentes.

### Exemplo de Transformação:

**Antes (Flask):**
```python
def listar_produtos():
    try:
        # codigo
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
```

**Depois (Flask):**
```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"erro": str(e), "sucesso": False}), 500
```
