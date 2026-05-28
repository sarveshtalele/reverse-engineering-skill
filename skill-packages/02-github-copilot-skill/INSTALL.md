# Installation — GitHub Copilot Skill

## Prerequisites

| Tool | Minimum version | Install |
|------|----------------|---------|
| VS Code | 1.90+ | https://code.visualstudio.com |
| GitHub Copilot extension | latest | VS Code Extensions → search "GitHub Copilot" |
| GitHub Copilot Chat extension | latest | VS Code Extensions → search "GitHub Copilot Chat" |
| Python | 3.8+ | https://python.org |
| Git | any | https://git-scm.com |

Both **GitHub Copilot** and **GitHub Copilot Chat** extensions are required. Copilot Chat is what runs terminal commands and reads files. Sign in to GitHub inside VS Code to activate both.

---

## Step 1 — Place the skill files in your project

Copy the contents of this package into the root of the project where you want to run analyses.

Required layout:

```
your-project/
├── .github/
│   └── prompts/
│       └── reverse-engineer.prompt.md   ← Copilot reads this
├── engine/                               ← analysis engine (9 modules)
│   ├── __init__.py
│   ├── pipeline.py
│   ├── loaders.py
│   ├── parsers.py
│   ├── analyzer.py
│   ├── ai_analysis.py
│   ├── output_manager.py
│   ├── evaluator.py
│   └── generators/
│       ├── sdd.py
│       ├── dashboard.py
│       └── report.py
├── reverse_engineer_skill.py             ← CLI entry point
├── run.bat                               ← Windows launcher
├── run.sh                                ← macOS/Linux launcher
└── outputs/                              ← generated files land here
```

---

## Step 2 — Enable prompt files in VS Code

Open (or create) `.vscode/settings.json` in your project and add:

```json
{
  "chat.promptFiles": true,
  "chat.promptFilesLocations": { ".github/prompts": true }
}
```

Reload VS Code: `Ctrl+Shift+P` → **Developer: Reload Window**

---

## Step 3 — Verify the engine

Open a VS Code terminal (`Ctrl+` ` `) and run:

```bash
python -c "from engine.pipeline import run_pipeline; print('engine ok')"
```

If you see `ModuleNotFoundError: engine`, check that you opened VS Code from the folder containing `engine/`, not from inside a subdirectory.

---

## Step 4 — Open GitHub Copilot Chat

Press `Ctrl+Alt+I` (Windows/Linux) or `Cmd+Alt+I` (macOS) to open the Copilot Chat sidebar.

---

## Step 5 — Attach the prompt

1. Click the **paperclip** (📎) icon in the Copilot Chat input bar
2. Select **Prompt…**
3. Choose **reverse-engineer** from the list

If the prompt doesn't appear, check Step 2 and reload VS Code.

---

## Step 6 — Run your first analysis

Paste a GitHub URL in the chat and press Enter:

```
https://github.com/spring-projects/spring-petclinic
```

Copilot will:
1. Open a terminal and run `python reverse_engineer_skill.py <url> --heuristic`
2. Wait for the engine to finish (10–60 seconds depending on repo size)
3. Read `outputs/spring-petclinic/spring-petclinic_sdd.json`
4. Output AI analysis in the chat
5. Write the AI content into `outputs/spring-petclinic/spring-petclinic_report.md` automatically

---

## Step 7 — Open the dashboard

```bash
# Windows
start outputs\spring-petclinic\spring-petclinic_dashboard.html

# macOS
open outputs/spring-petclinic/spring-petclinic_dashboard.html

# Linux
xdg-open outputs/spring-petclinic/spring-petclinic_dashboard.html
```

---

## Optional: Enable AI Mode (richer Python output)

The prompt uses `--heuristic` by default. To also have the Python engine write AI content into the output files (not just Copilot's narrative):

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # macOS/Linux
$env:ANTHROPIC_API_KEY = "sk-ant-..."  # Windows PowerShell
pip install anthropic
```

Then run the engine directly:

```bash
python reverse_engineer_skill.py https://github.com/owner/repo --ai
```

Cost: ~$0.02 per run.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Prompt not visible in picker | Check Step 2 (settings.json) and reload VS Code |
| `python: command not found` | Use `python3` on macOS/Linux; or install Python from python.org |
| `ModuleNotFoundError: engine` | Open VS Code from the folder containing `engine/`, not a subdirectory |
| Copilot doesn't open a terminal | Ensure GitHub Copilot **Chat** extension is installed (not just Copilot) |
| Terminal opens but nothing runs | Copilot may be in ask mode — switch to agent mode or approve the terminal command |
| `git clone failed` | Ensure the URL is a valid public GitHub repository |
| Output files not created | Check the terminal output for Python errors; run the script manually to diagnose |
| `UnicodeEncodeError` on Windows | Python 3.8+ handles this; upgrade Python if it persists |
