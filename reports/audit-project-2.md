# Architecture Audit Report — ecommerce-api-legacy

## Metadados do Projeto

- **Projeto:** `ecommerce-api-legacy`
- **Stack:** Node.js v24.18 + Express 4.18.2 + SQLite3
- **Data da Auditoria:** 2026-09-10
- **Escopo Analisado:** 3 arquivos analisados (`src/app.js`, `src/AppManager.js`, `src/utils.js`) | ~183 linhas de código

---

## Sumário Executivo de Achados

| Severidade | Total Encontrado |
| :--- | :---: |
| **CRITICAL** | 2 |
| **HIGH** | 3 |
| **MEDIUM** | 1 |
| **LOW** | 1 |
| **TOTAL** | **7** |

---

## Detalhamento dos Findings

### [CRITICAL] AP-03: Hardcoded Secret Credentials in Source Code (ID: EC-01)

- **Arquivo e Linhas:** `src/utils.js:1-7`
- **Descrição do Problema:**
  Chaves produtivas de gateway de pagamento (`pk_live_1234567890abcdef`), senhas de banco (`senha_super_secreta_prod_123`) e credenciais SMTP (`no-reply@fullcycle.com.br`) estão expostas diretamente no objeto `config`.
- **Impacto Arquitetural / Segurança:**
  Vazamento irreversível de segredos em repositórios e comprometimento de gateways de pagamento reais.
- **Recomendação de Refatoração:**
  Isolar configurações no módulo `config/index.js` consumindo `process.env` com fallbacks para desenvolvimento (Receita T-01).

---

### [CRITICAL] AP-04: Broken / Insecure Cryptographic Hash (ID: EC-02)

- **Arquivo e Linhas:** `src/utils.js:17-23` e `src/AppManager.js:68`
- **Descrição do Problema:**
  A função `badCrypto(pwd)` gera uma pseudo-hash através de um loop de 10.000 iterações convertendo a senha para base64 e truncando os caracteres (`hash.substring(0, 10)`). Além de extremamente vulnerável a colisões, não utiliza algoritmo com salt padronizado.
- **Impacto Arquitetural / Segurança:**
  Senhas de alunos e clientes armazenadas com hash trivialmente quebrável e vulnerável a colisões imediatas.
- **Recomendação de Refatoração:**
  Substituir por função criptográfica segura com `crypto.scrypt` ou `crypto.pbkdf2` nativo do Node.js (Receita T-05).

---

### [HIGH] AP-05: God Class / Frankenstein Monolith (ID: EC-03)

- **Arquivo e Linhas:** `src/AppManager.js:4-139`
- **Descrição do Problema:**
  A classe `AppManager` atua como um monólito concentrando: instanciação de banco SQLite em memória, criação de schema DDL (`initDb`), seeds iniciais de cursos e matrículas, configuração de rotas Express (`setupRoutes`), orquestração do checkout, emissão de relatórios e deleção de usuários.
- **Impacto Arquitetural / Segurança:**
  Total violação do Single Responsibility Principle (SRP) e acoplamento rígido que inviabiliza testes e extensibilidade.
- **Recomendação de Refatoração:**
  Decompor a classe em camadas MVC: `models/` (Course, User, Enrollment, Payment), `controllers/` (CheckoutController, ReportController, UserController) e `routes/` modulares (Receita T-03).

---

### [HIGH] AP-06: Sensitive Data Exposure in Logs (ID: EC-04)

- **Arquivo e Linhas:** `src/AppManager.js:45`
- **Descrição do Problema:**
  O número completo do cartão de crédito do cliente é impresso no console em texto claro (`console.log("Processando cartão " + cc + ...)`).
- **Impacto Arquitetural / Segurança:**
  Violação estrita das normas do PCI-DSS (Payment Card Industry Data Security Standard) e vazamento de dados financeiros sensíveis nos logs da aplicação.
- **Recomendação de Refatoração:**
  Mascarar dados de pagamento exibindo apenas os últimos 4 dígitos (`**** **** **** 4444`) e sanitizar saídas de log.

---

### [HIGH] AP-07: Mutable Global State & Concurrency Issues (ID: EC-05)

- **Arquivo e Linhas:** `src/utils.js:9-10, 12-15`
- **Descrição do Problema:**
  As variáveis `globalCache` e `totalRevenue` são mantidas em escopo global de módulo e sofrem mutações não controladas (`globalCache[key] = data`).
- **Impacto Arquitetural / Segurança:**
  Risco de vazamento de memória e inconsistência de dados entre requisições concorrentes.
- **Recomendação de Refatoração:**
  Eliminar o estado global mutável em favor de persistência adequada em banco de dados ou serviço de cache com TTL.

---

### [MEDIUM] AP-08: N+1 Queries & Nested Callback Hell (ID: EC-06)

- **Arquivo e Linhas:** `src/AppManager.js:80-128`
- **Descrição do Problema:**
  O endpoint `/api/admin/financial-report` implementa 4 níveis de callbacks aninhados com contadores manuais assíncronos (`coursesPending`, `enrPending`), executando consultas iterativas de usuários e pagamentos para cada matrícula.
- **Impacto Arquitetural / Segurança:**
  Gargalo de performance no banco (N+1 queries), alta complexidade cognitiva e alto risco de falha silenciosa se um callback não responder.
- **Recomendação de Refatoração:**
  Reescrever a lógica utilizando queries consolidadas com `JOIN` e adotar `async/await` com Promises nativas (Receita T-04 e T-07).

---

### [LOW] AP-10: Cryptic Naming & Magic Values (ID: EC-07)

- **Arquivo e Linhas:** `src/AppManager.js:29-33, 46`
- **Descrição do Problema:**
  Parâmetros da requisição nomeados cripticamente como `u`, `e`, `p`, `cid`, `cc` e checagem de bandeira de pagamento baseada no magic string `"4"` (`cc.startsWith("4")`).
- **Impacto Arquitetural / Segurança:**
  Legibilidade severamente prejudicada e manutenção propensa a erros.
- **Recomendação de Refatoração:**
  Documentar parâmetros e isolar validação de cartão em serviço de pagamento.

---

## Recomendações Prioritárias para a Fase 3 (Refatoração)

1. Decompor `AppManager.js` em estrutura limpa MVC (`src/models/`, `src/controllers/`, `src/routes/`, `src/config/`).
2. Migrar de Callback Hell para `async/await` com Promises para SQLite.
3. Isolar credenciais em `src/config/index.js` via `process.env`.
4. Mascarar cartões de crédito nos logs (conformidade PCI-DSS) e modernizar hashing de senhas com `crypto`.
5. Preservar 100% dos contratos das rotas `/api/checkout`, `/api/admin/financial-report` e `/api/users/:id`.

---

## Status do Gate de Aprovação (HITL)

- **Fase 2 concluída com sucesso.**
- **Relatório exportado para:** `reports/audit-project-2.md`
- **Aguardando aprovação do usuário para prosseguir para a Fase 3 (Refatoração).**
