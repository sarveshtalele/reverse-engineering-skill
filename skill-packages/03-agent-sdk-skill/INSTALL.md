# Installation — Agent SDK Skill

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.8+ | `python --version` |
| Git | any | `git --version` |
| `anthropic` SDK | ≥0.40.0 | `pip show anthropic` |

The `anthropic` package is required for **AI mode** only. Heuristic mode runs with zero pip dependencies (stdlib + git).

---

## Step 1 — Place the skill files in your project

Copy the contents of this package into your project root.

Required layout:

```
your-project/
├── engine/                         ← analysis engine (9 modules)
│   ├── __init__.py
│   ├── pipeline.py
│   ├── loaders.py
│   ├── parsers.py
│   ├── analyzer.py
│   ├── ai_analysis.py
│   ├── output_manager.py
│   ├── evaluator.py
│   └── generators/
│       ├── __init__.py
│       ├── sdd.py
│       ├── dashboard.py
│       └── report.py
├── reverse_engineer_agent.py       ← agent wrapper (this package)
├── reverse_engineer_skill.py       ← CLI entry point
├── skill_manifest.json             ← tool schema for Claude tool-use
├── run.bat                         ← Windows launcher
├── run.sh                          ← macOS/Linux launcher
└── outputs/                        ← generated files land here
```

---

## Step 2 — Install the Anthropic SDK

```bash
pip install anthropic
```

For loading API keys from a `.env` file (optional):

```bash
pip install python-dotenv
```

---

## Step 3 — Set your API key (AI mode only)

Heuristic mode requires no API key. Skip this step if you only need heuristic output.

```bash
# macOS / Linux — current session
export ANTHROPIC_API_KEY=sk-ant-...

# macOS / Linux — persist across sessions
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc

# Windows PowerShell — current session
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Windows — persist across sessions
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
```

Or create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Then add to your script:
```python
from dotenv import load_dotenv
load_dotenv()
```

Get a key: <https://console.anthropic.com/>

---

## Step 4 — Verify the engine

```bash
python -c "from engine.pipeline import run_pipeline; print('engine ok')"
```

If you see `ModuleNotFoundError: engine`, check that `engine/` is in the same directory as `reverse_engineer_agent.py`.

---

## Step 5 — Run your first analysis

### CLI (heuristic mode — no API key)

```bash
python reverse_engineer_agent.py https://github.com/spring-projects/spring-petclinic
```

### CLI (AI mode — requires API key)

```bash
python reverse_engineer_agent.py https://github.com/spring-projects/spring-petclinic --ai
```

### Python API (heuristic mode)

```python
from reverse_engineer_agent import ReverseEngineerAgent

result = ReverseEngineerAgent(mode="heuristic").run(
    "https://github.com/spring-projects/spring-petclinic"
)

print("Architecture :", result["summary"]["architecture_pattern"])
print("Endpoints    :", result["metrics"]["endpoints"])
print("Dashboard    :", result["output_files"]["dashboard"])
```

### Python API (AI mode)

```python
import os
from reverse_engineer_agent import ReverseEngineerAgent

os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."   # or set before running

result = ReverseEngineerAgent(mode="ai").run(
    "https://github.com/spring-projects/spring-petclinic"
)

print("AI Narrative :", result["ai_narrative"][:300])
```

---

## Step 6 — Open the dashboard

```bash
# Windows
start outputs\spring-petclinic\spring-petclinic_dashboard.html

# macOS
open outputs/spring-petclinic/spring-petclinic_dashboard.html

# Linux
xdg-open outputs/spring-petclinic/spring-petclinic_dashboard.html
```

---

## Expected Output

```
  [agent] Starting reverse engineer (mode=heuristic) ...

  Reverse engineering complete for: spring-petclinic

  Output directory: outputs/spring-petclinic/
    sdd              outputs/spring-petclinic/spring-petclinic_sdd.json
    dashboard        outputs/spring-petclinic/spring-petclinic_dashboard.html
    report           outputs/spring-petclinic/spring-petclinic_report.md
    block_diagram    outputs/spring-petclinic/spring-petclinic_block_diagram.svg
    dep_graph        outputs/spring-petclinic/spring-petclinic_dependency_graph.svg
    evaluation       outputs/spring-petclinic/spring-petclinic_evaluation.md
    manifest         outputs/spring-petclinic/manifest.json

  Metrics:
    Files analyzed : 45
    Classes        : 120
    Methods        : 890
    API endpoints  : 23

  Architecture   : Layered N-Tier MVC
  Modernization  : MEDIUM
  Language       : java
```

---

## CI / Automation

### Single repo

```bash
ANTHROPIC_API_KEY=sk-ant-... python reverse_engineer_agent.py \
  https://github.com/owner/repo --heuristic
```

### Batch analysis

```python
from reverse_engineer_agent import ReverseEngineerAgent

repos = [
    "https://github.com/org/service-a",
    "https://github.com/org/service-b",
    "https://github.com/org/service-c",
]

agent = ReverseEngineerAgent(mode="heuristic")
for url in repos:
    result = agent.run(url)
    print(f"{result['repo_name']:30s} | endpoints: {result['metrics'].get('endpoints', 0):4d} "
          f"| priority: {result['summary'].get('modernization_priority', 'n/a')}")
```

### GitHub Actions

```yaml
jobs:
  analyse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install anthropic
      - run: python reverse_engineer_agent.py ${{ inputs.repo_url }} --heuristic
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ANTHROPIC_API_KEY not set` | Set the env var or use `mode="heuristic"` |
| `ModuleNotFoundError: anthropic` | `pip install anthropic` |
| `ModuleNotFoundError: engine` | Ensure `engine/` is in the same folder as `reverse_engineer_agent.py` |
| `git clone failed` | Check the URL is a valid, public GitHub repository |
| Slow first run | `git clone --depth=1` takes 10–60 seconds for large repos |
| `ValueError: Invalid GitHub URL` | URL must start with `https://github.com/owner/repo` |
| AI mode falls back to heuristic | `ANTHROPIC_API_KEY` not set or `anthropic` not installed — check both |
