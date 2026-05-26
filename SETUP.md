# Reverse Engineer Skill — Setup Guide

Complete step-by-step instructions for three ways to use this skill:

| Option | AI engine | Anthropic key needed? |
|--------|----------|----------------------|
| [Option 1 — CLI + Claude AI](#option-1--cli-with-claude-ai) | Claude claude-sonnet-4-6 | Yes (optional) |
| [Option 2 — Claude Code Slash Command](#option-2--claude-code-slash-command) | Claude claude-sonnet-4-6 | Optional |
| [Option 3 — GitHub Copilot (no Anthropic key)](#option-3--github-copilot-chat-no-anthropic-key-needed) | GitHub Copilot (GPT-4) | **No** |

**Also in this guide:**
- [Sharing This Skill With Others](#sharing-this-skill-with-others) — 4 distribution methods (GitHub repo, ZIP, global install, prompt file only)
- [Quick Reference Commands](#quick-start-command-reference)
- [Troubleshooting](#troubleshooting)

---

## What This Skill Produces

You give it a GitHub URL. It generates **5 files** in `./outputs/{repo-name}/`:

| File | What it contains |
|------|-----------------|
| `{repo}_sdd.json` | 14-section System Design Document (machine-readable JSON) |
| `{repo}_dashboard.html` | 6-section Apple-theme dashboard — open in any browser |
| `{repo}_report.md` | 12-section Markdown report with business logic analysis |
| `{repo}_evaluation.md` | Automated quality score (100-point PASS/WARN/FAIL) |
| `manifest.json` | Run record with metrics and file sizes |

The **12-section report** now includes a full **Business Logic & Functional Overview**
(Section 2) explaining what the analysed repo does for its users — domain, workflows,
user roles, business rules, and entity glossary.

---

## Prerequisites (All Options)

| Tool | Version | Install |
|------|---------|---------|
| **Python** | 3.8+ | [python.org/downloads](https://www.python.org/downloads/) |
| **Git** | 2.x+ | [git-scm.com/downloads](https://git-scm.com/downloads) |

```bash
python --version   # must be 3.8+
git --version      # must be 2.x+
```

---

## Option 1 — CLI with Claude AI

Best for: Power users, CI/CD pipelines, batch analysis.

### Step 1 — Get this project

```bash
git clone https://github.com/YOUR_USERNAME/reverse-eng-proj.git
cd reverse-eng-proj
```

### Step 2 — Install the dependency

```bash
pip install -r requirements.txt
# installs: anthropic>=0.40.0
```

### Step 3 — Set your Anthropic API key (optional)

Without a key → all sections use heuristic fallbacks (still great output).
With a key → Claude claude-sonnet-4-6 writes the executive summary, modernization
roadmap, and business logic analysis.

```bash
# macOS / Linux (add to ~/.bashrc or ~/.zshrc for persistence)
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Windows PowerShell (add to $PROFILE for persistence)
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-api03-...
```

Get a free key at: <https://console.anthropic.com/>

### Step 4 — Run the analysis

```bash
# With Claude AI (requires ANTHROPIC_API_KEY)
python reverse_engineer_skill.py https://github.com/nopSolutions/nopCommerce

# Without AI (heuristic mode — fast, no API key)
python reverse_engineer_skill.py https://github.com/nopSolutions/nopCommerce --no-ai

# Show help
python reverse_engineer_skill.py --help
```

### Step 5 — Open the dashboard

```bash
# Windows
start outputs\nopCommerce\nopCommerce_dashboard.html

# macOS
open outputs/nopCommerce/nopCommerce_dashboard.html

# Linux
xdg-open outputs/nopCommerce/nopCommerce_dashboard.html
```

---

## Option 2 — Claude Code Slash Command

Best for: Interactive analysis, asking follow-up questions about the output,
          exploring findings conversationally.

The skill is registered as `/reverse-engineer` — a native Claude Code slash command.

### Step 1 — Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude --version    # verify installation
```

### Step 2 — Install the Python dependency

```bash
cd /path/to/reverse-eng-proj
pip install -r requirements.txt
```

### Step 3 — Set your API key (optional, recommended)

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

Claude Code uses this key both for its own conversation AND for the AI analysis
sections in the generated report. Without it, the skill still produces full output
using heuristic fallbacks.

### Step 4 — Open Claude Code INSIDE this project folder

```bash
cd /path/to/reverse-eng-proj
claude
```

> **Critical:** The slash command is registered from `.claude/commands/reverse-engineer.md`.
> Claude Code must be opened with `reverse-eng-proj` as its working directory.
> If you open a parent folder, the command won't appear.

### Step 5 — Verify the slash command is registered

Type `/` in the Claude Code chat. You should see `reverse-engineer` in the autocomplete.

If it doesn't appear:
- Confirm you are inside the `reverse-eng-proj` folder (`pwd` or `cd`)
- Confirm `.claude/commands/reverse-engineer.md` exists
- Restart Claude Code: `Ctrl+C` then `claude` again

### Step 6 — Run the skill

```
/reverse-engineer https://github.com/nopSolutions/nopCommerce
```

Claude Code will:
1. Run `python reverse_engineer_skill.py <url>` internally
2. Show you a summary of the findings in chat
3. Offer to answer questions about the architecture, business logic, and tech debt

### Step 7 — Ask follow-up questions

After the analysis, you can ask Claude Code directly:
```
What are the biggest tech debt risks in this repo?
Explain the checkout workflow based on the API endpoints.
Which microservices would you prioritise first?
Show me the entities in the Customer domain.
```

---

## Option 3 — GitHub Copilot Chat (No Anthropic Key Needed)

Best for: Teams already using GitHub Copilot, users without an Anthropic API key.

**How it works:** The Python script runs the static analysis (parsing, metrics, APIs,
entities, dead code). GitHub Copilot Chat then reads the structured output and provides
the AI narrative — executive summary, business logic explanation, and modernization
roadmap — using its own AI (GPT-4 based). No Anthropic API key required.

### Step 1 — Install VS Code extensions

Open VS Code and install:
- **GitHub Copilot** — extension ID `GitHub.copilot`
- **GitHub Copilot Chat** — extension ID `GitHub.copilot-chat`

Sign in with your GitHub account when prompted.

> You need an active **GitHub Copilot subscription** (free trial available for new users).
> Sign up: <https://github.com/features/copilot>

### Step 2 — Install Python dependency

```bash
pip install -r requirements.txt
```

### Step 3 — Open this project as your VS Code workspace root

```bash
code /path/to/reverse-eng-proj
```

Or: **File → Open Folder** → select the `reverse-eng-proj` folder.

> **Important:** Open `reverse-eng-proj` as the **workspace root**.
> Copilot auto-loads `.github/copilot-instructions.md` from the workspace root.
> Opening a parent folder means Copilot won't have the skill context.

### Step 4 — Verify prompt files are enabled

Check `.vscode/settings.json` (already configured in this project):

```json
{
  "chat.promptFiles": true,
  "chat.promptFilesLocations": { ".github/prompts": true }
}
```

If VS Code shows a "prompt files" notification, click **Enable**.
If the file is missing: `Ctrl+Shift+P` → **Preferences: Open Workspace Settings (JSON)** → add the above.

Then reload: `Ctrl+Shift+P` → **Developer: Reload Window**

### Step 5 — Open Copilot Chat

Press `Ctrl+Alt+I` (Windows/Linux) or `Cmd+Alt+I` (macOS).

Or: click the Copilot Chat icon in the VS Code sidebar.

### Step 6 — Attach the "Reverse Engineer" prompt

1. In the Copilot Chat input box, click the **paperclip / attach** icon (or type `#`)
2. Select **Prompt…**
3. Choose **"Reverse Engineer a GitHub Repo"**

The prompt filename is `.github/prompts/reverse-engineer.prompt.md`.

### Step 7 — Type the GitHub URL and press Enter

```
https://github.com/nopSolutions/nopCommerce
```

Copilot will:
1. Run `python reverse_engineer_skill.py <url> --no-ai` in the terminal
2. Read the generated SDD JSON (all structured data)
3. **Act as your AI architect** — write the executive summary, business domain
   analysis, modernization roadmap using Copilot's own AI
4. Present the full AI analysis in chat
5. Offer to write the AI content back into the report file

### Step 8 — Let Copilot write AI content into the files (optional)

After Copilot shows the analysis in chat, it will ask:

> "Would you like me to update the Markdown report with this AI-generated content?"

Say **yes** and Copilot will edit `outputs/{repo}_{repo}_report.md` Sections 1 and 2
with the AI-generated executive summary and business logic.

### Step 9 — Ask follow-up questions

```
What's the most critical refactoring priority for this codebase?
Explain the order management workflow in plain English.
Which bounded contexts should become independent microservices first?
What external dependencies are highest risk for CVEs?
```

---

### Alternative — Natural language without attaching the prompt

Because `.github/copilot-instructions.md` is auto-loaded when this workspace is open,
you can also just type naturally in Copilot Chat:

```
Analyze https://github.com/nopSolutions/nopCommerce and generate the reverse engineering report
```

Copilot will recognise the task from the instructions file and run the pipeline.

---

## Quick-Start Command Reference

```bash
# ── CLI ──────────────────────────────────────────────────────────────
# Full analysis with Claude AI (requires API key)
python reverse_engineer_skill.py https://github.com/owner/repo

# Fast heuristic analysis (no API key required)
python reverse_engineer_skill.py https://github.com/owner/repo --no-ai

# Show help and all flags
python reverse_engineer_skill.py --help

# ── Claude Code ──────────────────────────────────────────────────────
# (Run from inside the reverse-eng-proj folder)
claude
/reverse-engineer https://github.com/owner/repo

# ── Outputs ──────────────────────────────────────────────────────────
# Check all output files
ls outputs/<repo-name>/

# Open the dashboard (replace platform-specific command)
start outputs/<repo>/<repo>_dashboard.html       # Windows
open outputs/<repo>/<repo>_dashboard.html        # macOS
xdg-open outputs/<repo>/<repo>_dashboard.html   # Linux

# Validate SDD JSON is well-formed
python -c "import json; json.load(open('outputs/<repo>/<repo>_sdd.json', encoding='utf-8')); print('JSON OK')"

# Read quality score quickly
python -c "
import re, pathlib
md = pathlib.Path('outputs/<repo>/<repo>_evaluation.md').read_text(encoding='utf-8')
m = re.search(r'(\d+)/100', md)
print('Score:', m.group(0) if m else 'not found')
"
```

---

## Troubleshooting

### `/reverse-engineer` not showing in Claude Code autocomplete
- Open Claude Code from **inside** `reverse-eng-proj/` (not a parent folder)
- Confirm `.claude/commands/reverse-engineer.md` exists: `ls .claude/commands/`
- Restart Claude Code

### Copilot prompt not showing in VS Code
- Confirm `.vscode/settings.json` has `"chat.promptFiles": true`
- Reload window: `Ctrl+Shift+P` → **Developer: Reload Window**
- Confirm Copilot Chat extension is installed and signed in to GitHub

### "python: command not found"
Try `python3` instead, or check Python is in PATH: `echo $PATH`

### "git: command not found"
Install Git from [git-scm.com](https://git-scm.com/downloads)

### "No source files found"
- Check the URL is correct and the repo is public
- Supported extensions: `.py .java .cs .ts .tsx .js .jsx`
- Some repos (pure config, data, docs) have no parseable source files

### "0 API endpoints detected"
- The repo uses dynamic routing patterns not covered by static analysis
- Not every repo is an API server (libraries, CLIs, data pipelines) — expected
- Check `{repo}_evaluation.md` for recommendations

### "0 entities detected"
- ORM entity files may have been outside the 300-file cap
- Increase `SLOTS[3]` in `engine/pipeline.py` for more domain/entity file slots

### "AI sections show heuristic/fallback text" (CLI mode)
- Set `ANTHROPIC_API_KEY` (see Option 1, Step 3)
- Or switch to GitHub Copilot mode (Option 3) — no Anthropic key needed

### UnicodeEncodeError on Windows
Always run via the entry point (`python reverse_engineer_skill.py`) — it applies
a UTF-8 output fix at startup. Do not run `python engine/pipeline.py` directly.

### Copilot running script but terminal shows errors
- Run `pip install -r requirements.txt` first
- Confirm Python 3.8+ is installed and in PATH
- Try running the script manually first: `python reverse_engineer_skill.py <url> --no-ai`

---

## What Gets Generated — File-by-File

### `{repo}_sdd.json` — 14-section System Design Document

```json
{
  "sdd_metadata":         { "version", "generated_at", "generator", "model_used" },
  "project":              { "name", "url", "primary_language", "tech_stack", "platform", "layers" },
  "executive_summary":    { "purpose", "architecture_pattern", "tech_debt_concerns", "priority" },
  "codebase_metrics":     { "files", "classes", "methods", "endpoints", "languages", "top_modules" },
  "architecture":         { "style", "layers", "components", "dependency_graph" (Mermaid) },
  "module_inventory":     [ per-file: classes, methods, routes, dependencies ],
  "api_catalog":          { "openapi_3.0_spec", "endpoints_list" },
  "dependency_analysis":  { "top_10_modules", "external_deps", "dep_map_sample" },
  "dead_code_analysis":   { "unreferenced_files", "unreferenced_classes" },
  "data_architecture":    { "entities", "relationships", "microservice_boundaries" },
  "business_logic":       { "domain", "what_it_does", "workflows", "roles", "rules", "entity_glossary" },
  "modernization_roadmap":{ "phases", "target_stack", "microservices", "effort", "risks" },
  "risk_assessment":      [ 4 risk items with severity ],
  "tech_debt_inventory":  [ 5 debt categories ]
}
```

### `{repo}_dashboard.html` — 6-section interactive dashboard

Self-contained HTML — open in any browser, no server needed.
Six sidebar sections:
1. **Overview** — Metrics, language chart, tech stack, top modules, **business logic card**
2. **Architecture** — Interactive dependency graph (vis.js), layer list
3. **API Endpoints** — Live-search table with HTTP method colour badges
4. **Dead Code** — SVG ring chart, unreferenced file/class lists
5. **Modernization** — Phase timeline, microservice boundary grid
6. **Data Architecture** — Entity network graph, bounded context cards

### `{repo}_report.md` — 12-section Markdown report

Renders on GitHub, GitLab, Confluence, Notion — any Markdown viewer with Mermaid.

12 sections:
1. Executive Summary
2. **Business Logic & Functional Overview** ← explains what the repo does for its users
3. Codebase Metrics
4. Architecture Overview (Mermaid diagram)
5. Module Inventory (first 40 files)
6. API Catalog (OpenAPI 3.0 spec)
7. Dependency Analysis
8. Dead Code Analysis
9. Tech Debt Inventory
10. Modernization Roadmap
11. Data Architecture & Microservices Decomposition
12. Risk Assessment + Appendix

### `{repo}_evaluation.md` — 100-point quality score

Always generated. Use it after every run to find which sections need follow-up.

| Section | Max points | What it checks |
|---------|-----------|---------------|
| Parsing Quality | 20 | ≥10 files parsed, ≥90% success, ≥5 classes, ≥10 methods |
| API Endpoints | 20 | ≥10 endpoints, ≥3 HTTP methods, ≥80% valid paths |
| Dead Code | 15 | ≤50% dead ratio, ≥1 dead class found |
| Data Architecture | 15 | ≥5 entities, ≥3 boundaries, ≥1 relationship |
| Dependency Graph | 15 | ≥5 nodes, Mermaid diagram present, ≥3 tech items |
| AI Analysis | 15 | Non-fallback summary, known arch pattern, ≥3 phases |

---

## Next Steps After Your First Run

1. **Read the evaluation** (`{repo}_evaluation.md`) — find WARN/FAIL sections
2. **Open the dashboard** (`{repo}_dashboard.html`) — share with stakeholders
3. **Import the Markdown report** into Confluence/Notion/GitHub Wiki
4. **Ask follow-up questions** in Claude Code or Copilot Chat
5. **Feed the SDD JSON** to other AI tools for deeper domain analysis

---

## Sharing This Skill With Others

This skill can be distributed in four ways depending on who you are sharing with
and how they plan to use it. Choose the method that fits your audience.

---

### What Is the "Skill File"?

In Claude Code, a **skill** is any `.md` file placed inside a `.claude/commands/`
directory. When Claude Code opens a folder containing `.claude/commands/`, every
`.md` file inside becomes a `/slash-command` automatically.

For this project:
```
.claude/
└── commands/
    └── reverse-engineer.md   ← THIS is the Claude Code skill file
```

For GitHub Copilot, the equivalent is a **prompt file**:
```
.github/
└── prompts/
    └── reverse-engineer.prompt.md   ← THIS is the Copilot skill file
```

Neither format is a binary — they are plain Markdown files that describe what
the AI should do. You share them like any other file or repository.

---

### Method 1 — Share as a GitHub Repository (Recommended)

**Best for:** Teams, open-source sharing, keeping the skill up to date.

**Steps for you (the sharer):**

1. Push this project to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Add Reverse Engineer Skill v3.0"
   git remote add origin https://github.com/YOUR_USERNAME/reverse-eng-proj.git
   git push -u origin main
   ```

2. Share the repository URL with your team.

**Steps for the recipient:**

```bash
# 1. Clone the skill repository
git clone https://github.com/YOUR_USERNAME/reverse-eng-proj.git
cd reverse-eng-proj

# 2. Install the one dependency
pip install -r requirements.txt

# 3. (Optional) Set Anthropic API key for AI-powered sections
export ANTHROPIC_API_KEY="sk-ant-api03-..."   # macOS/Linux
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."  # Windows PowerShell

# 4. Use via CLI
python reverse_engineer_skill.py https://github.com/owner/repo

# 5. Or open Claude Code from the folder for the slash command
claude
# then type: /reverse-engineer https://github.com/owner/repo

# 6. Or open VS Code in the folder for GitHub Copilot
code .
# then: Copilot Chat → attach "Reverse Engineer a GitHub Repo" prompt
```

> **Keeping it updated:** Recipients can run `git pull` to get future improvements.

---

### Method 2 — Share as a Skill Package ZIP (Offline / No Git)

**Best for:** Sharing in organisations where GitHub is not used, USB/email distribution,
offline environments.

**Create the package (run once):**

**On macOS/Linux:**
```bash
# From inside the reverse-eng-proj folder
cd ..
zip -r reverse-engineer-skill-v3.zip reverse-eng-proj \
  --exclude "reverse-eng-proj/outputs/*" \
  --exclude "reverse-eng-proj/.git/*" \
  --exclude "reverse-eng-proj/__pycache__/*" \
  --exclude "reverse-eng-proj/**/__pycache__/*"
```

**On Windows PowerShell:**
```powershell
# From inside the reverse-eng-proj folder
Set-Location ..
Compress-Archive -Path "reverse-eng-proj" `
  -DestinationPath "reverse-engineer-skill-v3.zip" `
  -Force
# Note: Remove outputs/ and .git/ manually before zipping for a clean package
```

**Minimal package contents (what must be included):**
```
reverse-eng-proj/
├── reverse_engineer_skill.py        ← entry point
├── requirements.txt                 ← dependency list
├── engine/                          ← entire engine package
│   ├── __init__.py
│   ├── loaders.py
│   ├── parsers.py
│   ├── analyzer.py
│   ├── ai_analysis.py
│   ├── evaluator.py
│   ├── output_manager.py
│   ├── pipeline.py
│   └── generators/
│       ├── __init__.py
│       ├── sdd.py
│       ├── report.py
│       └── dashboard.py
├── templates/                       ← schema references
│   ├── sdd_template.json
│   ├── report_template.md
│   └── dashboard_template.html
├── .claude/
│   └── commands/
│       └── reverse-engineer.md     ← Claude Code skill file
├── .github/
│   ├── copilot-instructions.md     ← auto-loaded by Copilot Chat
│   └── prompts/
│       └── reverse-engineer.prompt.md  ← Copilot skill file
└── .vscode/
    └── settings.json               ← prompt file discovery settings
```

> You do NOT need to include `outputs/`, `.git/`, `ARCHITECTURE.md`, `COMPONENTS.md`,
> `EVALUATION.md`, or `SETUP.md` for the skill to work — they are documentation only.

**Steps for the recipient:**

```bash
# 1. Extract the ZIP
unzip reverse-engineer-skill-v3.zip         # macOS/Linux
# Windows: right-click → Extract All

# 2. Enter the folder
cd reverse-eng-proj

# 3. Install dependency
pip install -r requirements.txt
# OR without pip: pip install anthropic>=0.40.0

# 4. Run
python reverse_engineer_skill.py https://github.com/owner/repo --no-ai
```

---

### Method 3 — Install as a Global Claude Code Skill (Personal Use)

**Best for:** Making `/reverse-engineer` available in **every project** you open
in Claude Code, not just this one. Install once; use everywhere.

Claude Code supports two levels of commands:
- **Project-level:** `.claude/commands/` in the current folder (what we have)
- **User-level:** `~/.claude/commands/` — available in every project globally

**Install globally (macOS/Linux):**

```bash
# 1. Create the global commands directory (if it doesn't exist)
mkdir -p ~/.claude/commands

# 2. Copy the skill files
cp .claude/commands/reverse-engineer.md ~/.claude/commands/

# 3. Also copy the Python engine somewhere permanent (e.g. ~/tools/)
cp -r /path/to/reverse-eng-proj ~/tools/reverse-eng-proj
```

**Important:** The `.md` command file references `reverse_engineer_skill.py` by
relative path. For global use, edit `~/.claude/commands/reverse-engineer.md`
and add an absolute path to the script:

In the command file, change the run step to:
```bash
python ~/tools/reverse-eng-proj/reverse_engineer_skill.py "$ARGUMENTS"
```

**Install globally (Windows PowerShell):**

```powershell
# 1. Create the global commands directory
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\commands"

# 2. Copy the skill file
Copy-Item ".claude\commands\reverse-engineer.md" "$env:USERPROFILE\.claude\commands\"

# 3. Copy engine to a permanent location
Copy-Item -Recurse "C:\path\to\reverse-eng-proj" "$env:USERPROFILE\tools\reverse-eng-proj"
```

**Verify global install:**
```bash
# Open Claude Code in ANY folder
cd ~/some-other-project
claude
# Type / → reverse-engineer should appear globally
```

---

### Method 4 — Share Only the GitHub Copilot Prompt File

**Best for:** Teams that use VS Code + GitHub Copilot and don't need the Python engine
(they will use Copilot's manual analysis path).

The Copilot prompt file is completely self-contained as a Markdown instruction document.
Share just this single file:

```
.github/prompts/reverse-engineer.prompt.md
```

**Recipient setup:**

1. In their VS Code workspace, create the folder if it doesn't exist:
   ```bash
   mkdir -p .github/prompts
   ```

2. Copy the file into it:
   ```
   .github/prompts/reverse-engineer.prompt.md
   ```

3. Ensure `.vscode/settings.json` has prompt file discovery enabled:
   ```json
   {
     "chat.promptFiles": true,
     "chat.promptFilesLocations": { ".github/prompts": true }
   }
   ```

4. Reload VS Code: `Ctrl+Shift+P` → **Developer: Reload Window**

5. In Copilot Chat, click the paperclip icon → **Prompt…** →
   **"Reverse Engineer a GitHub Repo"**

> **Note:** Without the Python engine, Copilot will use its own manual analysis path
> (Step 2b in the prompt) — Copilot analyses the repo itself using its tools.
> Quality is comparable but slower than the Python-engine path.

---

### Quick Comparison: Which Method Should You Use?

| Your situation | Best method |
|---------------|------------|
| You have a GitHub account and want to share publicly | Method 1 — GitHub repo |
| Sharing with your team via email or internal file share | Method 2 — ZIP package |
| You want `/reverse-engineer` in every project you open | Method 3 — Global install |
| Your team only uses Copilot, no Python setup | Method 4 — Prompt file only |
| You want to keep the skill private to your org | Method 1 — Private GitHub repo |

---

### What Recipients Need (Minimum Requirements)

| Requirement | Method 1 | Method 2 | Method 3 | Method 4 |
|-------------|----------|----------|----------|----------|
| Python 3.8+ | ✅ | ✅ | ✅ | ❌ (not needed) |
| Git | ✅ | ❌ | ❌ | ❌ |
| `pip install anthropic` | ✅ optional | ✅ optional | ✅ optional | ❌ |
| Claude Code (`npm install -g @anthropic-ai/claude-code`) | For slash cmd | For slash cmd | ✅ yes | ❌ |
| VS Code + GitHub Copilot subscription | For Copilot | For Copilot | For Copilot | ✅ yes |
| Anthropic API key | ❌ optional | ❌ optional | ❌ optional | ❌ never |

---

## Next Steps After Your First Run

1. **Read the evaluation** (`{repo}_evaluation.md`) — find WARN/FAIL sections
2. **Open the dashboard** (`{repo}_dashboard.html`) — share with stakeholders
3. **Import the Markdown report** into Confluence/Notion/GitHub Wiki
4. **Ask follow-up questions** in Claude Code or Copilot Chat
5. **Feed the SDD JSON** to other AI tools for deeper domain analysis

---

_Reverse Engineer Skill v3.0 — See `ARCHITECTURE.md` for technical reference,
`COMPONENTS.md` for function-by-function docs, `EVALUATION.md` for scoring guide._
