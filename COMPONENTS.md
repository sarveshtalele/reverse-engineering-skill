# Component & Function Reference — Reverse Engineer Skill v3.0

A plain-English explanation of every module, every function, and every output section.
Use this as your first reference when reading, extending, or debugging the codebase.

---

## How to Read This Document

Each section follows this pattern:

```
FUNCTION NAME  (file it lives in)
  What it does    — the job in one sentence
  Why it exists   — what breaks without it
  Input           — what it receives
  Output          — what it returns / side-effects
  Key logic       — the most important implementation detail
```

---

## Entry Point

### `reverse_engineer_skill.py`

**What it does:** The CLI entry point. Accepts a GitHub URL from the command line and starts the pipeline.

**Why it exists:** Gives users a single command to run (`python reverse_engineer_skill.py <url>`) without needing to know Python imports or package structure.

**Key logic:** Before doing anything else, it wraps `sys.stdout` in a UTF-8 encoder. Windows terminals use `cp1252` by default — any non-ASCII character (including the ✅/⚠️/❌ emoji in evaluation output) would crash with `UnicodeEncodeError`. This one-line fix at startup prevents all such crashes in every downstream module.

---

## `engine/loaders.py` — File Discovery

### `SUPPORTED_EXTENSIONS`

**What it does:** A set of file extensions the tool can parse.

**Why it exists:** Without an allowlist, the file walker would try to parse compiled binaries, images, and config files — wasting time and producing garbage.

**Current list:** `.py .java .cs .ts .tsx .js .jsx .vb .go .rb .php .swift .kt .cpp .h`

### `SKIP_DIRS`

**What it does:** A set of directory names the file walker never descends into.

**Why it exists:** `node_modules/` can contain 100,000+ files. `bin/` and `obj/` contain compiled output. `migrations/` contains auto-generated database migration scripts. Skipping these keeps the file count to the actual hand-written source code.

**Current list:** `node_modules`, `bin`, `obj`, `.git`, `dist`, `build`, `__pycache__`, `migrations`, `packages`, `.vs`, `vendor`, `target`, `out`, `cache`, `.cache`, `backup`, `tmp`, `temp`, `logs`, `wwwroot`

### `load_repo(repo_path, extensions=None) → list[dict]`

**What it does:** Walks the cloned repository directory tree and returns a list of all readable source files with their content.

**Why it exists:** Every downstream stage needs file content. This centralises the walk logic so parsers receive clean `{path, content}` dicts — no file I/O in parsers.

**Output:** `[{"path": "/absolute/path/file.cs", "content": "source code string"}, ...]`

**Key logic:** Reads every file with `encoding="utf-8", errors="ignore"` — files with embedded null bytes or non-UTF-8 sequences simply have those characters silently dropped rather than raising an exception.

---

## `engine/parsers.py` — Language Parsers

### `detect_language(file_name) → str | None`

**What it does:** Maps a filename to a language identifier string.

**Why it exists:** The pipeline needs to know which parser to use. A single lookup dict is simpler and faster than repeated `endswith()` chains.

**Output:** `"python"` | `"java"` | `"dotnet"` | `"typescript"` | `"javascript"` | `None`

---

### `parse_python(file_path, code) → dict`

**What it does:** Extracts all classes, methods/functions, imports, Flask/FastAPI route decorators, and SQLAlchemy/Django ORM entities from a Python source file.

**Why it exists:** Python uses `class` and `def` keywords consistently, and its ORM frameworks use class-level column declarations — all regex-friendly.

**Key logic:**
- Methods starting with `_` (private/dunder) are included — they matter for dead code detection
- Flask routes: `@app.route('/path', methods=['GET','POST'])`
- FastAPI routes: `@router.get('/path')`, `@app.post('/path')`
- SQLAlchemy entities: looks for `Column()` and `__tablename__` in the class body
- Django entities: looks for `models.Model` in class inheritance

---

### `parse_java(file_path, code) → dict`

**What it does:** Extracts classes, interfaces, methods, imports, Spring MVC route annotations, and JPA/Hibernate entity annotations from a Java source file.

**Why it exists:** Java's explicit type declarations and annotation syntax make it well-suited to regex extraction.

**Key logic:**
- Method detection filters a keyword set (`class`, `if`, `for`, `while`, `return`, etc.) to avoid false positives
- Spring routes: `@GetMapping("/path")`, `@RequestMapping(value="/path")`
- JPA entities: `@Entity`, `@Table(name="...")`, `@ManyToOne`, `@OneToMany`

---

### `parse_dotnet(file_path, code) → dict`

**What it does:** Extracts classes, interfaces, methods, `using` imports, namespace, ASP.NET Core attribute-routed endpoints, and EF Core entity definitions from a C# source file.

**Why it exists:** C# is the primary language of nopCommerce and most enterprise .NET codebases — the most important parser in the tool.

**Key logic — two-pass route extraction:**
A single regex can't reliably link `[HttpGet("/path")]` to the method that follows it, because there may be stacked attributes (`[Authorize]`, `[HttpGet]`) or multi-line signatures in between. The two-pass approach:
1. Find every HTTP attribute → record position + path
2. Scan the 600 characters *after* each attribute → find the next method name

**Key fix — `partial class`:**
`public partial class ProductController` is the default in .NET code-gen. Without `partial` in the modifier group, the regex `public class X` misses all partial classes, producing 0 detected classes in most .NET codebases.

**Key fix — file-scoped namespaces (C# 10+):**
`namespace Nop.Core.Domain.Customers;` (with a semicolon, no braces) is the default in modern C# projects. The namespace regex must match both styles.

---

### `parse_js_ts(file_path, code) → dict`

**What it does:** Extracts classes, interfaces (TypeScript), functions (named + arrow), ES module and CommonJS imports, and Express.js routes from a JavaScript or TypeScript source file.

**Why it exists:** JavaScript's loose syntax allows classes, arrow functions, and CommonJS `require()` side-by-side — all need to be covered.

**Key logic:**
- Arrow functions: `const handler = async (req, res) => {` — captured via const/let assignment patterns
- Express routes: `app.get('/path', handler)`, `router.post('/path', handler)`

---

### `_extract_db_entities_dotnet(file_path, code, classes) → list[dict]`

**What it does:** Extracts ORM entity definitions from a C# file using two detection strategies.

**Why it exists:** EF Core entities are plain C# classes — there's no single annotation that marks them. Multiple heuristics are needed.

**Strategy 1 — DbContext scan:**
If the file contains a class inheriting from `DbContext`, every `DbSet<X>` property is an entity. This is authoritative — the DbContext is the ORM's single source of truth.

**Strategy 2 — Domain model detection:**
For entity classes themselves, the parser checks for:
- Domain namespace pattern: `namespace Nop.Core.Domain.Customers` (contains "Domain")
- BaseEntity inheritance: `: BaseEntity`
- Navigation property keywords: `virtual ICollection<X>`, `virtual X`
- EF Core data annotations: `[Key]`, `[Table]`, `[Column]`, `[ForeignKey]`

**Output per entity:**
```python
{
    "name": "Customer",
    "table": "Customer",           # from [Table("...")] or class name
    "fields": [{"name": "Email", "type": "string"}, ...],
    "relationships": [{"type": "OneToMany", "target": "Order"}, ...],
    "file": "Customer.cs"
}
```

---

### `_extract_db_entities_java(file_path, code, classes) → list[dict]`

**What it does:** Extracts JPA/Hibernate entity definitions from a Java file.

**Why it exists:** Java enterprise apps universally use JPA annotations — `@Entity` is the definitive marker.

**Key logic:** `@Entity` on a class is the primary signal. `@Table(name="...")` overrides the table name. `@ManyToOne`, `@OneToMany`, `@ManyToMany` on fields become relationship entries.

---

### `_extract_db_entities_python(file_path, code, classes) → list[dict]`

**What it does:** Extracts SQLAlchemy model definitions and Django ORM model definitions from Python files.

**Why it exists:** Python ORMs use distinct but consistent patterns — `__tablename__` for SQLAlchemy, `models.Model` for Django.

**Key logic:**
- SQLAlchemy: `__tablename__ = "users"` sets the table name; `Column(String)` fields are extracted
- Django: `class User(models.Model)` is the signal; `ForeignKey(...)` and `ManyToManyField(...)` become relationships
- `relationship(...)` in SQLAlchemy becomes a relationship entry

---

### `parse_file(file_record) → dict | None`

**What it does:** The dispatcher. Calls `detect_language()` and routes to the correct `parse_X` function.

**Why it exists:** Centralises the dispatch logic so the pipeline loop is a clean `for f in files: result = parse_file(f)`.

**Output:** The parser's result dict, or `None` for unsupported extensions (counted as "skipped" in the pipeline output).

---

## `engine/analyzer.py` — Analysis Engine

### `generate_report(parsed) → dict`

**What it does:** Aggregates the parsed file list into a single metrics dictionary.

**Why it exists:** Every generator needs file/class/method counts and language distribution. This computes them once in one pass.

**Output:** `{"total_files": 292, "total_classes": 284, "total_methods": 2301, "languages": {"dotnet": 292}}`

---

### `build_dependency_map(parsed) → dict[str, set[str]]`

**What it does:** Builds a directed graph of module dependencies from import statements.

**Why it exists:** The dependency graph (Mermaid diagram, top-modules list) requires knowing which module imports which other module. This function builds the adjacency structure.

**Output:** `{"CustomerController": {"System.Linq", "Nop.Core.Domain"}, ...}`

**Key logic:** The key is the filename stem (without extension). The values are the deduplicated `dependencies` list from each parsed file (already cleaned by each parser to remove standard library roots).

---

### `generate_mermaid(parsed, max_links=80) → str`

**What it does:** Converts the dependency map into a Mermaid `graph TD` diagram string.

**Why it exists:** Mermaid is the universal diagramming format — it renders natively on GitHub, GitLab, Notion, Confluence, and in VS Code. The diagram gives immediate visual intuition of the codebase's coupling structure.

**Key logic:**
- Node names are sanitised to `[a-zA-Z0-9_]` (Mermaid requirement)
- A set of `IGNORE` roots prevents clutter: `os`, `sys`, `java`, `Microsoft`, `react`, etc.
- Edges are deduplicated with a `seen` set
- Cap at 80 edges — beyond this the diagram is unreadable

---

### `extract_api_endpoints(parsed) → list[dict]`

**What it does:** Flattens all `routes` lists from all parsed files into one flat endpoint list, adding the source file path to each.

**Why it exists:** Generators need a single list of all endpoints. Individual parsers return per-file routes — this combines them.

**Output:** `[{"path": "/api/customers", "methods": ["GET"], "class": "CustomerController", "method": "GetAll", "file": "CustomerController.cs"}, ...]`

---

### `generate_openapi_spec(endpoints, repo_name) → dict`

**What it does:** Converts the flat endpoint list into a valid OpenAPI 3.0 JSON specification.

**Why it exists:** OpenAPI is the industry-standard API documentation format. A machine-readable spec makes the SDD immediately consumable by API tools (Postman, Swagger UI, API gateways).

**Key logic:**
- Path parameters are normalised: `<id>` → `{id}`, `:id` → `{id}`
- If no endpoints were found, a placeholder `/health` endpoint is added so the spec is always valid JSON
- Multiple HTTP methods on the same path are merged under one path object

---

### `detect_dead_code(parsed) → dict`

**What it does:** Identifies files and classes that are never referenced by any other file in the analyzed set.

**Why it exists:** Dead code is a major source of maintenance burden. Automatically flagging candidates saves hours of manual searching.

**Key logic (two-pass):**
1. Build `all_refs` — every import string, dependency, and class name found across ALL files
2. For each file: if its stem doesn't appear in `all_refs` AND none of its classes appear in `all_refs` → mark as dead
3. Exclude known entry-point names: `main`, `app`, `index`, `startup`, `program`, `__init__`

**Important caveat:** This is heuristic-only. It cannot detect runtime-loaded modules, DI container registrations, or reflection-based usage. Always validate before deleting anything flagged here.

---

### `detect_tech_stack(parsed, repo_path) → list[str]`

**What it does:** Identifies the frameworks, tools, and infrastructure technologies used in the repository.

**Why it exists:** The tech stack is shown prominently in the dashboard, SDD, and report — it's the first thing stakeholders want to know.

**Key logic (two-pass):**
1. **Dependency scan** — checks all `dependencies` strings against a signature dict: `microsoft.aspnetcore` → "ASP.NET Core", `org.springframework` → "Spring Boot", `django` → "Django", etc.
2. **Config file scan** — checks for `Dockerfile` → "Docker", `package.json` → "Node.js", `pom.xml` → "Maven", `*.csproj` → ".NET Project File", etc.

---

### `detect_platform(parsed) → str`

**What it does:** Returns a human-readable runtime platform string based on the primary language.

**Why it exists:** Stakeholders need to know the infrastructure context (cloud, OS, runtime) at a glance.

**Output examples:** `.NET / Windows Server`, `JVM / Linux`, `Python / Linux`, `Node.js`

---

### `detect_architecture_layers(parsed) → list[str]`

**What it does:** Detects which architectural layers are present in the codebase by scanning file paths for keyword patterns.

**Why it exists:** Enterprise applications follow layered architecture (API → Service → Repository → Domain). Detecting these layers confirms the architecture pattern and helps the AI generate accurate modernization advice.

**Patterns:**
| Keywords in path | Layer |
|-----------------|-------|
| `controller`, `api`, `endpoint`, `route`, `handler` | API / Presentation Layer |
| `service`, `business`, `domain`, `core`, `logic` | Business Logic Layer |
| `repository`, `data`, `dal`, `model`, `entity`, `db` | Data Access Layer |
| `helper`, `util`, `common`, `shared`, `extension` | Utility / Shared Layer |
| `config`, `setting`, `startup`, `program` | Configuration / Bootstrap Layer |
| `view`, `template`, `razor` | View / Template Layer |

---

### `find_top_modules(dep_map, n=10) → list[tuple]`

**What it does:** Returns the N modules with the most outgoing dependencies (highest fan-out).

**Why it exists:** High fan-out modules are coupling hotspots. Identifying them helps architects prioritise what to decompose first during modernization.

**Output:** `[("OrderService", 14), ("CustomerService", 11), ...]`

---

### `extract_external_deps(parsed) → list[str]`

**What it does:** Collects all unique dependency strings across all parsed files and returns them sorted.

**Why it exists:** The SDD and report both need an external dependencies list for the dependency hygiene risk assessment. Aggregating here avoids duplication in generators.

---

### `detect_database_schema(parsed) → dict`

**What it does:** Aggregates all `db_entities` lists from every parsed file into a unified schema model.

**Why it exists:** Each parser extracts entities file-by-file. This function merges them, deduplicates by entity name, counts relationships, and produces the schema structure used by all three generators.

**Key logic:**
- If the same entity name appears in multiple files, the later parse result wins (more complete data)
- `entity_count` and `relationship_count` are computed after deduplication

**Output:**
```python
{
    "entity_count": 51,
    "relationship_count": 0,
    "has_schema": True,
    "entities": [{"name": "Customer", "table": "Customer", "fields": [...], "relationships": [...], "file": "Customer.cs"}, ...]
}
```

---

### `suggest_microservice_data_boundaries(db_schema, modernization=None) → list[dict]`

**What it does:** Groups detected entities into bounded contexts using semantic keyword matching, producing a candidate microservice decomposition.

**Why it exists:** The core question of microservices migration is "which entities belong to which service?" Keyword clustering gives a first-pass answer instantly from the entity names alone — no AI call needed.

**7 domain clusters:**
| Bounded Context | Keyword signals |
|----------------|----------------|
| Customer / Identity | customer, user, account, identity, member, profile, auth, role |
| Product / Catalog | product, catalog, category, item, sku, inventory, price, stock |
| Order / Commerce | order, cart, checkout, payment, invoice, transaction, shipment |
| Content / Media | content, blog, post, article, review, comment, media, image |
| Notification / Comms | notification, email, sms, campaign, newsletter, message, alert |
| Configuration | setting, configuration, locale, currency, country, language, theme |
| Search / Analytics | search, index, analytics, report, stat, log, audit, metric |

**Fallback:** When no entities are detected (repo uses no recognised ORM pattern), falls back to the `microservices_boundaries` list from the AI modernization roadmap — entities list will be empty, context noted as "From AI roadmap".

**Output:**
```python
[{"name": "Product / Catalog", "entities": ["Product", "Category", ...], "color": "#4cc9f0", "entity_count": 12}, ...]
```

---

## `engine/ai_analysis.py` — AI Layer

### `claude_analyze(prompt, max_tokens=2000) → str | None`

**What it does:** Sends a prompt to Claude claude-sonnet-4-6 and returns the text response.

**Why it exists:** All AI calls go through one function — makes it easy to swap models, add retry logic, or mock in tests.

**Key design:** Returns `None` on ANY failure (missing API key, network timeout, JSON parse error, rate limit). Never raises. The caller is always responsible for checking `None` and using a fallback.

---

### `ai_executive_summary(parsed, report, repo_name) → dict`

**What it does:** Asks Claude to produce a structured executive summary of the codebase.

**Why it exists:** Static analysis can count classes and detect frameworks, but it can't synthesise a one-paragraph description of what the system actually does. Claude fills this gap.

**Prompt strategy:** Sends the top 20 files' class/method/route lists. Asks for JSON output with specific keys to ensure parseable structure.

**Fallback (no API key):** Returns a heuristic dict with a template-based purpose string, "Monolithic" architecture pattern, and `HIGH` priority for codebases with >500 methods.

---

### `ai_modernization_roadmap(parsed, report, repo_name, tech_stack) → dict`

**What it does:** Asks Claude to produce a phased modernization plan including target stack, migration phases with risk levels, proposed microservice boundaries, and estimated effort.

**Why it exists:** Modernization planning requires understanding both the current state (what the code does) and the target state (what the architecture should become) — exactly what a language model excels at.

**Fallback (no API key):** Returns a hardcoded 4-phase plan (Assess → Foundation → Migrate → Validate) with a language-appropriate default target stack (e.g., C# → .NET 8, Azure, Kubernetes, Docker).

---

## `engine/output_manager.py` — File Writer

### `class OutputManager`

**What it does:** Manages creating the output directory and writing all files for one pipeline run. Tracks every written file's size so the manifest is accurate.

**Why it exists:** Without a central write tracker, the manifest would need to re-stat every file after writing — or the caller would need to manually track sizes. `OutputManager` makes writes self-tracking.

### `OutputManager.__init__(repo_name, base_dir="outputs")`
Creates `outputs/{repo_name}/` if it doesn't exist. Initialises the `_written` tracking list.

### `OutputManager.write_json(filename, data, indent=2) → Path`
Serialises a dict as JSON with `ensure_ascii=False` (preserves Unicode class names) and `default=list` (converts Python `set` objects to JSON arrays). Appends to `_written`.

### `OutputManager.write_text(filename, content) → Path`
Writes a string as UTF-8 text. Used for HTML and Markdown outputs. Appends to `_written`.

### `OutputManager.write_manifest(**metrics) → Path`
Writes a `manifest.json` containing the generation timestamp, repo name, output directory, every written file's name+size, and any keyword metrics passed by the caller (files_analyzed, classes, methods, etc.).

### `OutputManager.summary_lines() → list[str]`
Returns a list of formatted strings, one per written file: `"     * outputs/repo/file.json  (142 KB)"`. Used for the console summary after each run.

---

## `engine/evaluator.py` — Quality Scorer

### `evaluate_pipeline_output(...) → dict`

**What it does:** Scores the pipeline's output across 6 sections on a 100-point scale, assigning PASS/WARN/FAIL to each individual check.

**Why it exists:** Static analysis is inherently heuristic. Without automated quality feedback, users have no way to know if the results are trustworthy or need manual follow-up. The evaluator makes quality visible immediately.

**Sections and what they check:**
| Section | What it checks |
|---------|---------------|
| Parsing Quality (20 pts) | Were files found? What was the parse success rate? Were classes and methods extracted? |
| API Endpoints (20 pts) | Were endpoints found? Are HTTP methods varied? Do paths look valid? |
| Dead Code Analysis (15 pts) | Is the dead-file ratio plausible (not 99%)? Did the analysis complete? |
| Entity / Data Architecture (15 pts) | Were ORM entities detected? Were boundaries identified? Relationships? |
| Dependency Graph (15 pts) | Is the dependency map populated? Was the Mermaid diagram produced? Tech stack? |
| AI Analysis Quality (15 pts) | Is there a substantive executive summary? Architecture pattern? Roadmap phases? |

### `write_evaluation_md(evaluation) → str`

**What it does:** Renders the evaluation result dict as a complete Markdown document.

**Why it exists:** The dict is useful for programmatic processing; the Markdown is what humans read. The rendered document includes an ASCII progress bar, section detail tables, recommendations, and an interpretation guide.

---

## `engine/pipeline.py` — The Orchestrator

### `clone_repo(url, target_dir) → None`

**What it does:** Runs `git clone --depth=1 <url> <target_dir>` as a subprocess.

**Why it exists:** Shallow cloning avoids downloading GB of git history — only the current working tree is needed for static analysis. Using `subprocess.run()` with a list (not a shell string) avoids injection vulnerabilities and Windows path issues.

### `repo_name_from_url(url) → str`

**What it does:** Extracts a filesystem-safe repo name from a GitHub URL.

**Why it exists:** The output directory is named after the repo. Characters like `/`, `:`, and spaces must be sanitised.

**Logic:** Strip `.git` suffix → take the last URL segment → replace `[^\w\-]` with `_`

### `run_pipeline(repo_url) → None`

**What it does:** Executes all 9 pipeline stages in order for one repository URL.

**Why it exists:** This is the single public entry point — `from engine import run_pipeline` is all external callers need.

**9 stages:**
1. Clone → `clone_repo()`
2. Load → `load_repo()`
3. Parse → layer-balanced file cap + `parse_file()` per file
4. Metrics → `generate_report()`, `build_dependency_map()`, `generate_mermaid()`, `find_top_modules()`
5. APIs + Dead Code → `extract_api_endpoints()`, `detect_dead_code()`, `detect_tech_stack()`, `detect_database_schema()`
6. AI → `ai_executive_summary()`, `ai_modernization_roadmap()`, `detect_platform()`, `detect_architecture_layers()`, `suggest_microservice_data_boundaries()`
7. Generate & Write → `generate_sdd()`, `generate_html_dashboard()`, `generate_md_report()`, `write_manifest()`
8. Evaluate → `evaluate_pipeline_output()`, `write_evaluation_md()`
9. Cleanup → `shutil.rmtree(tmp_dir)` — always runs even on exception

**Layer-balanced file cap:**
For repos with >300 source files, files are selected by layer quota:
- Layer 0 (controllers): ≤75 files
- Layer 1 (services): ≤75 files
- Layer 2 (repos/DAL): ≤40 files
- Layer 3 (domain/entity): ≤60 files ← crucial for entity detection
- Layer 4 (models/DTOs): ≤30 files
- Layer 5 (everything else): ≤20 files

---

## `engine/generators/sdd.py` — SDD JSON Builder

### `generate_sdd(...) → dict`

**What it does:** Assembles all analysis results into a single JSON-serialisable dict following the SDD Framework v1 schema.

**Why it exists:** The SDD JSON is the machine-readable output — other tools consume it, CI pipelines validate it, and it serves as the single source of truth for all other generators.

**14 sections:** sdd_metadata, project, executive_summary, codebase_metrics, architecture, module_inventory, api_catalog, dependency_analysis, dead_code_analysis, data_architecture, business_logic, modernization_roadmap, risk_assessment, tech_debt_inventory

**Key design:** `components` (unique classes across all files) is capped at 60 to keep the JSON manageable. `methods` per module is capped at 30. `dependency_map_sample` shows 25 modules × 10 deps each.

---

## `engine/generators/dashboard.py` — HTML Dashboard Builder

### `generate_html_dashboard(...) → str`

**What it does:** Builds a complete, self-contained HTML document as a Python f-string. All analysis data is embedded as a JavaScript `const DATA = {...}` object inside the HTML.

**Why it exists:** The dashboard is the stakeholder-facing output — it must open in any browser without a server, without installing anything, and without an internet connection (except CDN for rendering Chart.js, Mermaid, vis.js).

**Architecture:** One massive f-string containing HTML + CSS + JavaScript. The Python variables are interpolated once at generation time. After that, the file is pure static HTML with embedded data.

**Six sidebar sections:**

1. **Overview** — Count-up animated metric cards (files, classes, methods, endpoints). Chart.js horizontal bar chart showing language distribution. Tech stack badges. Most-connected-modules ranked bar chart.

2. **Architecture** — Mermaid graph `TD` diagram, initialised lazily (only when the section is first opened to avoid page-load delay). Architectural layer list.

3. **API Endpoints** — Live search input with real-time filtering. HTTP method colour-coded badges (GET=blue, POST=green, PUT=orange, DELETE=red, PATCH=purple). Full scrollable endpoint table.

4. **Dead Code** — SVG percentage ring (SVG circle with `stroke-dasharray` computed from the dead-file %). Scrollable lists of unreferenced files and classes.

5. **Modernization** — Vertical timeline for migration phases (each phase is a card connected by a vertical line — communicates sequence). Risk level badge per phase. Microservice boundary grid. Target stack badges.

6. **Data Architecture** — vis.js Network graph of entity nodes (colored by bounded context). Entity metric cards. Boundary cards with entity chips. Full entity table.

**JavaScript f-string safety rules (critical for contributors):**
- All Python f-string `{` must be doubled: `{{` → literal `{` in output
- Template literal variables: `${{varName}}` → `${varName}` in output
- No `\n` inside single-line JS comments — will produce `SyntaxError` in generated HTML
- All emoji are safe in JS string literals

---

## `engine/generators/report.py` — Markdown Report Builder

### `generate_md_report(...) → str`

**What it does:** Builds a complete GitHub Flavored Markdown document from all analysis results.

**Why it exists:** The Markdown report is the human-readable output for engineers and architects. It pastes directly into Confluence, GitHub Wiki, Notion, or Azure DevOps Wiki.

**12 sections + appendix:**

| Section | What it contains |
|---------|-----------------|
| 1. Executive Summary | AI-generated purpose, attribute table (arch, priority, platform, tech stack, totals) |
| 2. **Business Logic & Functional Overview** | Business domain · plain-English description · core workflows · user roles · business rules · entity glossary · integrations |
| 3. Codebase Metrics | Language distribution table, key count table |
| 4. Architecture Overview | Mermaid dependency graph (fenced code block), architectural layer list |
| 5. Module Inventory | `#### filename` entries with classes and methods (first 40 files) |
| 6. API Catalog | Method/path/handler/file table (first 50 endpoints) + OpenAPI JSON block |
| 7. Dependency Analysis | Top-10 modules table, external dependencies code block |
| 8. Dead Code Analysis | Warning note, unreferenced files list, unreferenced classes list |
| 9. Tech Debt Inventory | AI concerns list, tech debt severity classification table |
| 10. Modernization Roadmap | Target stack, phased plan with tasks, microservice list, risks, effort |
| 11. Data Architecture | Schema summary, entity table, boundary breakdown, 5-step migration guidance |
| 12. Risk Assessment | Four-row risk matrix |
| Appendix | How generated, 5-output-files table, limitations, extending guide |

---

## Output Sections Reference

### SDD JSON — 14 Top-Level Keys

| Key | Contents | Consumer |
|-----|----------|---------|
| `sdd_metadata` | Version, timestamp, generator, model | Provenance tracking |
| `project` | Name, URL, primary language, tech stack, platform, layers | Dashboard header, report header |
| `executive_summary` | Purpose, arch pattern, debt concerns, priority, reasoning | Report Section 1, Dashboard Overview |
| `codebase_metrics` | File/class/method/endpoint counts, language distribution, top modules | Report Section 2, Dashboard Overview |
| `architecture` | Style, layers, components list (≤60), Mermaid diagram | Report Section 3, Dashboard Architecture |
| `module_inventory` | Per-file: classes, methods (≤30), routes, dependencies | Report Section 4 |
| `api_catalog` | OpenAPI 3.0 spec, flat endpoint list | Report Section 5, Dashboard API Endpoints |
| `dependency_analysis` | External deps, dep map sample, top-10 modules | Report Section 6 |
| `dead_code_analysis` | Dead files (names + paths), dead classes (≤30) | Report Section 7, Dashboard Dead Code |
| `data_architecture` | Entities, relationships, microservice boundaries, migration notes | Report Section 11, Dashboard Data Architecture |
| `business_logic` | Domain, what it does, workflows, user roles, business rules, entity glossary, integrations | Report Section 2, Dashboard Overview |
| `modernization_roadmap` | Phases, target stack, microservices, effort, risk factors | Report Section 10, Dashboard Modernization |
| `risk_assessment` | 4 risk records with severity, description, recommendation | Report Section 12 |
| `tech_debt_inventory` | 5 debt categories with severity and description | Report Section 9 |

### Dashboard DATA Object Keys

```javascript
const DATA = {
  repoName:        "nopCommerce",          // String — shown in sidebar header
  repoUrl:         "https://github.com/...",
  generatedAt:     "2026-05-26T10:00:00Z",
  metrics: {
    files:     292,    // Parsed file count
    classes:   284,    // Total classes detected
    methods:   2301,   // Total methods detected
    endpoints: 284,    // API endpoints extracted
    deadFiles: 241,    // Unreferenced files
    languages: {"dotnet": 292}   // Language distribution
  },
  endpoints:      [...],  // [{path, methods, handler, file}, ...]
  deadFiles:      [...],  // ["filename.cs", ...]
  deadClasses:    [...],  // [{class, file}, ...]
  mermaid:        "graph TD\n  ...",  // Mermaid diagram string
  techStack:      ["ASP.NET Core", "Docker", ...],
  summary: {
    purpose:             "...",
    architecturePattern: "Monolithic",
    priority:            "HIGH",
    concerns:            ["...", ...]
  },
  modernization: {
    phases:      [{phase, title, duration, tasks, risk}, ...],
    targetStack: ["ASP.NET Core 8", "Azure", ...],
    boundaries:  ["Order Service", ...],
    effort:      "12-18 months",
    risks:       ["...", ...]
  },
  topModules:     [{module, connections}, ...],
  platform:       ".NET / Windows Server",
  archLayers:     ["API / Presentation Layer", ...],
  dbSchema: {
    entityCount:       51,
    relationshipCount: 0,
    hasSchema:         true,
    entities: [{name, table, fields, relationships, file}, ...]
  },
  dataBoundaries: [{name, entities, color, entity_count}, ...],
  businessLogic: {
    business_domain:         "E-Commerce / Online Retail",
    what_it_does:            "2-3 paragraph plain-English description...",
    core_workflows:          [{name, description, steps, endpoints}, ...],
    user_roles:              ["Customer", "Administrator", ...],
    key_business_rules:      ["Rule 1", ...],
    data_entities_explained: [{entity, business_meaning, key_operations}, ...],
    integrations:            ["Payment Gateway", "Email / SMTP", ...],
    fallback_used:           false    // true when no AI key set
  }
};
```

---

## Evaluation Sections

The evaluator (`engine/evaluator.py`) scores six sections. Here's what each check actually tests:

### Section 1 — Parsing Quality (20 pts)
| Check | Points | Pass condition |
|-------|--------|---------------|
| Files Parsed | 5 | ≥10 files parsed |
| Parse Success Rate | 5 | ≥90% of attempted files parsed |
| Classes Extracted | 5 | ≥5 classes detected |
| Methods Extracted | 5 | ≥10 methods detected |

### Section 2 — API Endpoint Detection (20 pts)
| Check | Points | Pass condition |
|-------|--------|---------------|
| Endpoints Detected | 8 | ≥10 endpoints |
| HTTP Method Variety | 6 | ≥3 distinct HTTP methods |
| Path Format Validity | 6 | ≥80% of paths start with `/` or contain `{` |

### Section 3 — Dead Code Analysis (15 pts)
| Check | Points | Pass condition |
|-------|--------|---------------|
| Dead File Ratio | 5 | ≤50% of files flagged (>80% = FAIL) |
| Analysis Completed | 5 | Dead code dict has expected structure |
| Class-Level Analysis | 5 | ≥1 dead class detected |

### Section 4 — Entity / Data Architecture (15 pts)
| Check | Points | Pass condition |
|-------|--------|---------------|
| Entities Detected | 7 | ≥5 entities |
| Microservice Boundaries | 5 | ≥3 boundaries |
| Relationships Detected | 3 | ≥1 relationship |

### Section 5 — Dependency Graph (15 pts)
| Check | Points | Pass condition |
|-------|--------|---------------|
| Dependency Map Built | 5 | ≥5 modules in dep map |
| Mermaid Diagram | 5 | Diagram has >20 chars |
| Tech Stack Detection | 5 | ≥3 tech items |

### Section 6 — AI Analysis Quality (15 pts)
| Check | Points | Pass condition |
|-------|--------|---------------|
| Executive Summary | 5 | Non-fallback text, >50 chars |
| Architecture Pattern | 5 | Known pattern name present |
| Modernization Phases | 5 | ≥3 roadmap phases |

---

## Extending the Project

### Adding a new language parser

1. `engine/loaders.py` — add extension to `SUPPORTED_EXTENSIONS`
2. `engine/parsers.py` — add to `detect_language()` dict
3. `engine/parsers.py` — write `parse_X(file_path, code) → dict`  
   Must return all 8 keys: `file, language, classes, methods, imports, dependencies, routes, db_entities`
4. `engine/parsers.py` — optionally write `_extract_db_entities_X(file_path, code, classes) → list`
5. `engine/parsers.py` — add dispatch case to `parse_file()`
6. `engine/analyzer.py` — if the language uses a new ORM, add detection to `detect_tech_stack()`

### Adding a new dashboard section

1. `engine/generators/dashboard.py` — add nav item HTML (sidebar `<li>`)
2. Add section HTML (`<section id="section-NEWNAME">`)
3. Add CSS classes
4. Add JS: `buildNewSection()` function called from boot sequence
5. Update `switchSection()` to handle the new section name
6. `engine/generators/report.py` — add corresponding Markdown section
7. `engine/generators/sdd.py` — add corresponding JSON section

### Adding a new evaluation check

1. `engine/evaluator.py` — in the relevant `_eval_*` function, add:
   ```python
   checks.append(_check("Check Name", "PASS"|"WARN"|"FAIL", points_awarded, points_possible, "Message"))
   score += points_awarded
   ```
2. Update the section's `max_score` if adding new point-bearing checks
3. Add a recommendation in `recs` if the check can FAIL

---

_Reverse Engineer Skill v3.0 · Components & Function Reference_
