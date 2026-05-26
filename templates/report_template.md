# {{REPO_NAME}} — System Reverse Engineering Report

> **Auto-generated** by the Reverse Engineer Skill (Claude Code) · v3.0
> Generated: {{GENERATED_AT}}
> Repository: [{{REPO_URL}}]({{REPO_URL}})
> Primary Language: **{{PRIMARY_LANGUAGE}}**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Logic & Functional Overview](#2-business-logic--functional-overview)
3. [Codebase Metrics](#3-codebase-metrics)
4. [Architecture Overview](#4-architecture-overview)
5. [Module Inventory](#5-module-inventory)
6. [API Catalog](#6-api-catalog)
7. [Dependency Analysis](#7-dependency-analysis)
8. [Dead Code Analysis](#8-dead-code-analysis)
9. [Tech Debt Inventory](#9-tech-debt-inventory)
10. [Modernization Roadmap](#10-modernization-roadmap)
11. [Data Architecture & Microservices Decomposition](#11-data-architecture--microservices-decomposition)
12. [Risk Assessment](#12-risk-assessment)
13. [Appendix](#13-appendix)

---

## 1. Executive Summary

{{SYSTEM_PURPOSE}}

| Attribute | Value |
|-----------|-------|
| **Architecture Pattern** | {{ARCHITECTURE_PATTERN}} |
| **Modernization Priority** | {{MODERNIZATION_PRIORITY}} |
| **Platform** | {{PLATFORM}} |
| **Detected Tech Stack** | {{TECH_STACK_INLINE}} |
| **Total Files** | {{TOTAL_FILES}} |
| **Total Classes** | {{TOTAL_CLASSES}} |
| **Total Methods / Functions** | {{TOTAL_METHODS}} |

**Priority Reasoning:**
{{PRIORITY_REASONING}}

---

## 2. Business Logic & Functional Overview

> How this system works for its users — extracted from API endpoints, class names, ORM entity model, and AI analysis.

**Business Domain:** {{BUSINESS_DOMAIN}}

### What the System Does

{{WHAT_IT_DOES}}

### Core Business Workflows

{{CORE_WORKFLOWS}}

### User Roles & Actors

{{USER_ROLES}}

### Key Business Rules

{{KEY_BUSINESS_RULES}}

### Domain Entities in Business Terms

| Entity | Business Meaning | Key Operations |
|--------|-----------------|----------------|
{{ENTITY_GLOSSARY_ROWS}}

### Detected Integrations

{{INTEGRATIONS}}

---

## 3. Codebase Metrics

### Language Distribution

| Language | Files | Share |
|----------|-------|-------|
{{LANGUAGE_TABLE_ROWS}}

### Key Counts

| Metric | Value |
|--------|-------|
| Files Analyzed | **{{TOTAL_FILES}}** |
| Classes Defined | **{{TOTAL_CLASSES}}** |
| Methods & Functions | **{{TOTAL_METHODS}}** |
| API Endpoints Extracted | **{{TOTAL_ENDPOINTS}}** |
| Unreferenced Files (Dead Code) | **{{DEAD_FILES_COUNT}}** |
| Unreferenced Classes | **{{DEAD_CLASSES_COUNT}}** |
| Unique External Dependencies | **{{TOTAL_DEPS}}** |

---

## 3. Architecture Overview

**Pattern Identified:** {{ARCHITECTURE_PATTERN}}

### Architectural Layers

{{ARCH_LAYERS_LIST}}

### Global Dependency Graph

```mermaid
{{MERMAID_DIAGRAM}}
```

> **How to read this graph:** Nodes are source file modules. Edges represent import/using statements.
> Standard library namespaces are excluded. Run in any Mermaid-compatible renderer (GitHub, GitLab, Notion, Confluence, VS Code, etc.).

---

## 4. Module Inventory

_Showing first 40 of {{TOTAL_FILES}} files. Full inventory available in `{{REPO_NAME}}_sdd.json`._

{{MODULE_INVENTORY_SECTION}}

---

## 5. API Catalog

**Total Endpoints Extracted:** {{TOTAL_ENDPOINTS}}

{{API_CATALOG_TABLE}}

### OpenAPI 3.0 Specification

```json
{{OPENAPI_JSON}}
```

> Auto-extracted from routing annotations (ASP.NET `[HttpGet]`/`[Route]`, Spring `@GetMapping`, Flask `@route`, FastAPI `@app.get`, Express `app.get()`).
> Validate and extend this spec manually for production use.

---

## 6. Dependency Analysis

### Top 10 Most Connected Modules

| Module | Outgoing References |
|--------|-------------------|
{{TOP_MODULES_TABLE_ROWS}}

### External Dependency Sample

```
{{EXTERNAL_DEPS_SAMPLE}}
```

> Full dependency map available in `{{REPO_NAME}}_sdd.json` under `dependency_analysis.external_dependencies`.

---

## 7. Dead Code Analysis

> **Important:** Dead code detection is heuristic-based. Results require manual verification before any deletion.
> Files that appear unreferenced may be loaded dynamically, by configuration, or via reflection.

### Potentially Unreferenced Files ({{DEAD_FILES_COUNT}})

{{DEAD_FILES_LIST}}

### Potentially Unreferenced Classes ({{DEAD_CLASSES_COUNT}})

{{DEAD_CLASSES_LIST}}

---

## 8. Tech Debt Inventory

### Identified Concerns

{{TECH_DEBT_CONCERNS_LIST}}

### Tech Debt Classification

| Area | Severity | Details | Action |
|------|----------|---------|--------|
| Legacy Dependencies | HIGH | {{TOTAL_DEPS}} external deps detected | Audit against CVE databases; upgrade stale packages |
| Documentation | MEDIUM | Auto-generated; accuracy not verified | Manual review and annotation required |
| Test Coverage | UNKNOWN | Test suite metrics not assessed | Run coverage tools; establish baseline |
| Dead Code | {{DEAD_CODE_SEVERITY}} | {{DEAD_FILES_COUNT}} unreferenced files | Review and prune; reduce maintenance surface |
| API Contracts | {{API_COVERAGE_SEVERITY}} | {{TOTAL_ENDPOINTS}} endpoints documented | Validate against OpenAPI spec; add missing routes |

---

## 9. Modernization Roadmap

### Recommended Target Stack

{{TARGET_STACK_LIST}}

### Migration Phases

{{PHASES_SECTION}}

### Proposed Microservice Decomposition

{{MICROSERVICES_LIST}}

**Estimated Total Effort:** {{ESTIMATED_EFFORT}}

### Risk Factors

{{RISK_FACTORS_LIST}}

---

## 10. Data Architecture & Microservices Decomposition

> Entity definitions extracted by static analysis. Results depend on which files were included
> in the 300-file analysis cap. For large repos, run against a focused subset for best results.

### Schema Summary

| Metric | Value |
|--------|-------|
| Entities Detected | **{{ENTITY_COUNT}}** |
| Relationships Detected | **{{RELATIONSHIP_COUNT}}** |
| Bounded Contexts Identified | **{{BOUNDARY_COUNT}}** |

### Detected Entities

| Entity | Table | Fields | Relationships |
|--------|-------|--------|---------------|
{{ENTITY_TABLE_ROWS}}

### Proposed Microservice Data Boundaries

Each bounded context below represents a candidate microservice that should own
its own dedicated database (**Database-Per-Service** pattern).

{{DATA_BOUNDARY_SECTIONS}}

### Migration Guidance

When decomposing the monolithic database for microservices migration:

1. **Start with the loosest coupling** — identify entities with few cross-domain foreign keys.
2. **Introduce the Strangler Fig pattern** — new microservices own their tables, the monolith references them via API calls.
3. **Use the Outbox Pattern** for cross-service consistency — write events to an outbox table atomically, then publish via a message broker (e.g. RabbitMQ, Kafka).
4. **Avoid distributed transactions** — favour eventual consistency and compensating transactions.
5. **Data synchronisation phase** — run dual-write during transition; cut over once stable.

---

## 11. Risk Assessment

| Risk ID | Category | Severity | Description | Recommendation |
|---------|----------|----------|-------------|----------------|
| RISK-001 | Technical Debt | {{TECH_DEBT_SEVERITY}} | {{TOTAL_FILES}} files with accumulated technical debt | Systematic refactoring backlog and code review process |
| RISK-002 | Dead Code | {{DEAD_CODE_SEVERITY}} | {{DEAD_FILES_COUNT}} unreferenced modules detected | Review and remove unused code; reduce blast radius |
| RISK-003 | API Documentation | {{API_COVERAGE_SEVERITY}} | {{TOTAL_ENDPOINTS}} API endpoints extracted | Full OpenAPI 3.0 spec required before modernization |
| RISK-004 | Dependency Hygiene | MEDIUM | {{TOTAL_DEPS}} external dependencies detected | CVE audit and dependency pinning recommended |
| RISK-005 | Migration Complexity | HIGH | Legacy codebase with {{TOTAL_CLASSES}} classes | Phased migration with strangler-fig pattern recommended |

---

## 12. Appendix

### How This Report Was Generated

This report was produced by the **Reverse Engineer Skill** v3.0 for Claude Code, which performs:

1. **Repository Cloning** — `git clone --depth=1 {{REPO_URL}}`
2. **File Discovery** — Walks all source directories, filtering `.py`, `.java`, `.cs`, `.ts`, `.js`, etc.
3. **Layer-Balanced File Selection** — Prioritises controllers, services, repositories, domain entities within 300-file cap
4. **Static Code Parsing** — Regex-based extraction for classes, methods, imports, API routes, and ORM entities
5. **Dependency Mapping** — Builds directed graph from import/using statements
6. **Dead Code Detection** — Heuristic analysis of module reference counts
7. **API Extraction** — Identifies routing annotations (ASP.NET, Spring MVC, Flask, FastAPI, Express)
8. **OpenAPI Generation** — Assembles OpenAPI 3.0 spec from extracted routes
9. **Entity / DB Schema Detection** — Extracts ORM entities (EF Core, JPA/Hibernate, SQLAlchemy, Django)
10. **Microservice Boundary Clustering** — Semantic domain clustering into bounded contexts
11. **AI Analysis** — Claude claude-sonnet-4-6 generates executive summary and modernization roadmap
12. **Quality Evaluation** — Automated 100-point scoring across 6 sections → `{{REPO_NAME}}_evaluation.md`
13. **Output Generation** — Produces this `.md` + `_sdd.json` + `_dashboard.html` + `_evaluation.md`

### Five Output Files

| File | Purpose | Audience |
|------|---------|----------|
| `{{REPO_NAME}}_sdd.json` | Complete System Design Document (machine-readable, 13 sections) | Developers, Architects, AI tooling |
| `{{REPO_NAME}}_dashboard.html` | Interactive stakeholder dashboard (self-contained, 6 sections) | Product Owners, Management, Clients |
| `{{REPO_NAME}}_report.md` | This file — full technical narrative (11 sections + appendix) | Engineers, Architects, Code Reviewers |
| `{{REPO_NAME}}_evaluation.md` | Automated 100-point quality score with PASS/WARN/FAIL checks | QA, Pipeline CI, Developers |
| `manifest.json` | Machine-readable run record with file sizes and metrics | Automation, CI pipelines |

### Using These Files

**The Markdown report** (`_report.md`):
- Paste directly into GitHub Wiki, Confluence, Notion, or Azure DevOps Wiki
- Mermaid diagrams render natively on GitHub, GitLab, and Notion
- Use as the base for a formal SDD or architecture review document

**The HTML Dashboard** (`_dashboard.html`):
- Open directly in any web browser — no server required
- Share with stakeholders by attaching to email or hosting on any static host
- All data is embedded; no external dependencies at runtime (except CDN for Chart.js, Mermaid, vis.js)

**The SDD JSON** (`_sdd.json`):
- Feed to other AI tools for further analysis
- Import into architecture tools that accept JSON schema
- Use as input to migration planning or project management tooling

**The Evaluation Report** (`_evaluation.md`):
- Review immediately after each run to assess output quality
- Use PASS/WARN/FAIL checks to identify gaps requiring manual follow-up
- Track score improvements as parsers are extended or file caps adjusted

### Limitations & Caveats

- **Static analysis only** — runtime behaviour, dynamic dispatch, and reflection-based patterns are not captured
- **API extraction** relies on common annotation patterns; custom routing frameworks may be missed
- **Dead code** detection is heuristic — verify all findings before deletion
- **AI sections** require `ANTHROPIC_API_KEY` environment variable; deterministic fallbacks used otherwise
- **File cap** — analysis prioritises up to 300 files (layer-balanced: controllers → services → repos → domain → models → rest); very large repos have partial coverage
- **ORM relationships** via Fluent API (EF Core) or XML mapping (JPA) are not captured by regex analysis
- **Test files excluded** — `tests/`, `test/`, `__pycache__/`, `node_modules/` directories are skipped

### Extending the Analysis

To get deeper analysis:

```bash
# Set your Anthropic API key for AI-powered sections
export ANTHROPIC_API_KEY=sk-ant-...

# Re-run on the same or different repo
python reverse_engineer_skill.py https://github.com/owner/repo

# Five output files are written to ./outputs/{repo_name}/
```

---

_Generated by Reverse Engineer Skill v3.0 · Claude Code · Powered by Claude claude-sonnet-4-6 · {{GENERATED_AT}}_
