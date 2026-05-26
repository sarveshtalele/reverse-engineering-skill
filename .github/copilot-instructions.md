# GitHub Copilot Instructions — Reverse Engineer Skill v3.0

This repository contains the **Reverse Engineer Skill** — a Python static analysis engine that clones any public GitHub repository and produces five professional output files automatically.

---

## What This Skill Does

```
Input:  GitHub URL
        ↓
  reverse_engineer_skill.py  (CLI entry point)
        ↓
  engine/pipeline.py  (9-stage orchestrator)
        ↓
  Five output files in ./outputs/{repo_name}/
    ├── {repo}_sdd.json          — 14-section System Design Document
    ├── {repo}_dashboard.html    — 6-section Apple-theme HTML dashboard
    ├── {repo}_report.md         — 12-section Markdown technical report
    ├── {repo}_evaluation.md     — 100-point automated quality evaluation
    └── manifest.json            — Run metrics and file sizes
```

---

## How to Run

### GitHub Copilot mode (no Anthropic key required)

Copilot IS the AI engine. The Python script does all static analysis; Copilot
reads the SDD JSON output and provides AI-quality narrative.

1. In Copilot Chat, click the **paperclip/attach** icon → **Prompt…** →
   **"Reverse Engineer a GitHub Repo"**
2. Type the GitHub URL and press Enter
3. Copilot runs `python reverse_engineer_skill.py <url> --no-ai` internally
4. Copilot reads the output and generates executive summary, business logic analysis,
   and modernization roadmap using its own AI — no Anthropic key needed
5. Copilot offers to write AI content back into the report file

### CLI with Claude AI (optional Anthropic key)

```bash
# Install the one dependency
pip install -r requirements.txt

# Run with Claude AI (optional — requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY=sk-ant-...       # macOS/Linux
$env:ANTHROPIC_API_KEY="sk-ant-..."      # PowerShell
python reverse_engineer_skill.py https://github.com/owner/repo-name

# Run without AI (heuristic mode — no API key needed)
python reverse_engineer_skill.py https://github.com/owner/repo-name --no-ai

# Show help
python reverse_engineer_skill.py --help

# Outputs land in: ./outputs/{repo_name}/
```

### Claude Code slash command

```bash
cd /path/to/reverse-eng-proj
claude
# then in chat:
/reverse-engineer https://github.com/owner/repo-name
```

---

## Project Structure (v3.0)

```
reverse-eng-proj/
├── reverse_engineer_skill.py      CLI entry point — supports --no-ai flag
├── requirements.txt               anthropic>=0.40.0 only
├── SETUP.md                       Step-by-step setup guide (CLI, Claude Code, Copilot)
├── COMPONENTS.md                  Function-by-function reference for every module
├── ARCHITECTURE.md                Deep technical reference
├── EVALUATION.md                  Guide to interpreting quality evaluation outputs
│
├── engine/                        Modular Python package (v3.0.0)
│   ├── __init__.py                version = "3.0.0"
│   ├── loaders.py                 load_repo(), SUPPORTED_EXTENSIONS, SKIP_DIRS
│   ├── parsers.py                 5 language parsers + 3 ORM entity extractors
│   ├── analyzer.py                13 analysis functions
│   ├── ai_analysis.py             Claude API wrapper + heuristic fallbacks
│   ├── evaluator.py               100-point quality scorer + Markdown writer
│   ├── output_manager.py          OutputManager class
│   ├── pipeline.py                9-stage orchestrator
│   └── generators/
│       ├── sdd.py                 SDD JSON builder (14 sections)
│       ├── report.py              Markdown report builder (12 sections)
│       └── dashboard.py           Apple-theme HTML dashboard (6 sections)
│
└── templates/                     Development reference (NOT read at runtime)
    ├── sdd_template.json           SDD schema with placeholder comments
    ├── dashboard_template.html     Dashboard design reference
    └── report_template.md          Report structure reference
```

---

## When Copilot Should Help With This Project

### If the user asks to analyze a GitHub repo:

**Copilot-native path (no Anthropic key needed — recommended for Copilot users):**
1. Attach the **"Reverse Engineer a GitHub Repo"** prompt (paperclip → Prompt…)
2. Type the GitHub URL and press Enter
3. Copilot runs `python reverse_engineer_skill.py <url> --no-ai`
4. Copilot reads the SDD JSON and **you provide the AI analysis** — executive summary,
   business domain, workflows, modernization roadmap — using Copilot's own AI
5. Copilot offers to write the AI content into the report file

**CLI path (with Anthropic key):**
1. Run: `python reverse_engineer_skill.py <github-url>`
2. Claude claude-sonnet-4-6 generates AI sections automatically
3. Five output files go to `./outputs/{repo_name}/` automatically

**Key rule:** When in Copilot Chat agent mode, YOU are the AI engine.
The Python script provides structured facts; YOU interpret and narrate them.

### If the user asks to improve the skill or fix a bug:

| Task | Where to look |
|------|--------------|
| Add a new language parser | `engine/parsers.py` → add to `detect_language()`, write `parse_X()`, add to `parse_file()` |
| Improve entity detection | `engine/parsers.py` → edit `_extract_db_entities_X()` functions |
| Add a new analysis metric | `engine/analyzer.py` → add a new function, call from `engine/pipeline.py` |
| Change dashboard sections | `engine/generators/dashboard.py` → add nav item, section HTML, JS builder function |
| Change report sections | `engine/generators/report.py` → add Markdown section in `generate_md_report()` |
| Change SDD schema | `engine/generators/sdd.py` → add key in `generate_sdd()` + update `templates/sdd_template.json` |
| Add evaluation checks | `engine/evaluator.py` → add `_check()` calls to existing `_eval_*` functions |
| Change file selection | `engine/pipeline.py` → edit `SLOTS` dict or `_layer()` function |

### If the user asks about the output schemas:
- **SDD JSON**: See `templates/sdd_template.json` — 14 sections with `{{PLACEHOLDER}}` markers
- **HTML dashboard**: See `templates/dashboard_template.html` header comment for DATA object keys
- **Markdown report**: See `templates/report_template.md` — 12 sections + appendix
- **Evaluation**: See `EVALUATION.md` — PASS/WARN/FAIL criteria per check

---

## Parser Return Contract

Every `parse_X(file_path, code)` function must return this exact dict:

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

**Route dict format:**
```python
{"path": "/api/users/{id}", "methods": ["GET"], "class": "UserController", "method": "GetUser"}
```

**DB entity dict format:**
```python
{"name": "Customer", "table": "Customers", "fields": [{"name": "Email", "type": "string"}], "relationships": [{"type": "OneToMany", "target": "Order"}], "file": "Customer.cs"}
```

---

## How to Add a New Language Parser

1. Add to `detect_language()` in `engine/parsers.py`:
   ```python
   ".go": "go",
   ```
2. Add to `SUPPORTED_EXTENSIONS` in `engine/loaders.py`:
   ```python
   ".go",
   ```
3. Write the parser function (all 8 return keys required):
   ```python
   def parse_go(file_path, code):
       classes  = re.findall(r'^type\s+(\w+)\s+struct', code, re.MULTILINE)
       funcs    = re.findall(r'^func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(', code, re.MULTILINE)
       imports  = re.findall(r'"([^"]+)"', code)
       routes   = []
       for path, verb in re.findall(r'\.(GET|POST|PUT|DELETE|PATCH)\("([^"]+)"', code):
           routes.append({"path": verb, "methods": [path], "class": None, "method": "handler"})
       return {
           "file": file_path, "language": "go",
           "classes": classes, "methods": funcs,
           "imports": imports, "dependencies": list(set(imports)),
           "routes": routes, "db_entities": []
       }
   ```
4. Add dispatch case in `parse_file()`:
   ```python
   if lang == "go":
       return parse_go(path, code)
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
  mermaid:        "graph TD\n  ...",
  techStack:      ["ASP.NET Core", "Docker"],
  summary:        { purpose, architecturePattern, priority, concerns },
  modernization:  { phases, targetStack, boundaries, effort, risks },
  topModules:     [{module, connections}],
  platform:       ".NET / Windows Server",
  archLayers:     ["API / Presentation Layer"],
  dbSchema:       { entityCount, relationshipCount, hasSchema, entities },
  dataBoundaries: [{name, entities, color, entity_count}],
  businessLogic:  {business_domain, what_it_does, core_workflows, user_roles, key_business_rules, data_entities_explained, integrations, fallback_used}
}
```

---

## Coding Conventions

- **No new external dependencies** — only `anthropic` is in `requirements.txt`; git is called via `subprocess`
- **Regex-only parsers** — no `ast`, `tree-sitter`, or language-specific library dependencies
- **AI degrades gracefully** — every AI caller checks for `None` and substitutes heuristics
- **All output goes to `./outputs/{repo_name}/`** via `OutputManager`
- **HTML is self-contained** — no server needed; only CDN for Chart.js, Mermaid, vis-network (rendering only)
- **Python 3.8+ syntax** throughout
- **Google-style docstrings** on every module, class, and function
- **UTF-8 everywhere** — `encoding="utf-8"` on all file reads/writes; stdout wrapped at entry point

---

## Common Copilot Chat Prompts

```
"Add a parser for Go (.go) files — detect struct types, funcs, and Gin routes"
"Improve the dotnet entity extractor to handle Fluent API OnModelCreating()"
"Add a new dashboard section showing the evaluation score summary"
"Add a CLI flag --no-ai to skip AI analysis for faster runs"
"Extend the evaluator with a Section 7 checking for OpenAPI spec validity"
"Make the dependency graph highlight circular dependencies in red"
"Add Go/Rust/Ruby/PHP to the supported language parsers"
"Export the entity relationship data as a PlantUML ERD diagram"
```
