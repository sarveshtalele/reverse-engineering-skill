# Reverse Engineer Skill — Anthropic Agent SDK Edition
**Version:** 3.0.0

A Python agent wrapper that exposes the reverse engineer engine as a callable tool. Use it from CI pipelines, automation scripts, or any Anthropic SDK agent. Heuristic mode requires zero API keys.

---

## What It Does

```python
from reverse_engineer_agent import ReverseEngineerAgent

result = ReverseEngineerAgent(mode="heuristic").run(
    "https://github.com/spring-projects/spring-petclinic"
)

print(result["summary"]["architecture_pattern"])   # "Layered N-Tier MVC"
print(result["metrics"]["endpoints"])              # 23
print(result["output_files"]["dashboard"])         # outputs/spring-petclinic/...dashboard.html
print(result["ai_narrative"])                      # heuristic summary text
```

Or from the command line:

```bash
# Heuristic mode (no API key)
python reverse_engineer_agent.py https://github.com/django/django

# AI mode (calls Claude API)
python reverse_engineer_agent.py https://github.com/django/django --ai
```

---

## Output Files (in `./outputs/{repo_name}/`)

| File | Audience | Description |
|------|----------|-------------|
| `{repo}_sdd.json` | Engineering tools, CI | 14-section System Design Document |
| `{repo}_dashboard.html` | Stakeholders, PMs | Self-contained HTML dashboard |
| `{repo}_report.md` | Architects | 12-section Markdown report |
| `{repo}_block_diagram.svg` | All | Architecture layer diagram |
| `{repo}_dependency_graph.svg` | Engineers | Module dependency graph |
| `{repo}_evaluation.md` | QA | 100-point quality score |
| `manifest.json` | Automation | Run metrics and file sizes |

---

## Quick Start

### Install

```bash
# Clone / unzip the package into your project
cd your-project

# Install the Anthropic SDK (required for AI mode; heuristic mode needs nothing)
pip install anthropic

# Optional: load API key from .env
pip install python-dotenv
```

### Set your API key (AI mode only)

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Or create a .env file in the project root:
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Run

```bash
# Heuristic mode — $0.00, no key needed
python reverse_engineer_agent.py https://github.com/nopSolutions/nopCommerce

# AI mode — ~$0.02/run, requires ANTHROPIC_API_KEY
python reverse_engineer_agent.py https://github.com/nopSolutions/nopCommerce --ai
```

See `INSTALL.md` for full setup steps.

---

## Architecture

```
reverse_engineer_agent.py
        │
        ├── mode="heuristic"  ─────►  engine/pipeline.py  ─►  7 output files
        │                                                       returns structured dict
        │
        └── mode="ai"
                │
                ├── Anthropic client
                │   Turn 1: Claude sees tool definition (skill_manifest.json)
                │           → calls reverse_engineer_repo tool
                │
                ├── Tool execution: engine/pipeline.py  ─►  7 output files
                │   (same as heuristic but result fed back to Claude)
                │
                └── Turn 2: Claude reads SDD JSON result
                            → generates AI narrative
                            → returns structured dict with ai_narrative
```

---

## `ReverseEngineerAgent` API

### Constructor

```python
ReverseEngineerAgent(mode="heuristic", model="claude-sonnet-4-6")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | `str` | `"heuristic"` | `"heuristic"` or `"ai"` |
| `model` | `str` | `"claude-sonnet-4-6"` | Claude model for AI mode |

### `.run(repo_url)` — Return Value

```python
{
    "repo_name":    str,           # e.g. "spring-petclinic"
    "output_dir":   str,           # e.g. "outputs/spring-petclinic"
    "output_files": {
        "sdd":           str,      # path to _sdd.json
        "dashboard":     str,      # path to _dashboard.html
        "report":        str,      # path to _report.md
        "block_diagram": str,      # path to _block_diagram.svg
        "dep_graph":     str,      # path to _dependency_graph.svg
        "evaluation":    str,      # path to _evaluation.md
        "manifest":      str,      # path to manifest.json
    },
    "metrics": {
        "files":     int,          # files analyzed
        "classes":   int,
        "methods":   int,
        "endpoints": int,
    },
    "summary": {
        "architecture_pattern":  str,
        "modernization_priority": str,   # "HIGH" | "MEDIUM" | "LOW"
        "primary_language":      str,
        "tech_stack":            list[str],
    },
    "ai_narrative": str,           # AI narrative or heuristic summary
}
```

---

## `skill_manifest.json` — Tool Definition

The tool schema used in Claude API tool-use conversations:

```json
{
  "name": "reverse_engineer_repo",
  "description": "Reverse engineer any public GitHub repository...",
  "input_schema": {
    "type": "object",
    "properties": {
      "repo_url": { "type": "string" },
      "mode":     { "type": "string", "enum": ["heuristic", "ai"] }
    },
    "required": ["repo_url"]
  }
}
```

Use this to add the reverse engineer capability to any Anthropic tool-use conversation.

---

## CI / Automation Examples

### GitHub Actions

```yaml
- name: Reverse engineer dependency
  run: |
    pip install anthropic
    python reverse_engineer_agent.py https://github.com/owner/dep-repo --heuristic
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}   # optional

- name: Print metrics
  run: |
    python -c "
    import json
    m = json.load(open('outputs/dep-repo/manifest.json'))
    print('Endpoints:', m['metrics']['api_endpoints'])
    print('Dead files:', m['metrics']['dead_files'])
    "
```

### Python script

```python
from reverse_engineer_agent import ReverseEngineerAgent

repos = [
    "https://github.com/org/service-a",
    "https://github.com/org/service-b",
]

for url in repos:
    result = ReverseEngineerAgent(mode="heuristic").run(url)
    print(f"{result['repo_name']}: {result['metrics']['endpoints']} endpoints, "
          f"score={result['summary'].get('modernization_priority')}")
```

---

## Requirements

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.8+ | Runtime |
| Git | any | Repository cloning |
| `anthropic` | ≥0.40.0 | AI mode and tool-use (optional for heuristic) |

---

## Supported Languages

Python · Java · C# / .NET · JavaScript · TypeScript (+ JSX/TSX)

---

## Cost

| Mode | API calls | Cost per run |
|------|-----------|-------------|
| `heuristic` | 0 | **$0.00** |
| `ai` | 1 (batched, all 3 sections) | **~$0.02** |

Get a key: <https://console.anthropic.com/>
