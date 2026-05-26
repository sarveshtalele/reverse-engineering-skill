# productlaunch — Pipeline Evaluation Report

> **Auto-generated** by the Reverse Engineer Skill Evaluator · 2026-05-26T08:48:59.897098+00:00Z

---

## Overall Score

```
███████████████░░░░░  75/100 pts
```

**Confidence:** ⚠️ MEDIUM

Most outputs are reliable. One or more sections have low signal (small repo, no API framework detected, etc.). Cross-check highlighted sections manually.

---

## Section Scores

| Section | Score | Status |
|---------|-------|--------|
| 1. Parsing Quality | 20/20 | ✅ PASS |
| 2. API Endpoint Detection | 8/20 | ⚠️ WARN |
| 3. Dead Code Analysis | 10/15 | ❌ FAIL |
| 4. Entity / Data Architecture | 10/15 | ⚠️ WARN |
| 5. Dependency Graph | 15/15 | ✅ PASS |
| 6. AI Analysis Quality | 12/15 | ⚠️ WARN |
| **TOTAL** | **75/100** | **⚠️ MEDIUM** |

---

## Section Details

### 1. Parsing Quality — 20/20 pts

**Status:** ✅ PASS

> 73 files | 59 classes | 461 methods

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Files Parsed | ✅ PASS | +5/5 | 73 files parsed successfully |
| Parse Success Rate | ✅ PASS | +5/5 | 100% of attempted files parsed |
| Classes Extracted | ✅ PASS | +5/5 | 59 classes identified across parsed files |
| Methods Extracted | ✅ PASS | +5/5 | 461 methods/functions identified |

### 2. API Endpoint Detection — 8/20 pts

**Status:** ⚠️ WARN

> 0 endpoints extracted from 73 files

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Endpoints Detected | ⚠️ WARN | +2/8 | 0 endpoints detected. If this is an API server, routes may use patterns not covered by static analysis (e.g. reflection, attribute-less routing) |
| HTTP Method Variety | ⚠️ WARN | +3/6 | Cannot assess — no endpoints detected |
| Path Format Validity | ⚠️ WARN | +3/6 | Cannot assess — no endpoints detected |

**Recommendations:**
- No endpoints detected. If this is an API server, check if it uses minimal API patterns (e.g. app.MapGet), XML config routing, or convention-based routing not captured by attribute scanning

### 3. Dead Code Analysis — 10/15 pts

**Status:** ❌ FAIL

> 66 dead files | 30 dead classes

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Dead File Ratio | ❌ FAIL | +0/5 | 90% of files flagged as dead — heuristic likely unreliable for this repo structure |
| Analysis Completed | ✅ PASS | +5/5 | Dead code analysis ran and returned a structured result |
| Class-Level Analysis | ✅ PASS | +5/5 | 30 potentially unreferenced classes found |

**Recommendations:**
- Dead file ratio is high — the heuristic flags files that are never imported by other analyzed files. For script/tool repos this is expected. Always validate before deleting flagged files.
- Always manually verify dead code results before deletion — static analysis cannot detect runtime-loaded modules, reflection-based usage, or files loaded via config

### 4. Entity / Data Architecture — 10/15 pts

**Status:** ⚠️ WARN

> 3 entities | 0 relationships | 3 bounded contexts

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Entities Detected | ⚠️ WARN | +4/7 | Only 3 entities found — domain model files may have been excluded by the file cap, or ORM patterns differ from expected (unknown ORM) |
| Microservice Boundaries | ✅ PASS | +5/5 | 3 bounded contexts identified |
| Relationships Detected | ⚠️ WARN | +1/3 | 0 relationships detected despite 3 entities. Repo may use Fluent API or private backing fields for navigation properties (not captured by regex analysis) |

**Recommendations:**
- 0 relationships detected — if the repo uses EF Core Fluent API or JPA XML mapping, relationships won't be found by regex. Consider enhancing _extract_db_entities_dotnet() to parse OnModelCreating() method bodies

### 5. Dependency Graph — 15/15 pts

**Status:** ✅ PASS

> 63 dep nodes | 80 edges | 3 tech items

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Dependency Map Built | ✅ PASS | +5/5 | 63 modules with 80 dependency edges |
| Mermaid Diagram | ✅ PASS | +5/5 | Mermaid diagram generated (12 edges shown) |
| Tech Stack Detection | ✅ PASS | +5/5 | 3 technologies identified: .NET Project File, .NET Solution, ASP.NET Framework (Legacy) |

### 6. AI Analysis Quality — 12/15 pts

**Status:** ⚠️ WARN

> Heuristic fallback (no API key) | 4 roadmap phases | target: ASP.NET Core 8, Entity Framework Core, Azure / AWS

| Check | Status | Points | Message |
|-------|--------|--------|---------|
| Executive Summary | ⚠️ WARN | +2/5 | Fallback text in place — set ANTHROPIC_API_KEY for AI-generated summary |
| Architecture Pattern | ✅ PASS | +5/5 | Pattern identified: 'Monolithic (inferred)' |
| Modernization Phases | ✅ PASS | +5/5 | 4 phases: Assessment & Audit, Foundation & Refactoring, Migration & Modernization... |

**Recommendations:**
- Set ANTHROPIC_API_KEY environment variable to get full AI-powered executive summary and modernization roadmap instead of fallback text


---

## Recommendations

- No endpoints detected. If this is an API server, check if it uses minimal API patterns (e.g. app.MapGet), XML config routing, or convention-based routing not captured by attribute scanning
- Dead file ratio is high — the heuristic flags files that are never imported by other analyzed files. For script/tool repos this is expected. Always validate before deleting flagged files.
- Always manually verify dead code results before deletion — static analysis cannot detect runtime-loaded modules, reflection-based usage, or files loaded via config
- 0 relationships detected — if the repo uses EF Core Fluent API or JPA XML mapping, relationships won't be found by regex. Consider enhancing _extract_db_entities_dotnet() to parse OnModelCreating() method bodies
- Set ANTHROPIC_API_KEY environment variable to get full AI-powered executive summary and modernization roadmap instead of fallback text

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
