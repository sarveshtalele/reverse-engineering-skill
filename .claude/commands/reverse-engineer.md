# /reverse-engineer

Perform a complete reverse engineering analysis of any public GitHub repository.
**No Anthropic API key required** — Claude Code (you) is the AI engine.

The Python script handles all static analysis. You read the output and provide
AI-quality business logic analysis, executive summary, and architectural explanation
directly in the chat. Then you offer to write the AI content back into the report file.

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

### One-time setup (5 minutes)

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

**3. Install the one Python dependency:**
```bash
pip install -r requirements.txt
# (Only: anthropic>=0.40.0 — used for optional AI mode)
```

**4. No API key needed.** Claude Code itself provides AI analysis.
   The Python script runs with `--no-ai`; you (Claude Code) read the output
   and generate business logic, summary, and explanation.

   *(Optional: If you want Claude AI in the script too, set `ANTHROPIC_API_KEY`
   and run without `--no-ai`.)*

**5. Open Claude Code FROM INSIDE the project folder:**
```bash
cd /path/to/reverse-eng-proj
claude
```
> **Critical:** The `.claude/commands/` directory must be at the root of the
> folder you open Claude Code in.

**6. Verify the command is registered:**
Type `/` in the Claude Code chat — `reverse-engineer` should appear.

**7. Run your first analysis — no API key needed:**
```
/reverse-engineer https://github.com/nopSolutions/nopCommerce
```

---

## HOW THIS COMMAND WORKS

1. Python script does all static analysis (`--no-ai`, no API key needed)
2. Claude Code reads the SDD JSON output
3. **Claude Code IS the AI engine** — generates business logic, executive summary,
   architectural explanation, and block diagram walkthrough
4. Results shown in chat; offer to write AI content back to the report file

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

### Step 3a — Script found: Run static analysis (no AI, no key needed)

```bash
python reverse_engineer_skill.py $ARGUMENTS --no-ai
```

**Do NOT run `git clone` before this.** The script clones internally.

The `--no-ai` flag means:
- All static analysis runs at full speed (parsing, metrics, APIs, entities, dead code,
  block diagram generation)
- No Anthropic API calls are made
- You (Claude Code) will provide all AI analysis in the next step

**Pipeline stages run:**
1. Clone — shallow `git clone --depth=1` to a temp directory
2. Load — discover source files (Python, Java, C#/.NET, JS/TS, up to 300 files)
3. Parse — extract classes, methods, routes, ORM entities
4. Metrics — file/class/method counts, dependency graph
5. API & Dead Code — endpoints, database schema, tech stack, block diagram
6. Generate — SDD JSON, HTML dashboard (with How It Works section), Markdown report
7. Evaluate — 100-point quality scorer
8. Cleanup — delete temp clone

**Output files in `./outputs/{repo_name}/`:**
- `{repo_name}_sdd.json`        — 14-section System Design Document
- `{repo_name}_dashboard.html`  — Dashboard with block diagram & business logic
- `{repo_name}_report.md`       — 12-section Markdown technical report
- `{repo_name}_evaluation.md`   — 100-point quality evaluation
- `manifest.json`               — Run record with file sizes

---

### Step 4 — Read the analysis data (YOU are now the AI)

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

Also read the Markdown report to understand what was generated:
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

#### 5b — Business Logic & Domain (complete explanation)

1. **Business Domain** — e.g. "E-Commerce Platform", "HR Management System"
2. **What It Does** — 2–3 paragraphs plain-English from the user's perspective
3. **Core Workflows** — 3–5 key workflows, each with:
   - Workflow name (e.g. "Customer Checkout")
   - What triggers it and what steps are involved
   - Which API endpoints are used
4. **User Roles** — Who uses this system? (Customer, Admin, Vendor, etc.)
5. **Key Business Rules** — Rules the system enforces (infer from entities + routes)
6. **Entity Glossary** — For each data entity, explain in plain English what it represents
7. **Block Diagram Walkthrough** — Walk through the Mermaid block diagram in
   `business_logic.block_diagram`: explain each layer in plain English, what it does,
   and how data flows from top to bottom

#### 5c — Architectural Block Diagram Explanation

The dashboard's "How It Works" section shows an auto-generated Mermaid `flowchart TB`.
Explain it in detail:
- What each subgraph represents (Client → API → Business Logic → Data Access → DB)
- How a typical request flows through the layers
- Which controllers handle which workflows
- Which services contain the core business logic
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

### Step 7 — Offer to write AI content back to files

After presenting the analysis in chat, offer:

> "I can write this AI analysis into your report file so it includes the
> AI-generated content. Would you like me to update:
> 1. `{repo}_report.md` — Section 1 (Executive Summary) and Section 2 (Business Logic)
> 2. Both files?"

If the user says yes, edit the Markdown report:
- Replace Section 1 (Executive Summary) with your AI-generated version
- Replace Section 2 (Business Logic) with your full AI-generated business logic
- Add the block diagram walkthrough to Section 4 (Architecture Overview)

---

### Step 8 — Report completion

```
Reverse engineering complete for: {repo_name}

Output files (./outputs/{repo_name}/):
  {repo_name}_sdd.json         — System Design Document (14 sections)
  {repo_name}_dashboard.html   — Dashboard (block diagram + business logic)
  {repo_name}_report.md        — Technical Report (12 sections)
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
  Business domain   : DOMAIN (AI-enhanced)
  AI engine         : Claude Code (no ANTHROPIC_API_KEY required)
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

**Build analysis:**
- Metrics: file/class/method counts, language distribution
- Dependency map → Mermaid `graph TD` diagram
- Dead code: files/classes never imported
- OpenAPI 3.0 spec from routes
- Entity list + microservice boundary clustering
- Block diagram: classify classes into Controller/Service/Repository/DB layers
  and generate a `flowchart TB` Mermaid diagram

**Generate 5 output files** using templates in `templates/` as schema guides:
- `templates/sdd_template.json` → `{repo}_sdd.json` (14 sections)
- `templates/dashboard_template.html` → `{repo}_dashboard.html`
- `templates/report_template.md` → `{repo}_report.md` (12 sections)
- Evaluate your own output → `{repo}_evaluation.md`
- `manifest.json`

Then proceed with Steps 4–8 above.

---

## Notes

- **No ANTHROPIC_API_KEY required** — Claude Code (you) IS the AI engine
- **GitHub Copilot users**: See `.github/prompts/reverse-engineer.prompt.md` — same workflow
- Templates in `templates/` define exact schemas
- The HTML dashboard is fully self-contained — open in any browser without a server
- The "How It Works" dashboard section shows the block diagram (rendered via Mermaid.js)
  plus the full business logic explanation — all populated from static analysis
- Supports: Python, Java, C#/.NET, JavaScript, TypeScript (+JSX/TSX)
- Layer-balanced file cap: controllers → services → repositories → domain → models

## Key project files

| File | Purpose |
|------|---------|
| `reverse_engineer_skill.py` | CLI entry point (`--no-ai` flag skips API calls) |
| `engine/pipeline.py` | 9-stage orchestrator |
| `engine/analyzer.py` | 14 analysis functions (incl. `generate_block_diagram`) |
| `engine/ai_analysis.py` | Claude API + heuristic fallbacks (3 AI functions) |
| `engine/parsers.py` | 5 language parsers + ORM entity extractors |
| `engine/evaluator.py` | 100-point quality scorer |
| `engine/generators/sdd.py` | SDD JSON builder (14 sections) |
| `engine/generators/report.py` | Markdown report builder (12 sections) |
| `engine/generators/dashboard.py` | HTML dashboard (How It Works + block diagram) |
| `SETUP.md` | Full setup guide (CLI + Claude Code + GitHub Copilot) |
| `COMPONENTS.md` | Function-by-function reference |
| `ARCHITECTURE.md` | Deep technical reference |
| `EVALUATION.md` | Guide to interpreting quality scores |
