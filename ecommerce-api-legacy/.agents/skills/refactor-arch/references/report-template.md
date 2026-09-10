# Template Padronizado de Relatório de Auditoria Arquitetural

Este documento define o schema formal que a skill `refactor-arch` deve gerar na **Fase 2 (Architecture Audit)** e salvar obrigatoriamente no arquivo `reports/audit-project-<N>.md` (onde `<N>` é 1, 2 ou 3).

---

## Estrutura Formal do Relatório

O relatório de auditoria deve ser gerado no seguinte formato Markdown estrito:

```markdown
# Architecture Audit Report — <Nome do Projeto>

## Metadados do Projeto
- **Projeto:** <nome-da-pasta>
- **Stack:** <Linguagem> + <Framework>
- **Data da Auditoria:** <AAAA-MM-DD>
- **Escopo Analisado:** <N> arquivos analisados | ~<Total> linhas de código

---

## Sumário Executivo de Achados

| Severidade | Total Encontrado |
| :--- | :---: |
| **CRITICAL** | <N> |
| **HIGH** | <N> |
| **MEDIUM** | <N> |
| **LOW** | <N> |
| **TOTAL** | **<Soma>** |

---

## Detalhamento dos Findings

### [<SEVERIDADE>] <Nome do Anti-pattern / Problema> (ID: <PREFIXO>-<NUM>)
- **Arquivo e Linhas:** `<caminho/do/arquivo>:<linha_inicio>-<linha_fim>`
- **Descrição do Problema:**
  <Explicação detalhada do que o código está fazendo de incorreto ou vulnerável.>
- **Impacto Arquitetural / Segurança:**
  <Consequências diretas para a estabilidade, segurança, escalabilidade ou manutenibilidade da aplicação.>
- **Recomendação de Refatoração:**
  <Orientação clara de qual transformação do playbook deve ser aplicada na Fase 3.>

---

*(Repetir a seção '### [<SEVERIDADE>]' para cada finding identificado)*

---

## Recomendações Prioritárias para a Fase 3 (Refatoração)
1. <Ação prioritária de maior impacto (ex: eliminação de SQL Injection e isolamento de segredos)>
2. <Decomposição de God Classes / Monólitos para a camada MVC>
3. <Otimização de queries N+1 e padronização de tratamento de erros>
4. <Substituição de APIs obsoletas / deprecated>

---

## Status do Gate de Aprovação (HITL)
- **Fase 2 concluída com sucesso.**
- **Relatório exportado para:** `reports/audit-project-<N>.md`
- **Aguardando aprovação do usuário para prosseguir para a Fase 3 (Refatoração).**
```

---

## Regras de Preenchimento Mandatórias:
1. O arquivo deve sempre conter os caminhos e números de linha **exatos** no formato `<arquivo>:<linha>` ou `<arquivo>:<inicio>-<fim>`.
2. Os findings devem ser ordenados estritamente por severidade decrescente: `CRITICAL` → `HIGH` → `MEDIUM` → `LOW`.
3. O relatório deve contabilizar no mínimo 5 findings, incluindo obrigatoriamente pelo menos 1 de severidade `CRITICAL` ou `HIGH`.
4. Caso tenham sido detectadas APIs deprecated, estas devem estar registradas com o devido equivalente moderno indicado.
