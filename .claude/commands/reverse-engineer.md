# /reverse-engineer

Perform a complete reverse engineering analysis of any public GitHub repository.
**No API keys required** — the Python script uses pure static heuristics, and
Claude Code (you) provides the AI-powered narrative on top of the results.

## Usage

```
/reverse-engineer <github-repo-url>
```

**Examples:**
```
/reverse-engineer https://github.com/nopSolutions/nopCommerce
/reverse-engineer https://github.com/spring-projects/spring-petclinic
/reverse-engineer https://github.com/django/django
/reverse-engineer https://github.com/expressjs/express
```

---

## HOW TO SET UP THIS SKILL IN CLAUDE CODE

This file lives at `.claude/commands/reverse-engineer.md`.
Any `.md` file in `.claude/commands/` automatically becomes a `/` slash command
in Claude Code when you open Claude Code from inside this project folder.

### One-time setup (2 minutes)

**1. Install Claude Code** (if not already installed):
```bash
npm install -g @anthropic-ai/claude-code
claude --version   # verify
```

**2. Clone / place this project folder on your machine:**
```bash
git clone https://github.com/YOUR_USERNAME/reverse-eng-proj.git
cd reverse-eng-proj
```

**3. No pip install needed — zero external dependencies:**
```bash
# requirements.txt is intentionally empty
# Only Python stdlib + git are required
python --version   # Python 3.8+ required
git --version      # git required for cloning repos
```

**4. Open Claude Code FROM INSIDE the project folder:**
```bash
cd /path/to/reverse-eng-proj
claude
```
> **Critical:** The `.claude/commands/` directory must be at the root of the
> folder you open Claude Code in.

**5. Verify the command is registered:**
Type `/` in the Claude Code chat — `reverse-engineer` should appear.

**6. Run your first analysis:**
```
/reverse-engineer https://github.com/nopSolutions/nopCommerce
```

---

## HOW THIS COMMAND WORKS

1. Python script runs full static analysis (no API key needed)
2. Five output files are generated in `./outputs/{repo_name}/`
3. **Claude Code IS the AI engine** — reads the SDD JSON and provides:
   - Executive summary and architecture explanation
   - Business logic and domain analysis
   - Modernisation roadmap with reasoning
   - Block diagram walkthrough
4. Claude Code offers to write the AI content back into the report file

---

## Instructions for Claude Code

When this command is invoked with a GitHub repository URL (`$ARGUMENTS`):

---

### Step 1 — Validate input

Check that `$ARGUMENTS` is a valid GitHub URL (starts with `https://github.com/`).
If not, ask: **"Please provide a full GitHub URL (e.g. https://github.com/owner/repo)."**

---

### Step 2 — Check for the analysis script

```bash
python -c "import pathlib; print('ready' if pathlib.Path('reverse_engineer_skill.py').exists() else 'missing')"
```

---

### Step 3a — Script found: Run static analysis

```bash
python reverse_engineer_skill.py $ARGUMENTS --heuristic
```

**Do NOT run `git clone` before this.** The script clones internally.

The `--heuristic` flag skips the interactive mode-selection prompt (since Claude Code
IS the AI layer here). If the user passed `--ai` in `$ARGUMENTS`, the script will
use Claude API for richer output file content instead.

The script uses **layer-balanced static analysis** — no API keys, no network calls
beyond the initial git clone.

**Pipeline stages:**
1. Clone — shallow `git clone --depth=1` to a temp directory
2. Load — discover source files (Python, Java, C#/.NET, JS/TS, up to 300 files)
3. Parse — extract classes, methods, routes, ORM entities (300-file layer-balanced cap)
4. Metrics — file/class/method counts, dependency graph
5. API & Dead Code — endpoints, database schema, tech stack, block diagram
6. Analysis — static heuristics (or Claude API if `--ai` flag passed)
7. Generate — SDD JSON, HTML dashboard, Markdown report, SVG diagrams
8. Evaluate — 100-point quality scorer
9. Cleanup — remove temp clone directory

**Output files in `./outputs/{repo_name}/`:**
- `{repo_name}_sdd.json`              — 14-section System Design Document
- `{repo_name}_dashboard.html`        — Dashboard with block diagram & business logic
- `{repo_name}_report.md`             — 12-section Markdown technical report
- `{repo_name}_evaluation.md`         — 100-point quality evaluation
- `{repo_name}_block_diagram.svg`     — Architecture block diagram (SVG)
- `{repo_name}_dependency_graph.svg`  — Module dependency graph (SVG)
- `manifest.json`                     — Run record with file sizes

---

### Step 4 — Read the analysis data (YOU are now the AI layer)

Read the generated SDD JSON — it contains all structured data you need:

```
outputs/<repo_name>/<repo_name>_sdd.json
```

Key sections to read:
- `project` — language, tech_stack, platform, layers
- `codebase_metrics` — file/class/method/endpoint counts, language distribution
- `api_catalog` — all API endpoints extracted
- `data_architecture` — ORM entities, relationships, microservice boundaries
- `business_logic` — heuristic values (you will enhance with AI reasoning)
  - `block_diagram` — the auto-generated Mermaid flowchart TB of the system
- `dependency_analysis` — external dependencies

Also read the Markdown report:
```
outputs/<repo_name>/<repo_name>_report.md
```

---

### Step 5 — Provide AI Analysis (YOU are the AI engine)

You are a senior software architect. The Python script gave you structured facts.
Now YOU interpret and narrate them with AI-quality reasoning.

Think through: What does this system actually do? Who uses it? How do the layers
connect? What are the most important business workflows? What risks exist?

#### 5a — Executive Summary

| Field | Your analysis |
|-------|--------------|
| **Purpose** | 2–3 sentences: what does this system do and for whom? |
| **Architecture Pattern** | e.g. "Layered N-Tier Monolith", "CQRS + Event Sourcing", "MVC" |
| **Tech Debt Concerns** | Top 3 specific concerns from the code structure |
| **Modernization Priority** | HIGH / MEDIUM / LOW — with clear reasoning |

#### 5b — Business Logic & Domain

1. **Business Domain** — e.g. "E-Commerce Platform", "HR Management System"
2. **What It Does** — 2–3 paragraphs plain-English from the user's perspective
3. **Core Workflows** — 3–5 key workflows, each with name, steps, and endpoints
4. **User Roles** — Who uses this system? (Customer, Admin, Vendor, etc.)
5. **Key Business Rules** — Rules the system enforces (infer from entities + routes)
6. **Entity Glossary** — For each data entity, explain what it represents in plain English
7. **Block Diagram Walkthrough** — Walk through the Mermaid block diagram in
   `business_logic.block_diagram`: explain each layer and how data flows top to bottom

#### 5c — Architectural Block Diagram Explanation

The dashboard's "How It Works" section shows an auto-generated Mermaid `flowchart TB`.
Explain it in detail:
- What each subgraph represents (Client → API → Business Logic → Data Access → DB)
- How a typical request flows through the layers
- Which controllers handle which workflows
- What the database entities represent in business terms

---

### Step 6 — Output AI Analysis in Chat

Present your complete AI analysis clearly using markdown formatting:

---
#### Executive Summary

**Purpose:** [your analysis]

**Architecture:** [pattern detected]

**Modernization Priority:** [HIGH/MEDIUM/LOW] — [reasoning]

**Top Tech Debt Concerns:**
- [concern 1]
- [concern 2]
- [concern 3]

---
#### Business Logic & Domain

**Business Domain:** [domain name]

**What It Does:**
[your 2–3 paragraph plain-English explanation]

**Core Workflows:**
1. **[Workflow Name]** — [description + key steps + endpoints involved]
2. ...

**User Roles:** [role 1], [role 2], ...

**Key Business Rules:**
- [rule 1]
- [rule 2]

**Entity Glossary:**
| Entity | Business Meaning |
|--------|-----------------|
| [Name] | [plain English] |

---
#### How the Architecture Works (Block Diagram Walkthrough)

**Layer-by-layer explanation:**

1. **Client / User** — [who makes requests]
2. **API / Presentation Layer** — [what controllers/handlers do]
3. **Business Logic / Service Layer** — [what services/managers do]
4. **Data Access / Repository Layer** — [how data is accessed]
5. **Database** — [what entities are stored and why]
6. **External Services** — [integrations detected]

**Request flow:** [describe how a typical request flows through the layers]

---

### Step 7 — Write AI content directly into the report (no prompt needed)

**Do NOT ask the user** — automatically update the report file immediately after presenting the analysis in chat.

Edit `outputs/<repo_name>/<repo_name>_report.md`:
- Replace Section 1 (Executive Summary) with your AI-generated executive summary
- Replace Section 2 (Business Logic) with your full AI-generated business logic analysis
- Replace (or append to) Section 4 (Architecture Overview) with your block diagram walkthrough

Print a one-line confirmation after writing:
```
  [ok] AI analysis written to outputs/<repo_name>/<repo_name>_report.md
```

---

### Step 8 — Report completion

```
Reverse engineering complete for: {repo_name}

Output files (./outputs/{repo_name}/):
  {repo_name}_sdd.json         — System Design Document (14 sections)
  {repo_name}_dashboard.html   — Dashboard (block diagram + business logic)
  {repo_name}_report.md        — Technical Report (12 sections, AI-enhanced and written automatically)
  {repo_name}_evaluation.md    — Quality Evaluation
  manifest.json                — Run Manifest

Analysis (static engine + Claude Code AI):
  Files analyzed    : N
  Classes found     : N
  Methods found     : N
  API endpoints     : N
  Data entities     : N
  Dead code files   : N
  Primary language  : LANG
  Business domain   : DOMAIN (AI-enhanced by Claude Code)
  AI engine         : Claude Code (no API key required)
```

---

### Step 3b — Script missing (manual fallback path)

If `reverse_engineer_skill.py` is not found, perform the analysis manually:

**Clone:**
```bash
git clone --depth=1 $ARGUMENTS ./temp_analysis_repo
```

**Discover source files:** `.py .java .cs .ts .tsx .js .jsx`
Skip: `node_modules/ bin/ obj/ .git/ dist/ build/ migrations/ __pycache__/`

**For each file extract:**
- Classes and interfaces defined
- Methods/functions defined (exclude language keywords)
- Import/using/require statements
- API routes: `[HttpGet]`/`[Route]` (C#), `@GetMapping` (Java), `@app.route` (Python), `app.get` (JS/TS)
- ORM entities: `DbSet<X>` (C#), `@Entity` (Java), `class X(models.Model)` (Python)

**Generate 5 output files** using templates in `templates/` as schema guides:
- `templates/sdd_template.json` → `{repo}_sdd.json` (14 sections)
- `templates/dashboard_template.html` → `{repo}_dashboard.html`
- `templates/report_template.md` → `{repo}_report.md` (12 sections)
- Evaluate your own output → `{repo}_evaluation.md`
- `manifest.json`

Then proceed with Steps 4–8 above.

---

## Notes

- **Zero API keys required by default** — Claude Code (you) IS the AI engine; heuristic mode needs no keys
- **Optional `--ai` flag** — pass `--ai` to use Claude API for richer content written directly into output files (`ANTHROPIC_API_KEY` env var required; `pip install anthropic`)
- **Zero Python dependencies** — only stdlib + git needed (stdlib only for heuristic mode)
- **GitHub Copilot users**: See `.github/prompts/reverse-engineer.prompt.md`
- Templates in `templates/` define exact schemas
- The HTML dashboard is fully self-contained — open in any browser without a server
- Supports: Python, Java, C#/.NET, JavaScript, TypeScript (+JSX/TSX)
- SVG diagrams use hierarchical column layout (dependency graph) and tinted layer colors (block diagram)

## Key project files

| File | Purpose |
|------|---------|
| `reverse_engineer_skill.py` | CLI entry point; `--heuristic` / `--ai` / `--no-ai` flags |
| `engine/pipeline.py` | 9-stage orchestrator (clone → load → parse → analyze → API → AI → generate → evaluate → cleanup) |
| `engine/analyzer.py` | 13+ analysis functions including SVG diagram generators |
| `engine/ai_analysis.py` | Static heuristics + optional Claude API integration (`ai_all_sections_claude`) |
| `engine/parsers.py` | 5 language parsers + ORM entity extractors |
| `engine/evaluator.py` | 100-point quality scorer |
| `engine/generators/sdd.py` | SDD JSON builder (14 sections) |
| `engine/generators/report.py` | Markdown report builder (12 sections) |
| `engine/generators/dashboard.py` | Apple-theme HTML dashboard (6 sections, self-contained) |
| `SETUP.md` | Full setup guide |
| `COMPONENTS.md` | Function-by-function reference |
| `ARCHITECTURE.md` | Deep technical reference |
| `EVALUATION.md` | Guide to interpreting quality scores |
