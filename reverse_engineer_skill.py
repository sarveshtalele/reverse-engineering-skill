#!/usr/bin/env python3
"""
Reverse Engineer Skill — Entry Point
=====================================
Clones any public GitHub repository and generates five professional output
files via **pure static analysis** — no API keys, no LLM accounts, no
internet access beyond git clone.

Usage:
    python reverse_engineer_skill.py <github-repo-url> [--help]

Examples:
    python reverse_engineer_skill.py https://github.com/nopSolutions/nopCommerce
    python reverse_engineer_skill.py https://github.com/spring-projects/spring-petclinic
    python reverse_engineer_skill.py https://github.com/django/django

Output files (in ./outputs/{repo_name}/):
    {repo_name}_sdd.json        — 14-section System Design Document (JSON)
    {repo_name}_dashboard.html  — 6-section interactive HTML Dashboard
    {repo_name}_report.md       — 12-section Technical Markdown Report
    {repo_name}_evaluation.md   — Automated quality score (100-point)
    manifest.json               — Run record with metrics and file sizes

How AI analysis works (NO API key required):
    All analysis — executive summary, architecture pattern, business domain,
    modernisation roadmap — is produced by pure static code heuristics:
    class/method naming conventions, ORM entity detection, import analysis,
    and API route extraction.  No LLM is called by the Python script.

    To get AI-powered narrative on top of the static results:
      • Claude Code   : run /reverse-engineer <url> — Claude reads the
                        output files and provides AI explanation in chat.
      • GitHub Copilot: use the prompt in .github/prompts/reverse-engineer.prompt.md
                        — Copilot reads the SDD JSON and provides AI narrative.
      • Any other LLM : open the generated *_report.md or *_sdd.json and ask
                        your preferred AI to explain or enhance the content.
"""

import sys
import io

# Force UTF-8 output on Windows so print() never raises UnicodeEncodeError
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from engine.pipeline import run_pipeline

_HELP = __doc__


def main() -> None:
    """CLI entry point. Parses arguments and starts the pipeline."""
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(_HELP)
        sys.exit(0 if args else 1)

    # Extract URL (first positional arg — ignore any legacy --no-ai flag)
    repo_url = next((a for a in args if not a.startswith("--")), None)
    if not repo_url:
        print("Error: No GitHub URL provided.\n")
        print("Usage: python reverse_engineer_skill.py <github-repo-url>")
        sys.exit(1)

    if "--no-ai" in args:
        print("  [info] --no-ai flag ignored — this build uses pure static heuristics by default.\n")

    run_pipeline(repo_url)


if __name__ == "__main__":
    main()
