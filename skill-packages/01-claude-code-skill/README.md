# Reverse Engineer Skill — Claude Code Edition
**Version:** 3.0.0

Adds a `/reverse-engineer` slash command to Claude Code. Run it against any public GitHub repository and get 7 professional output files plus a full AI-quality narrative — all inside Claude Code, no Anthropic API key required.

---

## What It Does

```
/reverse-engineer https://github.com/spring-projects/spring-petclinic
```

Claude Code will:
1. Run `python reverse_engineer_skill.py <url> --heuristic` (the Python engine)
2. Read the generated `_sdd.json` (the 14-section System Design Document)
3. Produce in the chat:
   - Executive summary and architecture analysis
   - Business logic and domain explanation
   - Modernization roadmap with phases and risk factors
   - Architecture block diagram walkthrough (layer by layer)
4. **Automatically write** the AI narrative into `{repo}_report.md` — no confirmation prompt

---

## Output Files (in `./outputs/{repo_name}/`)

| File | Audience | Description |
|------|----------|-------------|
| `{repo}_sdd.json` | Engineering tools, CI | 14-section System Design Document |
| `{repo}_dashboard.html` | Stakeholders, PMs | Self-contained HTML dashboard (open in browser) |
| `{repo}_report.md` | Architects | 12-section Markdown report, AI-enhanced |
| `{repo}_block_diagram.svg` | All | Architecture layer diagram — Client → API → Service → DB |
| `{repo}_dependency_graph.svg` | Engineers | Module dependency graph — Sources / Hubs / Sinks columns |
| `{repo}_evaluation.md` | QA | 100-point automated quality score |
| `manifest.json` | Automation | Run metrics and file sizes |

---

## Quick Start

```bash
# Step 1 — Install Claude Code
npm install -g @anthropic-ai/claude-code

# Step 2 — Global skill install (one time — works in every project)
# macOS / Linux:
mkdir -p ~/.claude/skills/reverse-engineer && \
cp .claude/skills/reverse-engineer/SKILL.md ~/.claude/skills/reverse-engineer/SKILL.md

# Windows PowerShell:
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\reverse-engineer"
Copy-Item ".claude\skills\reverse-engineer\SKILL.md" `
          "$env:USERPROFILE\.claude\skills\reverse-engineer\SKILL.md"

# Step 3 — Open Claude Code in any project that has the engine
cd your-project-with-engine
claude

# Step 4 — Run
# /reverse-engineer https://github.com/spring-projects/spring-petclinic
```

See `INSTALL.md` for the full step-by-step guide including project-level install, engine placement, and troubleshooting.

---

## How It Works

```
User types:  /reverse-engineer https://github.com/...
                        │
              Claude reads SKILL.md
                        │
         python reverse_engineer_skill.py <url> --heuristic
                        │
              ┌─────────┴──────────┐
              │  9-stage engine    │
              │  (Python only)     │
              │  ─ Clone           │
              │  ─ Load files      │
              │  ─ Layer cap 300   │
              │  ─ Parse code      │
              │  ─ APIs/dead code  │
              │  ─ Heuristic AI    │
              │  ─ Write 7 files   │
              │  ─ Evaluate (100pt)│
              └─────────┬──────────┘
                        │
          Claude reads {repo}_sdd.json
                        │
    Generates AI narrative in chat (Executive Summary
    + Business Logic + Modernization Roadmap + Block
    Diagram Walkthrough)
                        │
    Writes AI content into {repo}_report.md automatically
```

**Claude Code = the AI engine.** The Python script handles static analysis; Claude Code provides the architectural reasoning and plain-English explanation.

---

## Two Install Modes

### Global install (recommended)
The SKILL.md lives in `~/.claude/skills/reverse-engineer/` — available in **every** project you open with Claude Code.

### Project-level install
The SKILL.md lives in `.claude/skills/reverse-engineer/SKILL.md` inside your project — available only when you open that project.

The `engine/` folder and `reverse_engineer_skill.py` must always be present in your **working directory** (the folder Claude Code is opened from).

---

## Analysis Modes

| Invocation | Mode | AI source |
|------------|------|----------|
| `/reverse-engineer <url>` | Heuristic engine + Claude Code AI | Claude Code (no key) |
| `/reverse-engineer <url> --ai` | Full AI engine + Claude Code AI | Python uses Claude API (~$0.02) + Claude Code |
| `python reverse_engineer_skill.py <url> --heuristic` | Heuristic only (CLI) | None |
| `python reverse_engineer_skill.py <url> --ai` | Full AI (CLI) | Claude API only |

---

## Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Claude Code | latest | Slash command host + AI engine |
| Node.js | 18+ | Required by Claude Code |
| Python | 3.8+ | Engine runtime |
| Git | any | Repository cloning |
| `anthropic` pip package | ≥0.40.0 | **Optional** — only for `--ai` CLI flag |

---

## Supported Languages

| Language | Extensions | What is extracted |
|----------|------------|------------------|
| Python | `.py` | Classes, methods, Flask/FastAPI routes, SQLAlchemy/Django ORM entities |
| Java | `.java` | Classes, interfaces, methods, Spring MVC routes, JPA entities |
| C# / .NET | `.cs`, `.aspx.cs` | Classes, methods, ASP.NET Core routes, EF Core DbSet entities |
| TypeScript | `.ts`, `.tsx` | Classes, interfaces, functions, Express routes |
| JavaScript | `.js`, `.jsx` | Classes, functions, Express routes |

---

## Real-World Example

Running `/reverse-engineer https://github.com/nopSolutions/nopCommerce`:

```
Files analyzed    : 292 (layer-balanced from 3,114 total)
Classes found     : 284
Methods found     : 2,301
API endpoints     : 284
Dead code files   : 241
Primary language  : C# / .NET
Tech stack        : ASP.NET Core, Docker
Evaluation score  : 78/100  [MEDIUM confidence]
```
