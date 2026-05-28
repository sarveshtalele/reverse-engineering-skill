# Reverse Engineer Skill v3.0

> One command. Any public GitHub repository. Seven professional output files.

Give it a GitHub URL and it clones the repo, runs a 9-stage static analysis pipeline, and writes everything to `outputs/{repo}/` — without executing a single line of the analysed code.

---

## Output Files

| File | Audience | Format |
|------|----------|--------|
| `{repo}_sdd.json` | Engineering tools, CI | 14-section System Design Document (JSON) |
| `{repo}_dashboard.html` | Stakeholders, PMs, leadership | Self-contained Apple-theme HTML (6 sections) |
| `{repo}_report.md` | Architects, Confluence, Notion | GitHub-compatible Markdown (12 sections) |
| `{repo}_block_diagram.svg` | All audiences | Architecture layer diagram (SVG, embeddable) |
| `{repo}_dependency_graph.svg` | Engineers | Module dependency graph (SVG, embeddable) |
| `{repo}_evaluation.md` | QA, developers | Automated 100-point quality score |
| `manifest.json` | Automation, CI | Run metrics and file index |

**Supported languages:** Python · Java · C# / .NET · JavaScript · TypeScript (+ JSX/TSX)

**AI sections** use `claude-sonnet-4-6` when `ANTHROPIC_API_KEY` is set. Full output — including all 7 files — is produced without it (heuristic mode, $0.00).

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [Usage Mode 1 — CLI](#3-usage-mode-1--cli)
4. [Usage Mode 2 — Claude Code](#4-usage-mode-2--claude-code)
5. [Usage Mode 3 — GitHub Copilot Chat](#5-usage-mode-3--github-copilot-chat)
6. [Usage Mode 4 — Agent SDK / Python API](#6-usage-mode-4--agent-sdk--python-api)
7. [CLI Flags Reference](#7-cli-flags-reference)
8. [Output Files In Detail](#8-output-files-in-detail)
9. [Enable AI Mode](#9-enable-ai-mode)
10. [Layer-Balanced File Cap](#10-layer-balanced-file-cap)
11. [Project Structure](#11-project-structure)
12. [Engine Module Reference](#12-engine-module-reference)
13. [Evaluation Scoring](#13-evaluation-scoring)
14. [Adding a New Language](#14-adding-a-new-language)
15. [Token Cost](#15-token-cost)

---

## 1. Prerequisites

| Tool | Minimum | Check |
|------|---------|-------|
| Python | 3.8+ | `python --version` |
| Git | any | `git --version` |

Downloads: [Python](https://www.python.org/downloads/) · [Git](https://git-scm.com/downloads)

---

## 2. Installation

```bash
# Clone the project
git clone https://github.com/YOUR_USERNAME/reverse-eng-proj.git
cd reverse-eng-proj

# Install the optional AI dependency (skip if using heuristic mode only)
pip install anthropic
```

`requirements.txt` contains one package: `anthropic>=0.40.0`  
The engine itself has zero pip dependencies — only Python stdlib + git are required.

---

## 3. Usage Mode 1 — CLI

The fastest path. Works on any OS.

### Step 1 — Open a terminal in the project folder

```powershell
# Windows PowerShell
cd C:\Users\YourName\Downloads\reverse-eng-proj
```

```bash
# macOS / Linux
cd ~/Downloads/reverse-eng-proj
```

### Step 2 — (Optional) Set your API key for AI sections

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."   # PowerShell — current session
```

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # bash/zsh — current session
```

### Step 3 — Run

```bash
# Heuristic mode (no API key needed)
python reverse_engineer_skill.py https://github.com/django/django --heuristic

# AI mode (requires ANTHROPIC_API_KEY)
python reverse_engineer_skill.py https://github.com/django/django --ai

# Interactive mode (prompts you to choose)
python reverse_engineer_skill.py https://github.com/django/django
```

Or use the platform scripts which auto-detect your Python binary:

```bash
# macOS / Linux
./run.sh https://github.com/django/django --heuristic

# Windows
run.bat https://github.com/django/django --heuristic
```

### Step 4 — Open the dashboard

```powershell
start outputs\django\django_dashboard.html          # Windows
open  outputs/django/django_dashboard.html          # macOS
xdg-open outputs/django/django_dashboard.html       # Linux
```

### Expected console output (nopCommerce example)

```
============================================================
  Reverse Engineer Skill
  Repository: https://github.com/nopSolutions/nopCommerce
============================================================

[1/9] Cloning repository...
      [ok] Clone complete

[2/9] Loading source files...
      Found 3,114 source files

[3/9] Applying layer-balanced file cap...
      Capped to 292 files (ctrl=75 svc=75 repo=40 domain=60 model=30 other=12)

[4/9] Parsing code structures...
      Parsed 292 / 292 files

[5/9] Extracting APIs and detecting dead code...
      284 API endpoints | 241 dead files | 7 tech stack items
      51 data entities | 7 microservice data boundaries

[6/9] Running AI analysis...
      Architecture: Monolithic | Priority: HIGH

[7/9] Generating 7 output files...
      [ok] SDD JSON          -> outputs\nopCommerce\nopCommerce_sdd.json       (415 KB)
      [ok] HTML Dashboard    -> outputs\nopCommerce\nopCommerce_dashboard.html  (96 KB)
      [ok] MD Report         -> outputs\nopCommerce\nopCommerce_report.md       (34 KB)
      [ok] Block Diagram     -> outputs\nopCommerce\nopCommerce_block_diagram.svg (18 KB)
      [ok] Dependency Graph  -> outputs\nopCommerce\nopCommerce_dependency_graph.svg (22 KB)

[8/9] Evaluating pipeline output quality...
      [ok] Evaluation        -> outputs\nopCommerce\nopCommerce_evaluation.md    (8 KB)

[9/9] Complete!

  Analysis summary:
     Files analyzed    : 292
     Classes found     : 284
     Methods found     : 2,301
     API endpoints     : 284
     Dead code files   : 241
     Primary language  : dotnet
     Tech stack        : .NET Project File, ASP.NET Core, Docker

  Quality evaluation:
     Score             : 78/100 pts  [MEDIUM confidence]
```

---

## 4. Usage Mode 2 — Claude Code

Claude Code reads `.claude/skills/reverse-engineer/SKILL.md` and runs the engine for you. **Claude Code itself acts as the AI engine** — no Anthropic API key required.

### Step 1 — Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

### Step 2 — Open Claude Code from the project folder

```bash
cd reverse-eng-proj
claude
```

### Step 3 — Run the slash command

```
/reverse-engineer https://github.com/nopSolutions/nopCommerce
```

Claude Code will:
1. Run `python reverse_engineer_skill.py <url> --heuristic`
2. Read the generated `_sdd.json`
3. Generate executive summary, business logic analysis, and modernization roadmap in the chat
4. **Automatically write the AI analysis back into `_report.md`** (no confirmation needed)

### Global install (skill available in every project)

```bash
# macOS / Linux
mkdir -p ~/.claude/skills/reverse-engineer
cp .claude/skills/reverse-engineer/SKILL.md ~/.claude/skills/reverse-engineer/SKILL.md

# Windows PowerShell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\reverse-engineer"
Copy-Item .claude\skills\reverse-engineer\SKILL.md "$env:USERPROFILE\.claude\skills\reverse-engineer\SKILL.md"
```

After global install, `/reverse-engineer` works from any directory — you still need the `engine/` folder and `reverse_engineer_skill.py` in your working directory.

---

## 5. Usage Mode 3 — GitHub Copilot Chat

VS Code with GitHub Copilot Chat uses `.github/prompts/reverse-engineer.prompt.md`. **Copilot acts as the AI engine** — no Anthropic API key required.

### Prerequisites

- VS Code 1.90+ with GitHub Copilot + GitHub Copilot Chat extensions
- This project folder open as the VS Code workspace

### Step 1 — Open VS Code

```bash
code C:\path\to\reverse-eng-proj
```

### Step 2 — Open Copilot Chat

`Ctrl+Alt+I` (Windows) / `Cmd+Alt+I` (macOS)

### Step 3 — Attach the prompt file

1. Click the **paperclip / attach** icon in the chat input
2. Select **Prompt…**
3. Choose **"reverse-engineer"**

### Step 4 — Enter a GitHub URL and send

```
https://github.com/spring-projects/spring-petclinic
```

Copilot opens a terminal, runs `reverse_engineer_skill.py --heuristic`, reads the SDD JSON, and outputs AI analysis in the chat. It then writes the AI content directly into `_report.md`.

### If the prompt file doesn't appear in the picker

Add to `.vscode/settings.json`:

```json
{
  "chat.promptFiles": true,
  "chat.promptFilesLocations": { ".github/prompts": true }
}
```

Then reload: `Ctrl+Shift+P` → **Reload Window**.

---

## 6. Usage Mode 4 — Agent SDK / Python API

Import `ReverseEngineerAgent` directly in your Python scripts or CI pipelines.

```python
from reverse_engineer_agent import ReverseEngineerAgent

# Heuristic mode — no API key required
agent = ReverseEngineerAgent(mode="heuristic")
result = agent.run("https://github.com/spring-projects/spring-petclinic")

print(result["summary"]["architecture_pattern"])   # "Layered N-Tier MVC"
print(result["metrics"]["endpoints"])              # 23
print(result["output_files"]["dashboard"])         # outputs/spring-petclinic/...

# AI mode — calls Claude API for narrative
agent = ReverseEngineerAgent(mode="ai")
result = agent.run("https://github.com/django/django")
print(result["ai_narrative"])
```

Or as a CLI:

```bash
python reverse_engineer_agent.py https://github.com/owner/repo
python reverse_engineer_agent.py https://github.com/owner/repo --ai
```

`ReverseEngineerAgent` is provided in the `03-agent-sdk-skill` package (see `skill-packages/`).

---

## 7. CLI Flags Reference

```
python reverse_engineer_skill.py <github-url> [flags]
```

| Flag | Effect |
|------|--------|
| _(no flag)_ | Interactive mode — prompts `[1] Heuristic / [2] AI` at startup |
| `--heuristic` | Force heuristic mode — skips interactive prompt, no API key needed |
| `--no-ai` | Alias for `--heuristic` |
| `--ai` | Force AI mode — skips interactive prompt, requires `ANTHROPIC_API_KEY` + `anthropic` package |
| `--help` / `-h` | Print usage and exit |

**Auto-fallback:** If `--ai` is passed but `ANTHROPIC_API_KEY` is not set or `anthropic` is not installed, the script auto-falls back to heuristic mode with a warning.

---

## 8. Output Files In Detail

### `{repo}_sdd.json` — System Design Document

14-section JSON document:

| # | Section | Contents |
|---|---------|----------|
| 1 | `sdd_metadata` | Version, timestamp, generator |
| 2 | `project` | Name, URL, language, tech stack, platform, architecture layers |
| 3 | `executive_summary` | Purpose, architecture pattern, tech debt concerns, modernization priority |
| 4 | `codebase_metrics` | Files, classes, methods, endpoints, language breakdown |
| 5 | `architecture` | Style, layers, components |
| 6 | `module_inventory` | Per-file list: classes, methods, routes |
| 7 | `api_catalog` | OpenAPI 3.0 spec + flat endpoint list |
| 8 | `dependency_analysis` | Import map, top 10 most-connected modules |
| 9 | `dead_code_analysis` | Unreferenced files and classes |
| 10 | `data_architecture` | ORM entities, relationships, microservice boundaries |
| 11 | `business_logic` | Domain, workflows, block diagram data |
| 12 | `modernization_roadmap` | 4-phase plan with effort estimates and risk levels |
| 13 | `risk_assessment` | Risk items with severity and mitigation |
| 14 | `tech_debt_inventory` | Debt categories with priority labels |

### `{repo}_dashboard.html` — Stakeholder Dashboard

Open in any browser — no server required. Six sidebar sections:

| Section | What you see |
|---------|-------------|
| **Overview** | Metric cards (files / classes / methods / endpoints), language chart, tech stack badges |
| **Architecture** | Architecture block diagram (SVG), layer breakdown |
| **API Endpoints** | Live search + HTTP method filter, full endpoint table |
| **Dead Code** | Percentage ring, unreferenced file and class lists |
| **Modernization** | Phase timeline, microservice boundary grid, target stack |
| **Data Architecture** | Entity table, bounded context cards |

### `{repo}_report.md` — Technical Report

12-section Markdown compatible with GitHub, Confluence, and Notion. Includes embedded SVG diagrams. When run via Claude Code or GitHub Copilot, AI-enhanced narrative is written directly into this file.

### `{repo}_block_diagram.svg` — Architecture Block Diagram

Standalone responsive SVG showing the 6-layer architecture:
`CLIENT → API/Presentation → Business Logic → Data Access → Database → External Services`

Each layer is tinted a distinct color. Each node shows the component name with its class count. Embeddable in any HTML page or Markdown file.

### `{repo}_dependency_graph.svg` — Module Dependency Graph

Hierarchical column layout SVG:
- **SOURCES** (left) — modules with outgoing deps only
- **HUBS** (center) — modules with both in and out
- **SINKS** (right) — modules with incoming deps only
- **ISOLATED** (bottom) — standalone modules

### `{repo}_evaluation.md` — Quality Score

100-point automated quality score produced after every run:

```
Score: 78/100  Confidence: MEDIUM

Section 1 — Parsing Quality           18/20  ✅ PASS
Section 2 — API Endpoint Detection    18/20  ✅ PASS
Section 3 — Dead Code Analysis        12/15  ✅ PASS
Section 4 — Entity / Data Architecture 8/15  ⚠️ WARN
Section 5 — Dependency Graph          15/15  ✅ PASS
Section 6 — AI Analysis Quality        7/15  ℹ️ INFO  (no API key)
```

Confidence bands: **HIGH** ≥ 80 · **MEDIUM** ≥ 60 · **LOW** ≥ 40 · **VERY LOW** < 40

### `manifest.json` — Run Manifest

Machine-readable run record with metrics, file sizes, and timestamps. Useful for CI comparison between runs.

---

## 9. Enable AI Mode

Without an API key, heuristic fallbacks produce complete output for all 7 files.  
With a key, `claude-sonnet-4-6` enriches the executive summary, modernization roadmap, and business logic analysis with context-aware narrative.

### Set the key

```powershell
# Windows PowerShell — current session
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Windows — persist across sessions
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
```

```bash
# macOS / Linux — current session
export ANTHROPIC_API_KEY="sk-ant-..."

# Persist (add to ~/.bashrc or ~/.zshrc)
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
```

### Install the SDK

```bash
pip install anthropic
```

Get a key: <https://console.anthropic.com/>

---

## 10. Layer-Balanced File Cap

For repos with more than 300 source files the pipeline selects files by layer priority rather than truncating arbitrarily:

| Layer | Keyword signals | Max files | Why |
|-------|----------------|-----------|-----|
| 0 — Controllers | `controller`, `handler`, `router` | 75 | API surface always covered |
| 1 — Services | `service`, `manager`, `processor` | 75 | Business logic always covered |
| 2 — Repositories | `repository`, `repo`, `dao`, `dal` | 40 | Data access always covered |
| 3 — Domain/Entity | `entity`, `domain`, `model`, `.aspx.cs` | 60 | ORM entities always covered |
| 4 — Models/DTOs | `dto`, `viewmodel`, `schema` | 30 | Transfer objects included |
| 5 — Everything else | remaining files | 20 | Best-effort coverage |
| **Total cap** | | **300** | |

Adjust quotas by editing `SLOTS` in `engine/pipeline.py`.

---

## 11. Project Structure

```
reverse-eng-proj/
│
├── reverse_engineer_skill.py     CLI entry point (≈ 42 lines)
├── reverse_engineer_agent.py     Agent SDK wrapper (from skill-packages/03)
├── requirements.txt              anthropic>=0.40.0
├── run.bat                       Windows runner (auto-detects Python binary)
├── run.sh                        macOS/Linux runner (auto-detects Python binary)
│
├── engine/                       Core analysis package
│   ├── __init__.py
│   ├── pipeline.py               9-stage orchestrator
│   ├── loaders.py                File discovery (SUPPORTED_EXTENSIONS, SKIP_DIRS)
│   ├── parsers.py                5 language parsers + ORM entity extractors
│   ├── analyzer.py               18 analysis functions (metrics, graphs, APIs, dead code…)
│   ├── ai_analysis.py            Claude API wrapper + heuristic fallbacks
│   ├── output_manager.py         OutputManager — write files, track sizes
│   ├── evaluator.py              100-point quality scorer + Markdown writer
│   └── generators/
│       ├── sdd.py                SDD JSON builder (14 sections)
│       ├── report.py             Markdown report builder (12 sections)
│       └── dashboard.py          Apple-theme HTML dashboard (6 sections)
│
├── templates/                    Development reference only — NOT read at runtime
│   ├── sdd_template.json
│   ├── dashboard_template.html
│   └── report_template.md
│
├── .claude/
│   ├── skills/
│   │   └── reverse-engineer/
│   │       └── SKILL.md          /reverse-engineer slash command (current standard)
│   └── commands/
│       └── reverse-engineer.md   /reverse-engineer slash command (legacy fallback)
│
├── .github/
│   ├── copilot-instructions.md   Auto-loaded context for GitHub Copilot Chat
│   └── prompts/
│       └── reverse-engineer.prompt.md   Agent prompt (mode: agent)
│
├── .vscode/
│   └── settings.json             Copilot prompt file settings
│
├── skill-packages/               Distributable packages for your team
│   ├── README.md
│   ├── GOVERNANCE.md
│   ├── build_packages.py
│   ├── 01-claude-code-skill/
│   ├── 02-github-copilot-skill/
│   ├── 03-agent-sdk-skill/
│   └── dist/                     Built ZIPs (git-ignored)
│
└── outputs/                      Generated files (git-ignored)
    └── {repo_name}/
        ├── {repo}_sdd.json
        ├── {repo}_dashboard.html
        ├── {repo}_report.md
        ├── {repo}_block_diagram.svg
        ├── {repo}_dependency_graph.svg
        ├── {repo}_evaluation.md
        └── manifest.json
```

---

## 12. Engine Module Reference

| Module | Key exports | Responsibility |
|--------|-------------|----------------|
| `engine.pipeline` | `run_pipeline`, `clone_repo`, `repo_name_from_url` | 9-stage orchestrator |
| `engine.loaders` | `load_repo`, `SUPPORTED_EXTENSIONS`, `SKIP_DIRS` | File discovery and content loading |
| `engine.parsers` | `parse_file`, `parse_python`, `parse_java`, `parse_dotnet`, `parse_js_ts` | Regex-based language parsers + ORM extractors |
| `engine.analyzer` | `generate_report`, `build_dependency_map`, `extract_api_endpoints`, `detect_dead_code`, `detect_tech_stack`, `generate_block_diagram`, `generate_block_diagram_svg`, `generate_dep_graph_svg` | All static analysis (18 functions) |
| `engine.ai_analysis` | `ai_executive_summary`, `ai_modernization_roadmap`, `ai_business_logic_analysis`, `ai_all_sections_claude` | Claude API integration + heuristic fallbacks |
| `engine.output_manager` | `OutputManager` | Write files, track sizes, emit `manifest.json` |
| `engine.evaluator` | `evaluate_pipeline_output`, `write_evaluation_md` | 100-point quality scoring |
| `engine.generators.sdd` | `generate_sdd` | Build 14-section SDD JSON dict |
| `engine.generators.dashboard` | `generate_html_dashboard` | Build self-contained HTML dashboard |
| `engine.generators.report` | `generate_md_report` | Build 12-section Markdown report |

### Parser return contract

Every `parse_X()` returns:

```python
{
    "file":         str,          # absolute path
    "language":     str,          # "python" | "java" | "dotnet" | "typescript" | "javascript"
    "classes":      list[str],    # class / interface names
    "methods":      list[str],    # method / function names
    "imports":      list[str],    # raw import strings
    "dependencies": list[str],    # deduplicated dependency namespaces
    "routes":       list[dict],   # [{path, methods, class, method}]
    "db_entities":  list[dict],   # [{name, table, fields, relationships, file}]
}
```

---

## 13. Evaluation Scoring

The `_evaluation.md` file is generated automatically after every run.

| Section | Max | What is measured |
|---------|-----|-----------------|
| 1 — Parsing Quality | 20 pts | Classes, methods, and dependency extraction completeness |
| 2 — API Endpoint Detection | 20 pts | Endpoint coverage vs. controller/route file count |
| 3 — Dead Code Analysis | 15 pts | Unreferenced file detection rate |
| 4 — Entity / Data Architecture | 15 pts | ORM entity and relationship extraction quality |
| 5 — Dependency Graph | 15 pts | Graph density, hub detection, edge count |
| 6 — AI Analysis Quality | 15 pts | Completeness of executive summary and roadmap sections |

Score guide: **HIGH** ≥ 80 · **MEDIUM** ≥ 60 · **LOW** ≥ 40 · **VERY LOW** < 40

If Section 6 scores low (common without an API key), the other five sections are the meaningful signal.

---

## 14. Adding a New Language

1. Add the extension to `detect_language()` in `engine/parsers.py`
2. Add the extension to `SUPPORTED_EXTENSIONS` in `engine/loaders.py`
3. Write `parse_X(file_path, code) -> dict` — return the contract above (including `db_entities`)
4. Optionally write `_extract_db_entities_X()` for ORM entity detection
5. Add the dispatch case to `parse_file()`

Layer classification for the file cap uses filename path keywords — no parser changes needed for that.

---

## 15. Token Cost

| Mode | API calls per run | Approximate cost |
|------|------------------|-----------------|
| Heuristic (`--heuristic`) | 0 | **$0.00** |
| AI (`--ai`) | 1 (batched, all 3 sections) | **~$0.02** |

With `--ai`, `ai_all_sections_claude()` makes a **single Claude API call** that returns executive summary, modernization roadmap, and business logic analysis together. The Claude Code and GitHub Copilot modes use **$0.00** (the LLM session token usage is covered by your Claude Code / Copilot subscription).

Get a key: <https://console.anthropic.com/> · Pricing: <https://www.anthropic.com/pricing>
