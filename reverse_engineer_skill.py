#!/usr/bin/env python3
"""
Reverse Engineer Skill — Entry Point
=====================================
Clones any public GitHub repository and generates five professional output files
via static analysis + optional AI analysis (Claude or GitHub Copilot).

Usage:
    python reverse_engineer_skill.py <github-repo-url> [--no-ai] [--help]

Flags:
    --no-ai     Skip all Anthropic API calls. Uses fast heuristic fallbacks for
                executive summary, modernization roadmap, and business logic.
                Use this when:
                  • You have no ANTHROPIC_API_KEY
                  • You are using GitHub Copilot as your AI engine (see SETUP.md)
                  • You want a faster run without AI calls

    --help      Show this help message and exit.

Examples:
    python reverse_engineer_skill.py https://github.com/nopSolutions/nopCommerce
    python reverse_engineer_skill.py https://github.com/spring-projects/spring-petclinic --no-ai
    python reverse_engineer_skill.py https://github.com/owner/my-python-api --no-ai

Output files (in ./outputs/{repo_name}/):
    {repo_name}_sdd.json        — 14-section System Design Document (JSON)
    {repo_name}_dashboard.html  — 6-section Apple-theme Stakeholder Dashboard
    {repo_name}_report.md       — 12-section Technical Markdown Report
    {repo_name}_evaluation.md   — Automated quality score (100-point)
    manifest.json               — Run record with metrics and file sizes

AI modes:
    With ANTHROPIC_API_KEY set   → Claude claude-sonnet-4-6 writes executive summary,
                                   modernization roadmap, and business logic analysis.
    With --no-ai flag            → All AI sections use deterministic heuristics.
                                   Use GitHub Copilot Chat to read the SDD JSON output
                                   and provide AI-quality narrative (see SETUP.md).
    No key + no flag             → Attempts API call, falls back to heuristics
                                   automatically with a warning.

GitHub Copilot users:
    Run with --no-ai. Then open Copilot Chat in VS Code, attach the
    "Reverse Engineer a GitHub Repo" prompt, and let Copilot provide
    AI analysis by reading the generated SDD JSON. No Anthropic key needed.
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
    """CLI entry point. Parses flags and starts the pipeline."""
    args = sys.argv[1:]

    # Show help
    if not args or "--help" in args or "-h" in args:
        print(_HELP)
        sys.exit(0 if args else 1)

    # Extract URL (first positional arg)
    repo_url = next((a for a in args if not a.startswith("--")), None)
    if not repo_url:
        print("Error: No GitHub URL provided.\n")
        print("Usage: python reverse_engineer_skill.py <github-repo-url> [--no-ai]")
        sys.exit(1)

    # Flags
    skip_ai = "--no-ai" in args

    if skip_ai:
        print("  [--no-ai] AI API calls disabled — using heuristic analysis.")
        print("  Tip: Open Copilot Chat in VS Code and attach 'Reverse Engineer a GitHub Repo'")
        print("       prompt to get AI-quality analysis from GitHub Copilot.\n")

    run_pipeline(repo_url, skip_ai=skip_ai)


if __name__ == "__main__":
    main()
