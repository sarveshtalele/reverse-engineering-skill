# Reverse Engineer Skill — Distribution Packages v3.0.0

Three ready-to-deploy packages for your team.  
Pick the one that matches your AI tooling, zip it, and share.

---

## Which Package Should I Use?

| # | Package | Best for | AI engine | Requires |
|---|---------|----------|-----------|----------|
| **01** | `01-claude-code-skill/` | Developers using Claude Code CLI | Claude Code (subscription) | `npm i -g @anthropic-ai/claude-code` |
| **02** | `02-github-copilot-skill/` | Teams on VS Code + GitHub Copilot | GitHub Copilot Chat | Copilot subscription + VS Code 1.90+ |
| **03** | `03-agent-sdk-skill/` | CI pipelines, Python automation | Claude API (pay-per-use) | `pip install anthropic` + `ANTHROPIC_API_KEY` |

All three packages bundle the **same Python engine** — the difference is how the AI narrative is generated and how the tool is invoked.

---

## Quick Start

### Option A — Build distributable ZIPs (for sharing with your team)

```bash
# From the repo root
python skill-packages/build_packages.py

# Creates in skill-packages/dist/:
#   reverse-engineer-claude-code-skill-v3.0.0.zip     (~100 KB)
#   reverse-engineer-github-copilot-skill-v3.0.0.zip  (~91 KB)
#   reverse-engineer-agent-sdk-skill-v3.0.0.zip       (~93 KB)
```

Send the appropriate ZIP to your team member. They unzip and follow the `INSTALL.md` inside.

### Option B — Use directly without building

Each folder is already complete — copy it to a project and follow its `INSTALL.md`.

---

## What's Inside Each Package

Every package contains:

```
{package}/
├── README.md           — What the package does and how to use it
├── INSTALL.md          — End-to-end setup guide for this platform
├── CHANGELOG.md        — Version history
├── requirements.txt    — pip dependencies (anthropic>=0.40.0)
├── engine/             — Full analysis engine (9 modules, injected at build time)
├── reverse_engineer_skill.py   — CLI entry point
├── run.bat             — Windows launcher script
├── run.sh              — macOS/Linux launcher script
└── outputs/            — Empty placeholder (outputs land here at runtime)
```

Plus the platform-specific file:

| Package | Platform file | What it does |
|---------|--------------|-------------|
| 01 | `.claude/skills/reverse-engineer/SKILL.md` | Registers `/reverse-engineer` as a Claude Code slash command |
| 02 | `.github/prompts/reverse-engineer.prompt.md` | Registers the prompt in VS Code's Copilot Chat prompt picker |
| 03 | `reverse_engineer_agent.py` + `skill_manifest.json` | Python agent class + Claude tool-use schema |

---

## Package 01 — Claude Code Skill

**Slash command:** `/reverse-engineer <github-url>`

```bash
# 1. Install Claude Code
npm install -g @anthropic-ai/claude-code

# 2. Copy .claude/skills/reverse-engineer/SKILL.md to your global skills folder (one-time setup)
#    macOS/Linux:
mkdir -p ~/.claude/skills/reverse-engineer
cp 01-claude-code-skill/.claude/skills/reverse-engineer/SKILL.md \
   ~/.claude/skills/reverse-engineer/SKILL.md
#    Windows PowerShell:
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\reverse-engineer"
Copy-Item "01-claude-code-skill\.claude\skills\reverse-engineer\SKILL.md" `
          "$env:USERPROFILE\.claude\skills\reverse-engineer\SKILL.md"

# 3. Open Claude Code in a project that has the engine files
claude

# 4. Run the command
# /reverse-engineer https://github.com/spring-projects/spring-petclinic
```

Claude Code acts as the AI engine — no Anthropic API key needed.

---

## Package 02 — GitHub Copilot Skill

**Prompt file:** `.github/prompts/reverse-engineer.prompt.md`

```bash
# 1. Copy the package contents into your project root
#    (engine/, reverse_engineer_skill.py, .github/prompts/)

# 2. Open VS Code in that project
code your-project

# 3. Open Copilot Chat: Ctrl+Alt+I / Cmd+Alt+I
# 4. Click paperclip → Prompt... → reverse-engineer
# 5. Paste a GitHub URL and send
```

GitHub Copilot Chat acts as the AI engine — no Anthropic API key needed.

---

## Package 03 — Agent SDK Skill

**Python class:** `ReverseEngineerAgent`

```bash
# 1. Install dependency
pip install anthropic

# 2. Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Use from Python
python reverse_engineer_agent.py https://github.com/owner/repo --ai
```

```python
from reverse_engineer_agent import ReverseEngineerAgent

result = ReverseEngineerAgent(mode="heuristic").run(
    "https://github.com/spring-projects/spring-petclinic"
)
print(result["summary"]["architecture_pattern"])
print(result["output_files"]["dashboard"])
```

Heuristic mode works without an API key. AI mode calls `claude-sonnet-4-6` (~$0.02/run).

---

## Build Script

`build_packages.py` assembles each package into a temp directory, copies the shared engine from the repo root, creates the ZIP, and removes the temp directory.

```bash
# Default build (v3.0.0)
python skill-packages/build_packages.py

# Build with a custom version tag
python skill-packages/build_packages.py --version 3.1.0
```

---

## Governance

See `GOVERNANCE.md` for:
- Ownership and roles
- Semantic versioning policy
- Release checklist
- How to add a new language parser
- Bug report process
