# nopCommerce — Pipeline Evaluation Report

> **Auto-generated** by the Reverse Engineer Skill Evaluator · 2026-05-26T10:34:06.716679+00:00Z

---

## Overall Score

```
███████████████████░  95/100 pts
```

**Confidence:** ✅ HIGH

The pipeline produced high-quality, verifiable outputs across all sections. Results can be used with high confidence for planning.

---

## Section Scores

| Section | Score | Status |
|---------|-------|--------|
| 1. Parsing Quality | 20/20 | ✅ PASS |
| 2. API Endpoint Detection | 17/20 | ⚠️ WARN |
| 3. Dead Code Analysis | 15/15 | ✅ PASS |
| 4. Entity / Data Architecture | 13/15 | ⚠️ WARN |
| 5. Dependency Graph | 15/15 | ✅ PASS |
| 6. AI Analysis Quality | 15/15 | ✅ PASS |
| **TOTAL** | **95/100** | **✅ HIGH** |

---

## Section Details

### 1. Parsing Quality — 20/20 pts

**Status:** ✅ PASS

> 292 files | 231 classes | 1452 methods

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Files Parsed | ✅ PASS | +5/5 | 292 files parsed successfully |
| Parse Success Rate | ✅ PASS | +5/5 | 100% of attempted files parsed |
| Classes Extracted | ✅ PASS | +5/5 | 231 classes identified across parsed files |
| Methods Extracted | ✅ PASS | +5/5 | 1452 methods/functions identified |

### 2. API Endpoint Detection — 17/20 pts

**Status:** ⚠️ WARN

> 284 endpoints extracted from 292 files

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Endpoints Detected | ✅ PASS | +8/8 | 284 API endpoints extracted |
| HTTP Method Variety | ⚠️ WARN | +3/6 | Only 2 HTTP method type(s) found: GET, POST |
| Path Format Validity | ✅ PASS | +6/6 | 284/284 paths have valid route format |

### 3. Dead Code Analysis — 15/15 pts

**Status:** ✅ PASS

> 79 dead files | 229 dead classes

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Dead File Ratio | ✅ PASS | +5/5 | 79 dead files = 27% of total (plausible range) |
| Analysis Completed | ✅ PASS | +5/5 | Dead code analysis ran and returned a structured result |
| Class-Level Analysis | ✅ PASS | +5/5 | 229 potentially unreferenced classes found |

**Recommendations:**
- Always manually verify dead code results before deletion — static analysis cannot detect runtime-loaded modules, reflection-based usage, or files loaded via config

### 4. Entity / Data Architecture — 13/15 pts

**Status:** ⚠️ WARN

> 51 entities | 0 relationships | 7 bounded contexts

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Entities Detected | ✅ PASS | +7/7 | 51 data entities extracted |
| Microservice Boundaries | ✅ PASS | +5/5 | 7 bounded contexts identified |
| Relationships Detected | ⚠️ WARN | +1/3 | 0 relationships detected despite 51 entities. Repo may use Fluent API or private backing fields for navigation properties (not captured by regex analysis) |

**Recommendations:**
- 0 relationships detected — if the repo uses EF Core Fluent API or JPA XML mapping, relationships won't be found by regex. Consider enhancing _extract_db_entities_dotnet() to parse OnModelCreating() method bodies

### 5. Dependency Graph — 15/15 pts

**Status:** ✅ PASS

> 286 dep nodes | 1334 edges | 7 tech items

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Dependency Map Built | ✅ PASS | +5/5 | 286 modules with 1334 dependency edges |
| Graphviz Diagram | ✅ PASS | +5/5 | Graphviz diagram generated (80 edges shown) |
| Tech Stack Detection | ✅ PASS | +5/5 | 7 technologies identified: .NET Project File, .NET Solution, ASP.NET Core, Docker, Docker Compose |

### 6. AI Analysis Quality — 15/15 pts

**Status:** ✅ PASS

> AI-powered (Claude claude-sonnet-4-6) | 4 roadmap phases | target: ASP.NET Core 8, Entity Framework Core, Azure / AWS

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Executive Summary | ✅ PASS | +5/5 | AI-generated executive summary present and substantive |
| Architecture Pattern | ✅ PASS | +5/5 | Pattern identified: 'MVC Monolith' |
| Modernization Phases | ✅ PASS | +5/5 | 4 phases: Assessment & Audit, Foundation & Refactoring, Migration & Modernization... |


---

## Recommendations

- Always manually verify dead code results before deletion — static analysis cannot detect runtime-loaded modules, reflection-based usage, or files loaded via config
- 0 relationships detected — if the repo uses EF Core Fluent API or JPA XML mapping, relationships won't be found by regex. Consider enhancing _extract_db_entities_dotnet() to parse OnModelCreating() method bodies

---

## Interpretation Guide

### What the Scores Mean

| Confidence | Score | Meaning |
|------------|-------|---------|
| HIGH       | ≥ 80  | All key pipeline sections produced verifiable output |
| MEDIUM     | ≥ 60  | Most sections reliable; some manual spot-checks advised |
| LOW        | ≥ 40  | Partial results — likely pattern coverage gaps |
| VERY LOW   | < 40  | Major gaps; treat as rough estimates only |

### Check Statuses

| Status | Meaning |
|--------|---------|
| ✅ PASS | Check passed — result is reliable |
| ⚠️ WARN | Partial or borderline result — review advised |
| ❌ FAIL | Check failed — result in this area may be missing or wrong |

### What Is Reliable vs Heuristic

| Output Area | Reliability | Notes |
|-------------|-------------|-------|
| File count & language distribution | HIGH | Exact filesystem walk |
| Class / method extraction | MEDIUM-HIGH | Regex-based; edge cases exist |
| Import / dependency detection | MEDIUM | Pattern-matched; dynamic imports missed |
| API endpoint extraction | MEDIUM | Attribute/decorator patterns; dynamic routes missed |
| Dead code detection | LOW-MEDIUM | Heuristic only — validate before deleting |
| Entity / DB schema | MEDIUM | ORM annotation & namespace heuristics |
| Microservice boundaries | LOW-MEDIUM | Keyword clustering — AI fallback |
| AI executive summary | HIGH (with API key) | Claude claude-sonnet-4-6; fallback text if no key |
| AI modernization roadmap | HIGH (with API key) | Claude claude-sonnet-4-6; fallback text if no key |

---

## How to Spot-Check Results

### Parsing Quality
- Open the SDD JSON → `module_inventory` array; pick 5 random files
- Verify the `classes` and `methods` lists match the actual source file content

### API Endpoints
- Compare `api_catalog.endpoints` in the SDD JSON against the actual
  controller files in the repository
- Check that HTTP methods (`GET`, `POST`, etc.) are correct

### Dead Code
- Pick 3 files from `dead_code_analysis.unreferenced_files`
- Search the repository for any import or reference to that file
- If found → false positive (this is expected; always validate before deleting)

### Entity Detection
- Open the SDD JSON → `data_architecture.entities`
- Cross-reference entity names against actual ORM model files in the repository

### Dependency Graph
- The Mermaid diagram in the HTML dashboard shows module-to-module edges
- Verify a known dependency exists as an edge in the graph

---

_Generated by Reverse Engineer Skill · Claude Code_
