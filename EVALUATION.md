# Reverse Engineer Skill — Evaluation Framework

This document describes how to interpret the automated evaluation report
(`{repo_name}_evaluation.md`) produced by the pipeline after every analysis run.

---

## What Is Evaluated

After the pipeline generates the three output files (SDD JSON, HTML Dashboard,
Markdown Report), the **Evaluator** runs automatically and scores six sections:

| # | Section                    | Max Points | What It Checks |
|---|----------------------------|------------|----------------|
| 1 | Parsing Quality            | 20 pts     | Files parsed, success rate, classes & methods extracted |
| 2 | API Endpoint Detection     | 20 pts     | Endpoints found, HTTP method variety, path format validity |
| 3 | Dead Code Analysis         | 15 pts     | Dead-file ratio plausibility, analysis completion, class-level detection |
| 4 | Entity / Data Architecture | 15 pts     | Entities detected, microservice boundaries, relationships mapped |
| 5 | Dependency Graph           | 15 pts     | Dependency map populated, Mermaid diagram generated, tech stack detected |
| 6 | AI Analysis Quality        | 15 pts     | Executive summary, architecture pattern, modernization phases |

**Total: 100 points**

---

## Confidence Bands

| Band       | Score Range | Meaning |
|------------|-------------|---------|
| HIGH       | ≥ 80 pts    | All key sections produced verifiable, substantive output |
| MEDIUM     | ≥ 60 pts    | Most sections reliable; manually review highlighted warnings |
| LOW        | ≥ 40 pts    | Partial results — static analysis coverage gaps likely |
| VERY LOW   | < 40 pts    | Major gaps — treat outputs as rough estimates only |

---

## Check Statuses

Each individual check within a section is assigned one of three statuses:

| Status | Icon | Meaning |
|--------|------|---------|
| PASS   | ✅   | The check passed — result in this area is reliable |
| WARN   | ⚠️   | Partial or borderline — review the message and spot-check |
| FAIL   | ❌   | Check failed — output in this area may be missing or incorrect |

The **section overall status** is the worst status across all its checks
(any FAIL → section FAIL; any WARN but no FAIL → section WARN).

---

## What Is Reliable vs Heuristic vs AI-Generated

### HIGH Reliability (Deterministic)

| Output                       | Notes |
|------------------------------|-------|
| File count                   | Exact filesystem walk — always correct |
| Language distribution        | Extension-based — highly accurate |
| Lines of code (if computed)  | Exact count |

### MEDIUM Reliability (Regex / Pattern Matching)

| Output                       | Notes |
|------------------------------|-------|
| Class & method extraction    | Regex-based; handles most patterns but misses reflection, macros, codegen |
| Import / dependency detection| Pattern-matched; dynamic imports (e.g. `importlib`, DI containers) missed |
| API endpoint extraction      | Attribute/decorator patterns; dynamic route registration missed |
| Entity / DB schema           | ORM annotation & namespace heuristics; Fluent API relationships not captured |
| Tech stack detection         | Scans package manager files; custom frameworks may be missed |

### LOW Reliability (Heuristic Estimation)

| Output                       | Notes |
|------------------------------|-------|
| Dead code detection          | Files never _imported_ by other analyzed files — always validate manually |
| Microservice boundaries      | Keyword clustering of entity names — rough semantic approximation |
| Dependency graph edges       | Only explicit imports; runtime wiring (DI, event bus) not captured |

### HIGH Reliability When API Key Set (AI-Generated)

| Output                       | Notes |
|------------------------------|-------|
| Executive summary            | Claude claude-sonnet-4-6 synthesis — falls back to template text without key |
| Architecture pattern         | AI inference from code structure — falls back to "Monolithic" without key |
| Modernization roadmap        | AI-generated phased plan — falls back to generic plan without key |
| Tech debt concerns           | AI-identified issues — generic list without key |

---

## How to Spot-Check Results

### Parsing Quality (Section 1)

1. Open `{repo_name}_sdd.json` → `module_inventory` array
2. Pick 5 random entries
3. Open the corresponding source file in the repository
4. Verify the `classes` list matches actual class declarations
5. Verify the `methods` list contains real function/method names
6. Check that `dependencies` reflect actual import statements

**Common issues:**
- `partial class` not detected in C# → check regex in `parsers.py`
- 0 classes in a JavaScript file → check if it uses `export default` with arrow functions
- 0 methods in a Go file → check if functions use receivers (`func (r *Repo) Name()`)

### API Endpoint Detection (Section 2)

1. Open `{repo_name}_sdd.json` → `api_catalog.endpoints`
2. Pick a controller/route file from the repository
3. Count the routes defined in that file manually
4. Compare against what appears in the SDD for that file

**Common issues:**
- ASP.NET minimal API (`app.MapGet(...)`) — not captured by attribute scanning
- Express.js router files using `router.get(...)` — may be missed if not in a standard pattern
- Spring Boot routes via XML config — not captured

**Rule of thumb:** If endpoint count is 0 and the repo is clearly an API server, the
routing pattern needs a new extractor in `analyzer.py → extract_api_endpoints()`.

### Dead Code Analysis (Section 3)

1. Pick 3 files from `dead_code_analysis.unreferenced_files` in the SDD
2. Search the **repository source** (not just analyzed files) for any import of that file
3. If found → false positive (expected; do not delete without checking)
4. Check the dead class list similarly

**Important:** Dead code detection is a **heuristic only**. It flags files that are never
imported by other _analyzed_ files. It cannot detect:
- Runtime module loading (`importlib.import_module`, reflection)
- Plugin architectures loaded via config
- Files used only in tests (if tests weren't in the analysis cap)

**Never delete flagged files without manual verification.**

### Entity / Data Architecture (Section 4)

1. Open `{repo_name}_sdd.json` → `data_architecture.entities`
2. Pick 5 entity names
3. Search the repository for each class name
4. Verify it is indeed an ORM entity (has `@Entity`, `[Key]`, inherits from a base model, etc.)
5. Check `fields` list matches actual properties
6. Check `relationships` list against navigation properties in the source

**If 0 entities detected:**
- Confirm domain/entity files are in `module_inventory` (they may have been excluded by the file cap)
- Increase layer-3 quota in `pipeline.py → SLOTS[3]` if domain files are being cut off
- Check if the ORM uses Fluent API only (no class-level annotations) — relationships won't be found

### Dependency Graph (Section 5)

1. Open the HTML dashboard → Dependency Graph section
2. Pick two modules you know are related in the source
3. Verify there is an edge between them in the graph
4. Check the Mermaid code in the Markdown report for the same edge

**Common issues:**
- Barrel files (`index.ts`, `__init__.py`) appear as highly connected — normal
- Circular dependencies may appear as bidirectional edges — verify if real
- Standard library imports (e.g. `System.*`, `java.util.*`) are intentionally excluded

### AI Analysis Quality (Section 6)

1. Check `executive_summary.purpose` in the SDD for substantive text
2. Verify the architecture pattern matches what you see in the codebase
3. Review the modernization phases for plausibility given the tech stack
4. If fallback text appears, set `ANTHROPIC_API_KEY` and re-run

---

## Interpreting the Evaluation Output File

The evaluation saves to `outputs/{repo_name}/{repo_name}_evaluation.md`.
The console also prints a condensed score table after the pipeline completes.

```
  Evaluation Score  : 82/100 pts  [HIGH confidence]
     ✅ 1. Parsing Quality                      18/20 pts
     ✅ 2. API Endpoint Detection                18/20 pts
     ✅ 3. Dead Code Analysis                    12/15 pts
     ⚠️ 4. Entity / Data Architecture            10/15 pts
     ✅ 5. Dependency Graph                      15/15 pts
     ✅ 6. AI Analysis Quality                   15/15 pts
```

Each section with ⚠️ or ❌ includes recommendation text explaining what to check.

---

## When to Re-Run the Pipeline

Consider re-running with adjustments when:

| Situation | Action |
|-----------|--------|
| 0 entities detected | Increase `SLOTS[3]` in `pipeline.py` for more domain files |
| 0 API endpoints | Add a new route extractor for the repo's routing pattern |
| <50% parse success | Add file extension support in `loaders.py` |
| Fallback AI text | Set `ANTHROPIC_API_KEY` environment variable |
| Very high dead file ratio | The repo has many standalone scripts — expected |
| 0 classes in C# | Check if `partial class` regex is correctly handled |

---

## Scoring Rationale

### Why 100-Point Scale?

A simple 100-point scale with weighted sections makes it easy to:
- Track improvement over time (re-run after adding new parsers)
- Compare analysis quality across different repository types
- Set thresholds for automated CI gates

### Why Not Score Accuracy?

The evaluator measures **output completeness and plausibility**, not ground-truth accuracy,
because the ground truth (actual number of classes, real dead code, etc.) would require
running the code or knowing the source intimately.

The evaluation answers: _"Did the pipeline produce substantive, internally consistent output?"_
not _"Is every detected class actually a class?"_

Manual spot-checking (described above) is the correct way to assess accuracy.

---

## Adding Custom Checks

To add a new check, edit `engine/evaluator.py`:

```python
# In any _eval_* function, call _check() and add to checks list:
checks.append(_check(
    name="My Custom Check",       # Short name
    status="PASS",                # "PASS" | "WARN" | "FAIL"
    points_awarded=5,             # Points earned for this result
    points_possible=5,            # Max points for this check
    message="Explanation text"    # Human-readable explanation
))
score += 5
```

Then add the section to the `sections` list in `evaluate_pipeline_output()`.

---

_Reverse Engineer Skill — Evaluation Framework Documentation_
