"""
reverse_engineer_agent.py — Anthropic Agent SDK Edition
Reverse Engineer Skill v3.0

Usage (CLI):
    python reverse_engineer_agent.py https://github.com/owner/repo

Usage (Python):
    from reverse_engineer_agent import ReverseEngineerAgent

    result = ReverseEngineerAgent().run("https://github.com/owner/repo")
    print(result["summary"]["architecture_pattern"])
    print(result["output_files"])

Modes:
    "heuristic"  — no API key required, rule-based analysis (default)
    "ai"         — calls Claude API for AI narrative (requires ANTHROPIC_API_KEY)
"""

from __future__ import annotations

import json
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Optional: load ANTHROPIC_API_KEY from .env
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# ReverseEngineerAgent
# ---------------------------------------------------------------------------

class ReverseEngineerAgent:
    """
    Agent wrapper that exposes the reverse engineer engine as a callable tool
    for programmatic use from CI pipelines, scripts, or any Anthropic SDK agent.

    Parameters
    ----------
    mode : str
        "heuristic" (default) — runs the Python pipeline with rule-based
        analysis; no Anthropic API key required.
        "ai" — additionally calls Claude API for AI narrative sections.
    model : str
        Claude model name used when mode="ai".
        Default: "claude-sonnet-4-6"
    """

    DEFAULT_MODEL = "claude-sonnet-4-6"

    def __init__(self, mode: str = "heuristic", model: str = DEFAULT_MODEL):
        if mode not in ("heuristic", "ai"):
            raise ValueError(f"mode must be 'heuristic' or 'ai', got {mode!r}")
        self.mode = mode
        self.model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, repo_url: str) -> dict[str, Any]:
        """
        Analyse a GitHub repository and return a structured result dict.

        Parameters
        ----------
        repo_url : str
            Full GitHub URL, e.g. "https://github.com/django/django"

        Returns
        -------
        dict with keys:
            repo_name     — repository name
            output_dir    — relative path to generated files
            output_files  — dict mapping label → file path
            metrics       — codebase counts (files, classes, methods, endpoints)
            summary       — architecture_pattern, modernization_priority, …
            ai_narrative  — AI-generated analysis text (or heuristic fallback)
        """
        repo_url = repo_url.strip()
        self._validate_url(repo_url)

        if self.mode == "ai":
            return self._run_ai_mode(repo_url)
        else:
            return self._run_heuristic_mode(repo_url)

    # ------------------------------------------------------------------
    # Heuristic mode — call pipeline directly
    # ------------------------------------------------------------------

    def _run_heuristic_mode(self, repo_url: str) -> dict[str, Any]:
        """Run the 9-stage pipeline and return structured result."""
        from engine.pipeline import run_pipeline  # type: ignore

        result = run_pipeline(repo_url, use_ai=False)
        return self._build_result(repo_url, result)

    # ------------------------------------------------------------------
    # AI mode — use Anthropic tool-use loop
    # ------------------------------------------------------------------

    def _run_ai_mode(self, repo_url: str) -> dict[str, Any]:
        """
        Use the Anthropic client to run the pipeline via tool-use and then
        ask Claude to produce an AI narrative from the SDD output.
        """
        try:
            import anthropic  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "anthropic package is required for AI mode.\n"
                "Install with: pip install anthropic"
            ) from exc

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print(
                "  [!] ANTHROPIC_API_KEY not set — falling back to heuristic mode.\n"
                "      Set the key or use ReverseEngineerAgent(mode='heuristic').",
                file=sys.stderr,
            )
            return self._run_heuristic_mode(repo_url)

        client = anthropic.Anthropic(api_key=api_key)
        tool_def = self._load_tool_definition()

        # ── Turn 1: ask Claude to call the tool ───────────────────────
        messages: list[dict] = [
            {
                "role": "user",
                "content": (
                    f"Please reverse-engineer this GitHub repository and provide "
                    f"a complete analysis:\n\n{repo_url}"
                ),
            }
        ]

        response = client.messages.create(
            model=self.model,
            max_tokens=4096,
            tools=[tool_def],
            messages=messages,
        )

        # ── Execute tool calls ─────────────────────────────────────────
        tool_results: list[dict] = []
        pipeline_result: dict = {}

        for block in response.content:
            if block.type == "tool_use" and block.name == "reverse_engineer_repo":
                inputs: dict = block.input  # type: ignore[attr-defined]
                call_url = inputs.get("repo_url", repo_url)
                call_mode = inputs.get("mode", "heuristic")

                print(f"  [agent] Executing reverse_engineer_repo({call_url!r}, mode={call_mode!r})")

                try:
                    from engine.pipeline import run_pipeline  # type: ignore
                    pipeline_result = run_pipeline(call_url, use_ai=(call_mode == "ai"))
                    tool_output = json.dumps(pipeline_result, indent=2, default=str)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_output[:8000],  # stay within token budget
                    })
                except Exception as exc:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "is_error": True,
                        "content": str(exc),
                    })

        # ── Turn 2: send tool results, get AI narrative ────────────────
        ai_narrative = ""
        if tool_results:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            narrative_response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                tools=[tool_def],
                messages=messages,
            )
            ai_narrative = self._extract_text(narrative_response)

        result = self._build_result(repo_url, pipeline_result)
        if ai_narrative:
            result["ai_narrative"] = ai_narrative
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_url(url: str) -> None:
        """Raise ValueError if url does not look like a GitHub repo URL."""
        if not re.match(r"https?://github\.com/[^/]+/[^/]+", url):
            raise ValueError(
                f"Invalid GitHub URL: {url!r}\n"
                "Expected format: https://github.com/owner/repo"
            )

    @staticmethod
    def _load_tool_definition() -> dict:
        """Load tool schema from skill_manifest.json (same directory as this file)."""
        manifest_path = Path(__file__).parent / "skill_manifest.json"
        if manifest_path.exists():
            with open(manifest_path, encoding="utf-8") as fh:
                return json.load(fh)
        # Inline fallback
        return {
            "name": "reverse_engineer_repo",
            "description": "Reverse engineer a public GitHub repository.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repo_url": {"type": "string"},
                    "mode": {
                        "type": "string",
                        "enum": ["heuristic", "ai"],
                        "default": "heuristic",
                    },
                },
                "required": ["repo_url"],
            },
        }

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Pull plain-text blocks from a Claude Messages response."""
        parts: list[str] = []
        for block in response.content:
            if hasattr(block, "type") and block.type == "text":
                parts.append(block.text)
        return "\n\n".join(parts).strip()

    @staticmethod
    def _build_result(repo_url: str, pipeline_result: dict) -> dict[str, Any]:
        """
        Normalise the raw pipeline result into the public return shape.
        Works whether pipeline_result is populated or empty (error case).
        """
        repo_name: str = pipeline_result.get(
            "repo_name",
            repo_url.rstrip("/").split("/")[-1],
        )
        output_dir: str = pipeline_result.get(
            "output_dir",
            f"outputs/{repo_name}",
        )

        # Collect output file paths ----------------------------------------
        output_files: dict[str, str] = pipeline_result.get("output_files", {})
        if not output_files:
            base = f"{output_dir}/{repo_name}"
            output_files = {
                "sdd":        f"{base}_sdd.json",
                "dashboard":  f"{base}_dashboard.html",
                "report":     f"{base}_report.md",
                "evaluation": f"{base}_evaluation.md",
                "block_diagram": f"{base}_block_diagram.svg",
                "dep_graph":  f"{base}_dependency_graph.svg",
                "manifest":   f"{output_dir}/manifest.json",
            }

        # Metrics --------------------------------------------------------------
        metrics: dict[str, Any] = pipeline_result.get("metrics", {})
        if not metrics:
            sdd_path = Path(output_files.get("sdd", ""))
            if sdd_path.exists():
                try:
                    with open(sdd_path, encoding="utf-8") as fh:
                        sdd = json.load(fh)
                    cm = sdd.get("codebase_metrics", {})
                    metrics = {
                        "files":     cm.get("total_files", 0),
                        "classes":   cm.get("total_classes", 0),
                        "methods":   cm.get("total_methods", 0),
                        "endpoints": cm.get("total_endpoints", 0),
                    }
                except Exception:
                    pass

        # Summary --------------------------------------------------------------
        summary: dict[str, Any] = pipeline_result.get("summary", {})
        if not summary:
            sdd_path = Path(output_files.get("sdd", ""))
            if sdd_path.exists():
                try:
                    with open(sdd_path, encoding="utf-8") as fh:
                        sdd = json.load(fh)
                    ex = sdd.get("executive_summary", {})
                    summary = {
                        "architecture_pattern":  ex.get("architecture_pattern", ""),
                        "modernization_priority": ex.get("modernization_priority", ""),
                        "primary_language":      sdd.get("project", {}).get("primary_language", ""),
                        "tech_stack":            sdd.get("project", {}).get("tech_stack", []),
                    }
                except Exception:
                    pass

        # AI narrative ---------------------------------------------------------
        ai_narrative: str = pipeline_result.get("ai_narrative", "")

        return {
            "repo_name":    repo_name,
            "output_dir":   output_dir,
            "output_files": output_files,
            "metrics":      metrics,
            "summary":      summary,
            "ai_narrative": ai_narrative,
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _print_result(result: dict[str, Any]) -> None:
    """Pretty-print the structured result to stdout."""
    repo = result.get("repo_name", "unknown")
    odir = result.get("output_dir", "outputs/" + repo)
    metrics = result.get("metrics", {})
    summary = result.get("summary", {})
    files = result.get("output_files", {})
    narrative = result.get("ai_narrative", "")

    print()
    print(f"  Reverse engineering complete for: {repo}")
    print()
    print(f"  Output directory: {odir}/")
    for label, path in files.items():
        print(f"    {label:<16} {path}")
    print()
    print(f"  Metrics:")
    print(f"    Files analyzed : {metrics.get('files', 'n/a')}")
    print(f"    Classes        : {metrics.get('classes', 'n/a')}")
    print(f"    Methods        : {metrics.get('methods', 'n/a')}")
    print(f"    API endpoints  : {metrics.get('endpoints', 'n/a')}")
    print()
    print(f"  Architecture   : {summary.get('architecture_pattern', 'n/a')}")
    print(f"  Modernization  : {summary.get('modernization_priority', 'n/a')}")
    print(f"  Language       : {summary.get('primary_language', 'n/a')}")

    if narrative:
        print()
        print("  AI Narrative:")
        for line in textwrap.wrap(narrative, width=72):
            print(f"    {line}")
    print()


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    url = args[0]
    mode = "heuristic"
    model = ReverseEngineerAgent.DEFAULT_MODEL

    for arg in args[1:]:
        if arg in ("--ai", "--mode=ai"):
            mode = "ai"
        elif arg.startswith("--model="):
            model = arg.split("=", 1)[1]

    print(f"\n  [agent] Starting reverse engineer (mode={mode}) ...")
    agent = ReverseEngineerAgent(mode=mode, model=model)
    result = agent.run(url)
    _print_result(result)


if __name__ == "__main__":
    main()
