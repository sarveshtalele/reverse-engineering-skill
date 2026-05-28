# Installation — Claude Code Skill

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Node.js | 18+ | `node --version` |
| Claude Code | latest | `npm i -g @anthropic-ai/claude-code` |
| Python | 3.8+ | `python --version` |
| Git | any | `git --version` |

---

## Install Method A — Global (Recommended)

Makes `/reverse-engineer` available in **every** project you open with Claude Code.
You set it up once and it works everywhere.

```bash
# macOS / Linux
mkdir -p ~/.claude/skills/reverse-engineer
cp .claude/skills/reverse-engineer/SKILL.md ~/.claude/skills/reverse-engineer/SKILL.md
```

```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\reverse-engineer"
Copy-Item .claude\skills\reverse-engineer\SKILL.md `
          "$env:USERPROFILE\.claude\skills\reverse-engineer\SKILL.md"
```

**Result:** `~/.claude/skills/reverse-engineer/SKILL.md` is installed globally.

---

## Install Method B — Project-Level

Makes `/reverse-engineer` available only inside a specific project folder.

Copy the entire `01-claude-code-skill/` contents (including `.claude/`, `engine/`,
`reverse_engineer_skill.py`) into your project root:

```
your-project/
├── .claude/
│   └── skills/
│       └── reverse-engineer/
│           └── SKILL.md          ← skill definition
├── engine/                        ← analysis engine (9 modules)
├── reverse_engineer_skill.py      ← CLI entry point
└── ...your other files...
```

> **Legacy path** `.claude/commands/reverse-engineer.md` is also included in this
> package and works too — both formats are supported by Claude Code.

---

## Step 2 — Place the engine files

The engine must live in the **same directory** you open Claude Code from.

After copying:

```bash
python -c "from engine.pipeline import run_pipeline; print('engine ok')"
```

If you see `ModuleNotFoundError`, check that `engine/` is beside `reverse_engineer_skill.py`.

---

## Step 3 — Open Claude Code

```bash
cd your-project
claude
```

---

## Step 4 — Verify the skill is registered

Type `/` in the Claude Code input. `reverse-engineer` should appear in the list.

---

## Step 5 — Run your first analysis

```
/reverse-engineer https://github.com/spring-projects/spring-petclinic
```

Expected output in `./outputs/spring-petclinic/`:

| File | Description |
|------|-------------|
| `spring-petclinic_sdd.json` | 14-section System Design Document |
| `spring-petclinic_dashboard.html` | Stakeholder dashboard (open in browser) |
| `spring-petclinic_report.md` | 12-section Markdown report (AI-enhanced) |
| `spring-petclinic_evaluation.md` | 100-point quality evaluation |
| `spring-petclinic_block_diagram.svg` | Architecture block diagram |
| `spring-petclinic_dependency_graph.svg` | Module dependency graph |
| `manifest.json` | Run manifest |

---

## Optional: Enable AI Mode

By default the skill uses **heuristic mode** (Claude Code itself acts as the AI layer —
no API key needed). To also enrich the raw output files with Claude API content:

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # macOS/Linux
$env:ANTHROPIC_API_KEY = "sk-ant-..."  # Windows PowerShell
pip install anthropic
```

Then pass `--ai`:
```
/reverse-engineer https://github.com/owner/repo --ai
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `/reverse-engineer` not in slash menu | Restart Claude Code; confirm `SKILL.md` path is correct |
| `git clone failed` | Ensure the URL is a valid public GitHub repo |
| `ModuleNotFoundError: engine` | Run Claude Code from the folder containing `engine/` |
| `UnicodeEncodeError` on Windows | Python 3.8+ handles this; upgrade Python if it persists |
