# Architecture — Reverse Engineer Skill v3.0

This document is the authoritative technical reference for the project. It covers every file, every module, every function, the complete data flow, and the rationale behind every design decision.

**Current version:** 3.0.0  
**Engine:** `engine/` package — 13 modules  
**Entry point:** `reverse_engineer_skill.py` — 42 lines  
**Verified against:** nopCommerce (3,114 files → 284 API endpoints, 51 entities, 7 bounded contexts, 292 files analyzed)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Complete File Reference](#2-complete-file-reference)
3. [Data Flow — End to End](#3-data-flow--end-to-end)
4. [Engine Package — Module by Module](#4-engine-package--module-by-module)
   - [entry point — reverse_engineer_skill.py](#entry-point--reverse_engineer_skillpy)
   - [engine/__init__.py](#engine__init__py)
   - [engine/loaders.py](#engineloaderspy)
   - [engine/parsers.py](#engineparserspy)
   - [engine/analyzer.py](#engineanalyzerpy)
   - [engine/ai_analysis.py](#engineai_analysispy)
   - [engine/output_manager.py](#engineoutput_managerpy)
   - [engine/evaluator.py](#engineevaluatorpy)
   - [engine/pipeline.py](#enginepipelinepy)
   - [engine/generators/sdd.py](#enginegeneratorssddpy)
   - [engine/generators/dashboard.py](#enginegeneratorsdashboardpy)
   - [engine/generators/report.py](#enginegeneratorsreportpy)
5. [Claude Code Integration](#5-claude-code-integration)
6. [GitHub Copilot Integration](#6-github-copilot-integration)
7. [VS Code Settings](#7-vs-code-settings)
8. [Template Files](#8-template-files)
9. [Design Decisions](#9-design-decisions)
10. [Token Usage & Cost](#10-token-usage--cost)

---

## 1. Project Overview

The Reverse Engineer Skill is a **pure-Python static analysis engine** that accepts any public GitHub repository URL and produces five professional output files — without executing the analysed code.

```
Input:  GitHub URL
        │
        ▼
  reverse_engineer_skill.py   (42-line entry point)
        │
        ▼
  engine/pipeline.py          (9-stage orchestrator)
        │
  ┌─────┴──────────────────────────────────────────┐
  │  engine/loaders.py         File discovery        │
  │  engine/parsers.py         5 lang parsers +      │
  │                            ORM entity extractors │
  │  engine/analyzer.py        13 analysis functions │
  │  engine/ai_analysis.py     Claude API            │
  │  engine/evaluator.py       Quality scorer        │
  │  engine/output_manager.py  File writer           │
  │  engine/generators/        3 output builders     │
  └────────────────────────────────────────────────┘
        │
  ┌─────┴──────────────────────────┐
  │  outputs/{repo}/               │
  │  ├── {repo}_sdd.json           │
  │  ├── {repo}_dashboard.html     │
  │  ├── {repo}_report.md          │
  │  ├── {repo}_evaluation.md      │
  │  └── manifest.json             │
  └────────────────────────────────┘
```

---

## 2. Complete File Reference

### Project root

```
reverse-eng-proj/
├── reverse_engineer_skill.py       75 lines  CLI entry point; --no-ai flag; imports engine.pipeline
├── requirements.txt                 1 line   anthropic>=0.40.0
├── README.md                       User documentation with step-by-step guides
├── ARCHITECTURE.md                 This file — complete technical reference
└── EVALUATION.md                   Guide to interpreting {repo}_evaluation.md outputs
```

### `engine/` package

```
engine/
├── __init__.py           26 lines   Package exports + version string (3.0.0)
├── loaders.py            89 lines   load_repo · SUPPORTED_EXTENSIONS · SKIP_DIRS
├── parsers.py           655 lines   detect_language · parse_python · parse_java
│                                    parse_dotnet · parse_js_ts · parse_file
│                                    _extract_db_entities_dotnet
│                                    _extract_db_entities_java
│                                    _extract_db_entities_python
├── analyzer.py          629 lines   generate_report · build_dependency_map
│                                    generate_mermaid · extract_api_endpoints
│                                    generate_openapi_spec · detect_dead_code
│                                    detect_tech_stack · detect_platform
│                                    detect_architecture_layers · find_top_modules
│                                    extract_external_deps
│                                    detect_database_schema
│                                    suggest_microservice_data_boundaries
├── ai_analysis.py       530 lines   claude_analyze · ai_executive_summary
│                                    ai_modernization_roadmap · ai_business_logic_analysis
├── output_manager.py    154 lines   OutputManager class
├── evaluator.py         848 lines   evaluate_pipeline_output · write_evaluation_md
│                                    _eval_parsing_quality · _eval_api_endpoints
│                                    _eval_dead_code · _eval_data_architecture
│                                    _eval_dependency_graph · _eval_ai_analysis
├── pipeline.py          347 lines   clone_repo · repo_name_from_url · run_pipeline
└── generators/
    ├── __init__.py        9 lines   Empty package init
    ├── sdd.py           330 lines   generate_sdd (14-section SDD JSON)
    ├── report.py        530 lines   generate_md_report (12-section Markdown)
    └── dashboard.py   2,200 lines   generate_html_dashboard (6-section Apple HTML)
```

### Integration files

```
.claude/
└── commands/
    └── reverse-engineer.md      /reverse-engineer slash command for Claude Code

.github/
├── copilot-instructions.md      Auto-loaded by Copilot Chat in this workspace
└── prompts/
    ├── reverse-engineer.prompt.md   mode: agent — full analysis pipeline
    └── improve-parser.prompt.md     mode: ask   — add/improve a language parser

.vscode/
└── settings.json                chat.promptFiles + Copilot workspace settings

templates/
├── sdd_template.json            SDD schema reference with placeholder comments (14 sections)
├── dashboard_template.html      Design reference with DATA object documentation (6 sections)
└── report_template.md           Report structure reference (12 sections + appendix)
```

---

## 3. Data Flow — End to End

```
GitHub URL  (e.g. https://github.com/nopSolutions/nopCommerce)
    │
    ▼ Stage 1: clone_repo()
    git clone --depth=1 <url> → temp dir    [~30-90s for large repos]
    │
    ▼ Stage 2: load_repo()
    os.walk() → skip SKIP_DIRS → read files matching SUPPORTED_EXTENSIONS
    Returns: list of {path, content} dicts  [3,114 files for nopCommerce]
    │
    ▼ Stage 3: Layer-balanced file cap
    if len(files) > 300:
        SLOTS = {0:75, 1:75, 2:40, 3:60, 4:30, 5:20}   # per-layer quotas
        _layer(f) → 0=controllers, 1=services, 2=repos,
                    3=domain/entity, 4=models/dtos, 5=rest
        files = layer-balanced selection ≤ 300
    [Guarantees domain/entity files always appear even when ctrl+svc alone > 300]
    │
    ▼ Stage 3 cont.: parse_file() [× up to 300]
    detect_language() → dispatch to:
      parse_python()   → classes, methods, Flask/FastAPI routes, SQLAlchemy/Django entities
      parse_java()     → classes, methods, Spring routes, JPA/Hibernate entities
      parse_dotnet()   → classes, interfaces, ASP.NET routes, EF Core entities
      parse_js_ts()    → classes, functions, Express routes
    Returns: list of parsed dicts (each includes "db_entities" key)
    │
    ▼ Stage 4: Analysis Engine
    generate_report()                → {total_files, total_classes, total_methods, languages}
    build_dependency_map()           → {module_stem: set(dependencies)}
    generate_mermaid()               → Mermaid graph TD string (≤80 edges)
    find_top_modules()               → [(module, connection_count), ...] top 10
    │
    ▼ Stage 5: APIs & Dead Code
    extract_api_endpoints()          → flat list of {path, methods, class, method, file}
    generate_openapi_spec()          → OpenAPI 3.0 JSON dict
    detect_dead_code()               → {dead_files: [...], dead_classes: [...]}
    detect_tech_stack()              → ["ASP.NET Core", "Docker", ...]
    detect_database_schema()         → {entity_count, relationship_count, entities: [...]}
    │
    ▼ Stage 6: AI Analysis (requires ANTHROPIC_API_KEY)
    ai_executive_summary()           → {purpose, architecture_pattern, tech_debt_concerns, priority}
    ai_modernization_roadmap()       → {phases, target_stack, microservices, effort, risk_factors}
    ai_business_logic_analysis()     → {business_domain, what_it_does, core_workflows,
                                        user_roles, key_business_rules, data_entities_explained,
                                        integrations, fallback_used}
    detect_platform()                → ".NET / Windows Server"
    detect_architecture_layers()     → ["API Layer", "Service Layer", ...]
    suggest_microservice_data_boundaries() → [{name, entities, color, entity_count}, ...]
    [All three AI functions fall back to deterministic heuristics if API key is absent or call fails]
    │
    ▼ Stage 7: OutputManager + Generators
    om = OutputManager(repo_name)               → creates outputs/{repo_name}/
    generate_sdd(...)          → dict           → om.write_json("{repo}_sdd.json")
    generate_html_dashboard(…) → str            → om.write_text("{repo}_dashboard.html")
    generate_md_report(...)    → str            → om.write_text("{repo}_report.md")
    om.write_manifest(...)                      → manifest.json with metrics + file sizes
    │
    ▼ Stage 8: Evaluator
    evaluate_pipeline_output(...)    → {total_score, confidence, sections, recommendations}
    write_evaluation_md(evaluation)  → str      → om.write_text("{repo}_evaluation.md")
    [100-pt quality score across 6 sections: PASS/WARN/FAIL per check]
    │
    ▼ Stage 9: Cleanup + Console summary
    shutil.rmtree(tmp_dir)           → temp clone deleted even on exception
    Console prints: file list, analysis metrics, quality score table
```

---

## 4. Engine Package — Module by Module

---

### Entry point — `reverse_engineer_skill.py`

**42 lines.** The entire file is:

```python
import sys, io

# UTF-8 fix for Windows cp1252 terminals
if sys.stdout.encoding not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from engine.pipeline import run_pipeline

def main():
    """CLI entry point. Validates arguments and starts the pipeline."""
    if len(sys.argv) < 2:
        print("Usage: python reverse_engineer_skill.py <github-repo-url>")
        sys.exit(1)
    run_pipeline(sys.argv[1])

if __name__ == "__main__":
    main()
```

**Why the UTF-8 wrapper?**  
Windows terminals default to `cp1252`. Any `print()` containing a non-ASCII character (including emoji in evaluation output like ✅, ⚠️, ❌) raises `UnicodeEncodeError`. Wrapping at startup fixes all cases in one place — avoids auditing every print in every module.

---

### `engine/__init__.py`

**26 lines.** Sets version and re-exports the public API:

```python
__version__ = "3.0.0"
from engine.pipeline import run_pipeline, clone_repo, repo_name_from_url
__all__ = ["run_pipeline", "clone_repo", "repo_name_from_url"]
```

Version history: 1.0.0 (monolithic script) → 2.0.0 (modular engine package) → 3.0.0 (entity detection, evaluator, layer-balanced cap).

---

### `engine/loaders.py`

**89 lines.** Responsible for discovering and reading source files.

**Constants:**

| Constant | Purpose |
|----------|---------|
| `SUPPORTED_EXTENSIONS` | 16 extensions: `.py .java .cs .ts .tsx .js .jsx .vb .go .rb .php .swift .kt .cpp .h` |
| `SKIP_DIRS` | 20 directories to always skip: `tests/`, `node_modules/`, `bin/`, `obj/`, `.git/`, `dist/`, `build/`, `migrations/`, etc. |

**`load_repo(repo_path, extensions=None) → list[dict]`**

- Walks the directory tree with `os.walk`
- Filters dirs in-place (`dirs[:] = ...`) to prevent descending into `SKIP_DIRS`
- Checks match case-insensitively: `d.lower() not in SKIP_DIRS`
- Reads each matching file as UTF-8 with `errors="ignore"` (binary-looking files don't crash)
- Returns `[{"path": str, "content": str}, ...]`

---

### `engine/parsers.py`

**655 lines.** Five language parsers, three ORM entity extractors, plus the dispatcher.

**Universal parser contract** — every `parse_X` returns:

```python
{
    "file":         str,          # absolute path to source file
    "language":     str,          # canonical language name
    "classes":      list[str],    # class + interface names defined here
    "methods":      list[str],    # method/function names (keywords excluded)
    "imports":      list[str],    # raw import strings as written in source
    "dependencies": list[str],    # deduplicated top-level namespace names
    "routes":       list[dict],   # [{path, methods, class, method}, ...]
    "db_entities":  list[dict],   # [{name, table, fields, relationships, file}, ...]
}
```

**All parsers use regex only** — no AST, no tree-sitter, no language-specific library.

---

**`detect_language(file_name) → str | None`**

Extension lookup dict mapping `.cs → "dotnet"`, `.ts/.tsx → "typescript"`, etc. Returns `None` for unrecognised extensions — those files are skipped by `parse_file()`.

---

**`parse_python(file_path, code) → dict`**

| Element | Regex |
|---------|-------|
| Classes | `^class\s+(\w+)` (MULTILINE) |
| Instance methods | `^\s+def\s+(\w+)` (MULTILINE) |
| Top-level functions | `^def\s+(\w+)` (MULTILINE) |
| `import X` | `^import\s+([\w\.]+)` |
| `from X import` | `^from\s+([\w\.]+)\s+import` |
| Flask `@app.route` | `@\w+\.route\(['"]([^'"]+)['"]...)` |
| FastAPI/DRF `@app.get` | `@(?:app|router)\.(get|post|put|delete|patch)\(...` |

**`_extract_db_entities_python(file_path, code, classes)`** detects:
- SQLAlchemy: `Column()`, `relationship()`, `__tablename__`
- Django ORM: `models.Model`, `ForeignKey()`, `ManyToManyField`

---

**`parse_java(file_path, code) → dict`**

| Element | Regex / approach |
|---------|-----------------|
| Classes | Access modifier + optional `abstract` + `class\s+(\w+)` |
| Interfaces | `interface\s+(\w+)` |
| Methods | Access modifier + return type + `(\w+)\s*\(` — filtered against keyword set |
| Imports | `^import\s+([\w\.\*]+);` |
| Spring `@GetMapping` | `@(Get|Post|Put|Delete|Patch)Mapping\(['"]([^'"]+)['"]` |
| Spring `@RequestMapping` | `@RequestMapping\([^)]*value\s*=\s*['"]([^'"]+)` |

**`_extract_db_entities_java(file_path, code, classes)`** detects:
- JPA/Hibernate: `@Entity`, `@Table(name=...)`, `@ManyToOne`, `@OneToMany`, `@ManyToMany`

---

**`parse_dotnet(file_path, code) → dict`**

The most complex parser, handling ASP.NET Core attribute routing.

| Element | Approach |
|---------|----------|
| Classes | Access modifier + optional `abstract/sealed/partial/static` + `class\s+(\w+)` |
| Interfaces | `interface\s+(\w+)` |
| Methods | Access modifier + return type + `(\w+)\s*\(` — filtered against `_kw` set |
| `using` statements | `^using\s+([\w\.]+);` |
| Namespace | `^namespace\s+([\w\.]+)` (both traditional and file-scoped with `;`) |
| Class-level `[Route]` | Extracted first as `ctrl_prefix` — prepended to all method routes |
| HTTP attributes | **Two-pass**: find `[HttpGet/Post/Put/Delete/Patch/Route]` → scan 600 chars ahead for method signature |

**Critical C# fix:** The class regex includes `partial` in the modifier group: `(?:(?:abstract|sealed|partial|static)\s+)*class` — without this, `public partial class X` (common in .NET) produces zero detected classes.

**`_extract_db_entities_dotnet(file_path, code, classes)`** detects:

- **Pattern 1 — DbContext subclass:** If class inherits from `DbContext`, extracts all `DbSet<X>` registrations as entities
- **Pattern 2 — Entity/domain model:** If file has domain namespace pattern (`[\w.]*Domain[\w.]*`), `BaseEntity` inheritance, navigation property keywords (`virtual ICollection<X>`), or EF Core attributes (`[Key]`, `[Table]`, `[Column]`, `[ForeignKey]`):
  - Extracts scalar fields (non-navigation properties)
  - Extracts one-to-many (`virtual ICollection<X>`) and many-to-one (`virtual X`) relationships

---

**`parse_js_ts(file_path, code) → dict`**

| Element | Regex |
|---------|-------|
| Classes | `class\s+(\w+)` |
| Interfaces (TS only) | `interface\s+(\w+)` |
| Functions | `function\s+(\w+)` and arrow/const functions |
| ES module imports | `from\s+['"]([^'"]+)['"]` |
| CommonJS imports | `require\(['"]([^'"]+)['"]\)` |
| Express routes | `(?:app|router)\.(get|post|put|delete|patch)\(['"]([^'"]+)['"]` |

---

**`parse_file(file_record) → dict | None`**

Dispatcher: calls `detect_language()` then routes to the correct `parse_X`. Returns `None` for unsupported extensions.

---

### `engine/analyzer.py`

**629 lines.** Thirteen analysis functions.

---

**`generate_report(parsed) → dict`**

Single-pass aggregation:

```python
{"total_files": 292, "total_classes": 284, "total_methods": 2301, "languages": {"dotnet": 292}}
```

---

**`build_dependency_map(parsed) → dict`**

Creates `{module_stem: set(dependencies)}`. Stem = filename without extension.

---

**`generate_mermaid(parsed, max_links=80) → str`**

Builds a Mermaid `graph TD` diagram. Skips nodes in `IGNORE` set (standard library roots: `os`, `sys`, `java`, `Microsoft`, `react`, etc.). Sanitises node names. Stops at 80 edges.

---

**`extract_api_endpoints(parsed) → list`**

Flattens all `routes` lists into one flat list with source file added.

---

**`generate_openapi_spec(endpoints, repo_name) → dict`**

Converts endpoint list to OpenAPI 3.0. Path params normalised (`<id>` → `{id}`). Always valid JSON — `/health` placeholder when no endpoints found.

---

**`detect_dead_code(parsed) → dict`**

Two-pass heuristic:
1. Build `all_refs` — every import string, dependency, and class name across all files
2. Flag file if its stem and none of its classes appear in `all_refs`
3. Exclude entry-point filenames (`main`, `app`, `index`, `startup`, `program`, etc.)

Returns `{"dead_files": [...], "dead_classes": [...]}`.

---

**`detect_tech_stack(parsed, repo_path) → list`**

Two-pass detection:
1. Dependency scan — checks all `dependencies` strings for framework signatures
2. Config file scan — checks for `Dockerfile`, `package.json`, `pom.xml`, `*.csproj`, `*.sln`, etc.

---

**`detect_platform(parsed) → str`**

Maps primary language to runtime:

| Primary language | Platform |
|-----------------|---------|
| `dotnet` | `.NET / Windows Server` |
| `java` | `JVM / Linux` |
| `python` | `Python / Linux` |
| `typescript` or `javascript` | `Node.js` |
| *(other)* | `Cross-platform` |

---

**`detect_architecture_layers(parsed) → list`**

Scans file paths for keyword patterns → layer labels (API, Business Logic, Data Access, Utility, Configuration, View).

---

**`find_top_modules(dep_map, n=10) → list`**

Sorts modules by outgoing dependencies (fan-out), returns top `n` as `[(name, count)]`.

---

**`extract_external_deps(parsed) → list`**

Collects all unique dependency strings, sorts, returns up to 100.

---

**`detect_database_schema(parsed) → dict`**

Aggregates `db_entities` from all parsed files:

1. Merge duplicates by entity name (later occurrences win)
2. Count total entities and total relationships
3. Return:

```python
{
    "entity_count":       51,
    "relationship_count": 0,
    "has_schema":         True,
    "entities": [
        {
            "name":          "Customer",
            "table":         "Customer",
            "fields":        [{"name": "Email", "type": "string"}, ...],
            "relationships": [],
            "file":          "Customer.cs"
        },
        ...
    ]
}
```

---

**`suggest_microservice_data_boundaries(db_schema, modernization=None) → list`**

Semantic domain clustering across 7 domain keyword buckets:

| Cluster | Keywords |
|---------|---------|
| Customer / Identity | customer, user, account, identity, member, profile, auth, role, permission |
| Product / Catalog | product, catalog, category, item, sku, inventory, price, stock, attribute |
| Order / Commerce | order, cart, checkout, payment, invoice, transaction, shipment, discount, coupon |
| Content / Media | content, blog, post, article, review, comment, media, image, video, news |
| Notification / Comms | notification, email, sms, campaign, newsletter, message, alert, template |
| Configuration | setting, configuration, locale, currency, country, language, theme, plugin |
| Search / Analytics | search, index, analytics, report, stat, log, audit, metric, export |

**Fallback:** When no entities detected, derives boundaries from `modernization.microservices_boundaries` AI output (entities list will be empty, marked as "From AI roadmap").

Returns:
```python
[{"name": "Product / Catalog", "entities": ["Product", "Category", ...], "color": "#4cc9f0", "entity_count": 12}, ...]
```

---

### `engine/ai_analysis.py`

**275 lines.** Wraps the Anthropic API with structured prompts and always provides deterministic fallback.

**`claude_analyze(prompt, max_tokens=2000) → str | None`**

```python
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=max_tokens,
    messages=[{"role": "user", "content": prompt}]
)
return response.content[0].text
```

Returns `None` (never raises) on `ImportError`, missing API key, or any API failure.

---

**`ai_executive_summary(parsed, report, repo_name) → dict`**

Builds a prompt with the top 20 file summaries and asks for JSON:

```json
{
  "purpose":               "Natural-language description",
  "architecture_pattern":  "MVC Monolith | Layered N-Tier | ...",
  "tech_debt_concerns":    ["concern1", "concern2"],
  "modernization_priority": "HIGH | MEDIUM | LOW",
  "priority_reasoning":    "Why this priority"
}
```

**Fallback:** Returns heuristic values including a plain-English purpose from language + file counts. Priority defaults to `HIGH` for codebases with >500 methods.

---

**`ai_modernization_roadmap(parsed, report, repo_name, tech_stack) → dict`**

Asks for a phased migration plan:

```json
{
  "target_stack":             ["technology1", "..."],
  "phases":                   [{"phase": 1, "title": "...", "duration": "...", "tasks": [...], "risk": "LOW|MEDIUM|HIGH"}],
  "microservices_boundaries": ["Service A", "Service B"],
  "estimated_total_effort":   "8-13 months",
  "risk_factors":             ["risk1", "risk2"]
}
```

**Fallback:** Returns a hardcoded 4-phase plan with language-appropriate target stack.

---

### `engine/output_manager.py`

**154 lines.** Encapsulates all file-writing for one pipeline run.

```python
class OutputManager:
    def __init__(self, repo_name: str, base_dir: str = "outputs")
    def path_for(self, filename: str) -> Path
    def write_json(self, filename: str, data: dict, indent: int = 2) -> Path
    def write_text(self, filename: str, content: str) -> Path
    def write_manifest(self, **metrics) -> Path
    def summary_lines(self) -> list[str]
```

All writes are tracked in `self._written` so `write_manifest()` automatically embeds accurate file sizes.

---

### `engine/evaluator.py`

**848 lines.** Automated 100-point quality scoring engine. Runs after every pipeline execution.

**`evaluate_pipeline_output(...) → dict`**

Scores six sections:

| Section | Max | Checks |
|---------|-----|--------|
| 1. Parsing Quality | 20 pts | Files parsed, success rate, classes extracted, methods extracted |
| 2. API Endpoint Detection | 20 pts | Endpoints found, HTTP method variety, path format validity |
| 3. Dead Code Analysis | 15 pts | Dead-file ratio plausibility, analysis completion, class-level |
| 4. Entity / Data Architecture | 15 pts | Entities detected, boundaries, relationships |
| 5. Dependency Graph | 15 pts | Dep map populated, Mermaid diagram, tech stack |
| 6. AI Analysis Quality | 15 pts | Executive summary, architecture pattern, roadmap phases |

Each check returns `{"name", "status": PASS|WARN|FAIL, "points_awarded", "points_possible", "message"}`.

**Confidence bands:**

| Band | Score |
|------|-------|
| HIGH | ≥ 80 pts |
| MEDIUM | ≥ 60 pts |
| LOW | ≥ 40 pts |
| VERY LOW | < 40 pts |

**`write_evaluation_md(evaluation) → str`**

Renders the evaluation result as a Markdown document with:
- ASCII progress bar + score
- Section scores table
- Per-section check detail with PASS/WARN/FAIL rows
- Recommendations list
- Interpretation guide (reliability table, spot-check instructions)

---

### `engine/pipeline.py`

**347 lines.** The 9-stage orchestrator.

**`clone_repo(url, target_dir) → None`**

```python
subprocess.run(
    ["git", "clone", "--depth=1", url, target_dir],
    capture_output=True, text=True
)
```

`--depth=1` — shallow clone; commit history is irrelevant for static analysis. List args — avoids shell injection, handles Windows paths with spaces.

**`repo_name_from_url(url) → str`**

Strips trailing slashes and `.git`, takes the last path segment, sanitises to `[a-zA-Z0-9_\-]`.

**`run_pipeline(repo_url, skip_ai=False) → None`**

`skip_ai=True` bypasses all Anthropic API calls and forces heuristic fallbacks.
Used by `--no-ai` CLI flag and the GitHub Copilot agent-mode workflow.

```python
tmp_dir = tempfile.mkdtemp(prefix="rev_eng_")
try:
    ... # all 9 stages
finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
```

**Layer-balanced file cap (Stage 3):**

```python
FILE_CAP = 300
SLOTS = {0: 75, 1: 75, 2: 40, 3: 60, 4: 30, 5: 20}

def _layer(f):
    name     = os.path.basename(f["path"]).lower()
    path_low = f["path"].lower().replace("\\", "/")
    if "controller"                              in name: return 0
    if "service"                                 in name: return 1
    if "repository" in name or "repo" in name:           return 2
    if any(s in path_low for s in ["/domain/", "/entities/", "/entity/"]): return 3
    if "model" in name or "dto" in name:                 return 4
    return 5

buckets = defaultdict(list)
for f in files:
    buckets[_layer(f)].append(f)
files = []
for layer in sorted(SLOTS):
    files.extend(buckets[layer][:SLOTS[layer]])
files = files[:FILE_CAP]
```

**Why layer-balanced instead of simple sort?**  
nopCommerce has 136 controllers + 218 services = 354 files before any domain/entity files appear. A simple priority sort fills the 300-file cap with controllers and services, leaving zero slots for the 1,419 domain files that contain ORM entities. The quota system guarantees 60 domain file slots regardless of how many higher-priority files exist.

---

### `engine/generators/sdd.py`

**330 lines.** Assembles the 14-section SDD JSON dict.

**`generate_sdd(...) → dict`**

All 14 sections:

| Section | Source |
|---------|--------|
| `sdd_metadata` | Schema version, `datetime.now(UTC)`, generator attribution |
| `project` | `repo_name`, `repo_url`, `detect_platform()`, `tech_stack`, `detect_architecture_layers()` |
| `executive_summary` | `ai_executive_summary()` result or fallback |
| `codebase_metrics` | `report` dict + endpoint/dead code counts + most-connected modules |
| `architecture` | Pattern, layers, components (unique classes, capped at 60), Mermaid |
| `module_inventory` | All parsed files — classes, methods (top 30), routes, dependencies |
| `api_catalog` | OpenAPI 3.0 spec + flat endpoint list |
| `dependency_analysis` | Top-10 modules, external deps, dep map sample (25 modules × 10 deps) |
| `dead_code_analysis` | Dead files (names + full paths), dead classes (top 30) |
| `data_architecture` | Entity count, entities list, microservice boundaries, migration notes |
| `business_logic` | `ai_business_logic_analysis()` result — domain, workflows, roles, rules, entity glossary |
| `modernization_roadmap` | `ai_modernization_roadmap()` result or fallback |
| `risk_assessment` | 4 risk records with severity computed from metrics |
| `tech_debt_inventory` | 5 debt categories with counts embedded |

Written with `json.dump(..., ensure_ascii=False, default=list)` — Unicode class names preserved, Python `set` objects serialised as lists.

---

### `engine/generators/dashboard.py`

**2,084 lines.** The largest module. Generates the complete self-contained HTML dashboard.

**`generate_html_dashboard(...) → str`**

Returns a complete HTML document as a Python f-string. All analysis data is embedded in a `const DATA = {...}` JavaScript object so the file opens in any browser without a server.

**CDN dependencies (rendering only — no data sent externally):**
- `chart.js@4.4.0` — horizontal bar charts for language distribution and top modules
- `mermaid@10` — dependency graph diagram rendering
- `vis-network@9.1.9` — entity relationship network in the Data Architecture section

**Six sidebar sections:**

| Section | Key UI elements |
|---------|----------------|
| Overview | Metric cards with count-up animation · Chart.js horizontal bar (languages) · tech stack badges · most-connected-modules bar |
| Architecture | Mermaid graph (`theme: 'default'`, light) · architectural layer list |
| API Endpoints | Live search input with result count · HTTP method colour badges · sortable endpoint table |
| Dead Code | SVG percentage ring (r=40, circumference=251.2) · unreferenced file list · unreferenced class list |
| Modernization | Vertical timeline for phases with connector line · risk badge per phase · microservice boundary grid · target stack badges |
| Data Architecture | vis.js Network entity graph (nodes colored by bounded context) · metric cards · boundary cards with entity chips · entity table |

**`buildDataArch()` function:** Builds Data Architecture section DOM — entity count/boundary count/relationship count metric cards, vis.js network container, boundary-colored entity chips grid, full entity table.

**`initEntityNetwork()` function:** Creates vis.js Network with boundary-colored nodes, edges from entity relationships. Deferred rendering via `requestAnimationFrame()` to avoid race conditions. One-time initialisation guard (`entityNetInited` flag).

**JavaScript f-string safety rules:**
- All `{` → `{{`, all `}` → `}}` inside the Python f-string
- Template literals use `${{varName}}`
- No `\n` characters inside single-line JS comments (causes `SyntaxError` in the generated HTML)
- Emoji characters are safe in string literals

**Responsive behaviour:**
- `< 860px`: sidebar translates off-screen (`transform: translateX(-240px)`)
- Hamburger button toggles `sidebar.open` class
- Overlay div closes sidebar on click-outside

---

### `engine/generators/report.py`

**530 lines.** Builds the Markdown report as a Python f-string.

**`generate_md_report(...) → str`**

12 sections + appendix:

| # | Section | Key content |
|---|---------|------------|
| 1 | Executive Summary | Purpose · attribute table (arch, priority, platform, tech stack, totals) |
| 2 | **Business Logic & Functional Overview** | Business domain · what it does · core workflows · user roles · business rules · entity glossary · integrations |
| 3 | Codebase Metrics | Language distribution table · key count table |
| 4 | Architecture Overview | Mermaid code fence · architectural layer list |
| 5 | Module Inventory | `#### filename` entries with classes/methods (first 40 files) |
| 6 | API Catalog | method/path/handler/file table (first 50 endpoints) + OpenAPI JSON block |
| 7 | Dependency Analysis | Top-10 modules table · external deps code block |
| 8 | Dead Code Analysis | Warning note · unreferenced files/classes lists |
| 9 | Tech Debt Inventory | AI concerns list · tech debt severity table |
| 10 | Modernization Roadmap | Target stack · phases with task lists · microservice list · risks · effort |
| 11 | Data Architecture | Schema summary table · entity table · boundary breakdown · 5-step migration guidance |
| 12 | Risk Assessment | Four-row risk matrix |
| — | Appendix | How generated · 5 output files table · limitations · extending guide |

---

## 5. Claude Code Integration

### How slash commands work

Claude Code scans `.claude/commands/` at startup. Each `.md` file becomes a `/commandname` command.

When `/reverse-engineer <url>` is typed:
1. Claude reads `.claude/commands/reverse-engineer.md`
2. Replaces `$ARGUMENTS` with the URL
3. Claude checks for the script and runs it

**Command flow:**

```
User: /reverse-engineer https://github.com/owner/repo
  │
  ├─ bash: test -f reverse_engineer_skill.py   → "found"
  │
  └─ bash: python reverse_engineer_skill.py "https://github.com/owner/repo"
              │
              ├─ runs all 9 pipeline stages
              ├─ generates outputs/{repo}/  (5 files)
              └─ prints summary + quality score
```

**Critical rule in the command file:** "Do NOT clone the repo separately — the script clones internally." This prevents a double-clone bug.

**Fallback path:** If the script is missing, the command file instructs Claude to manually use Glob, Read, and Grep tools to analyse the repo and generate the files following the templates.

---

## 6. GitHub Copilot Integration

### `.github/copilot-instructions.md`

Auto-loaded by GitHub Copilot Chat whenever this workspace is open in VS Code. Contents:
- What the skill does and how to run it
- Current module structure (stage map)
- How to add a new language parser (including `db_entities` requirement)
- SDD JSON key schema
- Dashboard `DATA` object key schema
- Coding conventions

### `.github/prompts/reverse-engineer.prompt.md`

YAML frontmatter: `mode: agent` — Copilot acts autonomously, running terminal commands and creating files without asking permission.

### `.github/prompts/improve-parser.prompt.md`

YAML frontmatter: `mode: ask` — Copilot provides guidance but doesn't act autonomously. Appropriate for parser changes that require developer review.

---

## 7. VS Code Settings

`.vscode/settings.json`:

| Setting | Effect |
|---------|--------|
| `chat.promptFiles: true` | Enables the "attach prompt" UI in Copilot Chat |
| `chat.promptFilesLocations` | Tells VS Code where `.prompt.md` files live |
| `github.copilot.chat.codeGeneration.instructions` | Injected into every Copilot code generation |
| `python.analysis.extraPaths: ["."]` | Makes `engine` importable by Pylance without `src/` prefix |

---

## 8. Template Files

The three files in `templates/` are **development reference only** — they are never read at runtime by any module. The actual output is generated programmatically by the three generator modules.

| File | Sections | Purpose |
|------|---------|---------|
| `sdd_template.json` | 13 | SDD schema with `_comment`/`_usage` metadata keys and `{{PLACEHOLDER}}` markers |
| `dashboard_template.html` | 6 | Design reference with DATA object key documentation in HTML comment header |
| `report_template.md` | 11 + appendix | Report structure with `{{PLACEHOLDER}}` markers |

**Two purposes:**
1. **Development reference** — contributors can read the schema without running the tool
2. **LLM context** — when Claude Code performs manual analysis (script missing), templates define exactly what to generate

---

## 9. Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Regex-only parsers** | No dependency on `ast`, `tree-sitter`, or language runtimes. One tool handles all 5 languages. Easily extended. |
| **Layer-balanced file cap** | Simple priority sort failed for large enterprise repos (nopCommerce: 354 ctrl+svc files exceeded 300-cap before any domain files). Quota system guarantees entity files always appear. |
| **`subprocess` for git clone** | No `gitpython` dependency. List args avoid shell injection. Git is available everywhere Python is. |
| **`partial class` in C# regex** | `public partial class X` is the default in .NET (Razor, auto-generated code). Without `partial` in the modifier group, 0 classes are detected in many .NET codebases. |
| **File-scoped C# namespace** | `namespace Foo.Bar;` (C# 10+) omits the `{}` block. Both styles must be matched by the namespace regex. |
| **Semantic microservice clustering** | AI-suggested boundaries in `modernization.microservices_boundaries` are strings like "Order Service", not tied to actual entity names. Keyword clustering of actual entity names produces more accurate data boundaries. |
| **vis.js for entity network** | Same CDN as the dependency graph section — no extra network request. Nodes colored by bounded context give instant visual intuition of service ownership. |
| **6-section dashboard** | Data Architecture section added to show entity network and boundary cards — critical for microservices migration planning. |
| **Evaluator as pipeline stage** | Quality scoring runs automatically after every analysis — developers don't need to remember to check. Score appears in console output and writes to disk. |
| **PASS/WARN/FAIL (not numeric) per check** | Binary scores hide context. WARN communicates "result exists but needs manual review" which is the most common correct state for heuristic outputs. |
| **`--depth=1` shallow clone** | 70–90% faster than full clone. Commit history is irrelevant to static analysis. |
| **`OutputManager` class** | File sizes are known only after writing. Encapsulating writes in an instance means `write_manifest()` automatically knows all file sizes without extra tracking by the caller. |
| **`try/finally` cleanup** | The temp clone dir is always deleted — even on exception. Prevents GB of accumulated clones. |
| **Self-contained HTML** | Dashboard is one file — share by email, attach to Jira, host on S3. Only CDN dependency (Chart.js, Mermaid, vis-network) for rendering. |
| **Graceful AI fallback** | `claude_analyze()` returns `None` on any failure. All callers substitute deterministic heuristics. The tool always produces complete output. |
| **UTF-8 stdout wrapper** | Windows `cp1252` encoding crashes on any non-ASCII character including evaluation emoji. Wrapping at startup fixes everything in one place. |
| **`ensure_ascii=False` in JSON** | Class names in non-English codebases contain Unicode. Without this, Japanese identifiers become `商品` in the SDD JSON. |
| **`datetime.now(timezone.utc)`** | `datetime.utcnow()` is deprecated in Python 3.12+. |
| **Google-style docstrings** | Consistent format makes IDE hover documentation readable. Required on every module, class, and function. |

---

## 10. Token Usage & Cost

### Runtime cost per analysis run

Each `python reverse_engineer_skill.py <url>` with `ANTHROPIC_API_KEY` set makes exactly **2 API calls**:

| Call | Tokens in | Tokens out | Cost |
|------|-----------|------------|------|
| `ai_executive_summary` | ~800 | ~400 | ~$0.008 |
| `ai_modernization_roadmap` | ~900 | ~600 | ~$0.012 |
| **Per run (with API key)** | ~1,700 | ~1,000 | **~$0.02** |
| **Per run (no API key)** | 0 | 0 | **$0.00** |

### Token efficiency notes

- Each analysis run costs **~$0.02** with AI enabled, or **$0.00** with heuristic-only mode
- The evaluator adds zero API calls — it's entirely deterministic

> Current pricing: <https://www.anthropic.com/pricing>
