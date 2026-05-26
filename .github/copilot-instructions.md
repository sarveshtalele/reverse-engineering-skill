# GitHub Copilot Instructions — Reverse Engineer Skill (API-Key-Free Edition)

This repository contains the **Reverse Engineer Skill** — a pure Python static analysis engine
that clones any public GitHub repository and produces five professional output files automatically.

**No API keys, no LLM accounts, no external services required to run the analysis.**

---

## What This Skill Does

```
Input:  GitHub URL
        ↓
  reverse_engineer_skill.py  (CLI entry point)
        ↓
  engine/pipeline.py  (8-stage orchestrator)
        ↓
  Five output files in ./outputs/{repo_name}/
    ├── {repo}_sdd.json          — 14-section System Design Document
    ├── {repo}_dashboard.html    — 6-section interactive HTML dashboard
    ├── {repo}_report.md         — 12-section Markdown technical report
    ├── {repo}_evaluation.md     — 100-point automated quality evaluation
    └── manifest.json            — Run metrics and file sizes
```

All analysis — executive summary, architecture pattern, business domain, modernisation roadmap —
is produced by **pure static code heuristics** (class/method naming, ORM entity detection,
import analysis, API route extraction). No LLM is called by the Python script.

---

## How to Run

### CLI (zero dependencies — just Python + git)

```bash
# No pip install needed — zero external dependencies
python reverse_engineer_skill.py https://github.com/owner/repo-name

# Show help
python reverse_engineer_skill.py --help

# Outputs land in: ./outputs/{repo_name}/
```

### GitHub Copilot mode (Copilot provides AI narrative on the static output)

1. In Copilot Chat, click the **paperclip/attach** icon → **Prompt…** →
   **"Reverse Engineer a GitHub Repo"**
2. Type the GitHub URL and press Enter
3. Copilot runs `python reverse_engineer_skill.py <url>` internally
4. Copilot reads the SDD JSON output and provides AI-quality executive summary,
   business logic analysis, and modernisation roadmap using its own intelligence
5. Copilot offers to write the AI content back into the report file

### Claude Code slash command

```bash
cd /path/to/reverse-eng-proj
claude
# then in chat:
/reverse-engineer https://github.com/owner/repo-name
```

---

## Project Structure

```
reverse-eng-proj/
├── reverse_engineer_skill.py      CLI entry point (no flags needed)
├── requirements.txt               Empty — zero external Python dependencies
├── SETUP.md                       Step-by-step setup guide
├── COMPONENTS.md                  Function-by-function reference
├── ARCHITECTURE.md                Deep technical reference
├── EVALUATION.md                  Guide to interpreting quality scores
│
├── engine/                        Modular Python package
│   ├── __init__.py
│   ├── loaders.py                 load_repo(), SUPPORTED_EXTENSIONS, SKIP_DIRS
│   ├── parsers.py                 5 language parsers + 3 ORM entity extractors
│   ├── analyzer.py                13 analysis functions
│   ├── ai_analysis.py             Pure static heuristics (no API calls)
│   ├── evaluator.py               100-point quality scorer + Markdown writer
│   ├── output_manager.py          OutputManager class
│   ├── pipeline.py                8-stage orchestrator
│   └── generators/
│       ├── sdd.py                 SDD JSON builder (14 sections)
│       ├── report.py              Markdown report builder (12 sections)
│       └── dashboard.py           HTML dashboard (6 sections, fully self-contained)
│
└── templates/                     Development reference (NOT read at runtime)
    ├── sdd_template.json
    ├── dashboard_template.html
    └── report_template.md
```

---

## When Copilot Should Help With This Project

### If the user asks to analyze a GitHub repo:

**Copilot-native path (recommended):**
1. Attach the **"Reverse Engineer a GitHub Repo"** prompt (paperclip → Prompt…)
2. Type the GitHub URL and press Enter
3. Copilot runs `python reverse_engineer_skill.py <url>`
4. Copilot reads the SDD JSON and **YOU provide the AI analysis** — executive summary,
   business domain, workflows, modernisation roadmap — using Copilot's own AI
5. Copilot offers to write the AI content into the report file

**CLI path (static analysis only, instant results):**
1. Run: `python reverse_engineer_skill.py <github-url>`
2. Static heuristics generate all five output files automatically
3. Open the `.html` dashboard or `.md` report in your editor

**Key rule:** No API keys are ever needed. The Python script is self-contained.
When in Copilot Chat agent mode, YOU are the AI narrative layer on top of the
structured static analysis data.

### If the user asks to improve the skill or fix a bug:

| Task | Where to look |
|------|--------------|
| Add a new language parser | `engine/parsers.py` → add to `detect_language()`, write `parse_X()`, add to `parse_file()` |
| Improve entity detection | `engine/parsers.py` → edit `_extract_db_entities_X()` functions |
| Improve domain detection | `engine/ai_analysis.py` → edit `_detect_domain_label()` keyword map |
| Add a new analysis metric | `engine/analyzer.py` → add a new function, call from `engine/pipeline.py` |
| Change dashboard sections | `engine/generators/dashboard.py` → add nav item, section HTML, JS builder function |
| Change report sections | `engine/generators/report.py` → add Markdown section in `generate_md_report()` |
| Change SDD schema | `engine/generators/sdd.py` → add key in `generate_sdd()` |
| Add evaluation checks | `engine/evaluator.py` → add `_check()` calls to existing `_eval_*` functions |

---

## `ai_analysis.py` — Static Heuristic Engine

The three functions in `ai_analysis.py` use **zero API calls**. They produce results
by examining:

- **Class/method naming conventions** → architecture pattern (MVC, N-Tier, CQRS, etc.)
- **ORM entity names and relationships** → business domain, entity glossary
- **API endpoint paths and HTTP methods** → core workflows
- **Import/dependency strings** → integrations (Redis, Stripe, OAuth, etc.)
- **File counts and complexity metrics** → modernisation priority and effort estimate
- **Directory structure** → microservice boundary suggestions

All three functions always return a complete dict — no `None` values, no exceptions.

---

## Parser Return Contract

Every `parse_X(file_path, code)` function must return:

```python
{
    "file":         str,          # Absolute path to the source file
    "language":     str,          # "python" | "java" | "dotnet" | "typescript" | "javascript"
    "classes":      list[str],    # Class and interface names defined in this file
    "methods":      list[str],    # Method/function names (language keywords excluded)
    "imports":      list[str],    # Raw import strings as written in source
    "dependencies": list[str],    # Deduplicated top-level dependency namespaces
    "routes":       list[dict],   # [{path, methods, class, method}, ...]
    "db_entities":  list[dict],   # [{name, table, fields, relationships, file}, ...]
}
```

---

## SDD JSON — 13 Top-Level Keys

```
sdd_metadata, project, executive_summary, codebase_metrics, architecture,
module_inventory, api_catalog, dependency_analysis, dead_code_analysis,
data_architecture, business_logic, modernization_roadmap, risk_assessment, tech_debt_inventory
```

## Dashboard DATA Object Keys

```javascript
const DATA = {
  repoName, repoUrl, generatedAt,
  metrics: { files, classes, methods, endpoints, deadFiles, languages },
  endpoints:      [{path, methods, handler, file}],
  deadFiles:      ["filename.cs"],
  deadClasses:    [{class, file}],
  techStack:      ["ASP.NET Core", "Docker"],
  summary:        { purpose, architecturePattern, priority, concerns },
  modernization:  { phases, targetStack, boundaries, effort, risks },
  topModules:     [{module, connections}],
  platform:       ".NET / Windows Server",
  archLayers:     ["API / Presentation Layer"],
  dbSchema:       { entityCount, relationshipCount, hasSchema, entities },
  dataBoundaries: [{name, entities, color, entity_count}],
  businessLogic:  {business_domain, what_it_does, core_workflows, user_roles,
                   key_business_rules, data_entities_explained, integrations, fallback_used}
}
```

---

## Coding Conventions

- **Zero external dependencies** — no packages in `requirements.txt`; only Python stdlib + git
- **Regex-only parsers** — no `ast`, `tree-sitter`, or language-specific library dependencies
- **Pure heuristics** — all analysis functions return complete results without API calls
- **All output goes to `./outputs/{repo_name}/`** via `OutputManager`
- **HTML is self-contained** — no server needed; CDN only for Chart.js, Mermaid, vis-network
- **Python 3.8+ syntax** throughout
- **Google-style docstrings** on every module, class, and function
- **UTF-8 everywhere** — `encoding="utf-8"` on all file reads/writes

---

## Common Copilot Chat Prompts

```
"Add a parser for Go (.go) files — detect struct types, funcs, and Gin routes"
"Improve the dotnet entity extractor to handle Fluent API OnModelCreating()"
"Add a new dashboard section showing the evaluation score summary"
"Extend the evaluator with a Section 7 checking for OpenAPI spec validity"
"Make the dependency graph highlight circular dependencies in red"
"Add Go/Rust/Ruby/PHP to the supported language parsers"
"Export the entity relationship data as a PlantUML ERD diagram"
"Improve domain detection to also scan file path segments"
```
