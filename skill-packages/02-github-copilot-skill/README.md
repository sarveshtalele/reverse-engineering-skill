# Reverse Engineer Skill — GitHub Copilot Edition
**Version:** 3.0.0

A `.github/prompts/` file that turns GitHub Copilot Chat into a complete reverse engineering assistant. Copilot runs the Python engine in a terminal and then acts as the AI analyst — no Anthropic API key needed.

---

## What It Does

Attach the prompt in Copilot Chat, paste a GitHub URL, and Copilot will:

1. Run `python reverse_engineer_skill.py <url> --heuristic` in a VS Code terminal
2. Read the generated `{repo}_sdd.json`
3. Produce in the chat:
   - Executive summary and architecture pattern
   - Business logic and domain analysis
   - Modernization roadmap with phase plan
   - Entity glossary and user role breakdown
4. **Automatically write** the AI narrative into `{repo}_report.md` — no confirmation prompt

---

## Output Files (in `./outputs/{repo_name}/`)

| File | Audience | Description |
|------|----------|-------------|
| `{repo}_sdd.json` | Engineering tools, CI | 14-section System Design Document |
| `{repo}_dashboard.html` | Stakeholders, PMs | Self-contained HTML dashboard (open in browser) |
| `{repo}_report.md` | Architects | 12-section Markdown report, AI-enhanced by Copilot |
| `{repo}_block_diagram.svg` | All | Architecture layer diagram |
| `{repo}_dependency_graph.svg` | Engineers | Module dependency graph |
| `{repo}_evaluation.md` | QA | 100-point automated quality score |
| `manifest.json` | Automation | Run metrics and file sizes |

---

## Quick Start

```bash
# Step 1 — Open VS Code in your project (which contains engine/ and reverse_engineer_skill.py)
code your-project

# Step 2 — Open Copilot Chat
# Keyboard: Ctrl+Alt+I (Windows) / Cmd+Alt+I (macOS)

# Step 3 — Attach the prompt
# Click the paperclip icon → Prompt... → select "reverse-engineer"

# Step 4 — Paste a GitHub URL and send
# https://github.com/nopSolutions/nopCommerce
```

See `INSTALL.md` for the full step-by-step guide.

---

## How It Works

```
User attaches prompt + pastes URL in Copilot Chat
                    │
     Copilot reads reverse-engineer.prompt.md
                    │
     Copilot opens VS Code terminal and runs:
     python reverse_engineer_skill.py <url> --heuristic
                    │
           ┌────────┴──────────┐
           │  9-stage engine   │
           │  (Python only)    │
           │  ─ Clone repo     │
           │  ─ Load files     │
           │  ─ Layer cap 300  │
           │  ─ Parse code     │
           │  ─ APIs/dead code │
           │  ─ Heuristic AI   │
           │  ─ Write 7 files  │
           │  ─ Evaluate 100pt │
           └────────┬──────────┘
                    │
     Copilot reads {repo}_sdd.json
                    │
  Generates AI analysis in chat (Executive Summary
  + Business Logic + Modernization Roadmap)
                    │
  Writes AI content into {repo}_report.md automatically
```

**Copilot = the AI engine.** Python handles static analysis; Copilot provides architectural judgment and plain-English narrative.

---

## Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| VS Code | 1.90+ | IDE host |
| GitHub Copilot extension | latest | Copilot completions |
| GitHub Copilot Chat extension | latest | Chat + agent mode (runs terminal commands) |
| Python | 3.8+ | Engine runtime |
| Git | any | Repository cloning |

No Anthropic API key required. Your GitHub Copilot subscription covers the AI usage.

---

## Supported Languages

| Language | What is extracted |
|----------|------------------|
| Python | Classes, methods, Flask/FastAPI routes, SQLAlchemy/Django ORM entities |
| Java | Classes, interfaces, Spring MVC routes, JPA entities |
| C# / .NET | Classes, ASP.NET Core routes, EF Core entities, Web Forms (`.aspx.cs`) |
| TypeScript | Classes, interfaces, Express routes |
| JavaScript | Classes, functions, Express routes |

---

## AI Analysis Coverage

Copilot produces these sections from the SDD JSON data:

| Section | What Copilot writes |
|---------|---------------------|
| Executive Summary | Purpose, architecture pattern, top tech debt concerns, modernization priority |
| Business Logic | Domain name, plain-English description, core workflows, user roles, business rules |
| Entity Glossary | Plain-English meaning of each ORM entity |
| Modernization Roadmap | 4-phase migration plan, target stack, microservice boundaries, risk factors |

All of this is written directly into `{repo}_report.md` automatically.

---

## Optional: Direct Claude API Mode

The Python engine also supports `--ai` for richer content written directly into the output files:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pip install anthropic
python reverse_engineer_skill.py https://github.com/owner/repo --ai
```

In this case the Python script writes AI content to the SDD JSON and report, and Copilot provides additional narrative on top. Cost: ~$0.02 per run.

---

## Real-World Example

Running the prompt for `https://github.com/nopSolutions/nopCommerce`:

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
