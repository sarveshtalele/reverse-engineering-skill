"""
Pipeline
========
Orchestrates the complete reverse engineering pipeline from repository URL
to three output files.

Entry point: :func:`run_pipeline`.

Pipeline stages:

1. **Clone** — shallow-clone the repository with :func:`clone_repo`.
2. **Load** — walk source files with :mod:`engine.loaders`.
3. **Parse** — extract structural elements with :mod:`engine.parsers`
   (smart priority cap for large repos).
4. **Analyze** — compute metrics, dependency graph, API endpoints, dead code,
   and tech stack with :mod:`engine.analyzer`.
5. **AI Analysis** — generate executive summary, modernisation roadmap, and
   business logic analysis with :mod:`engine.ai_analysis` (graceful fallback
   when API unavailable).
6. **Generate** — build SDD JSON, HTML dashboard, and Markdown report with
   :mod:`engine.generators`.
7. **Write** — persist all outputs via :class:`~engine.output_manager.OutputManager`
   and emit a ``manifest.json`` with run metrics.
8. **Cleanup** — remove the temporary clone directory.
"""

import os
import re
import shutil
import subprocess
import tempfile

from engine.loaders     import load_repo
from engine.parsers     import parse_file
from engine.analyzer    import (
    generate_report,
    build_dependency_map,
    generate_mermaid,
    extract_api_endpoints,
    generate_openapi_spec,
    detect_dead_code,
    detect_tech_stack,
    detect_platform,
    detect_architecture_layers,
    find_top_modules,
    detect_database_schema,
    suggest_microservice_data_boundaries,
    generate_block_diagram,
)
from engine.ai_analysis import (
    ai_executive_summary,
    ai_modernization_roadmap,
    ai_business_logic_analysis,
)
from engine.generators.sdd       import generate_sdd
from engine.generators.dashboard import generate_html_dashboard
from engine.generators.report    import generate_md_report
from engine.output_manager       import OutputManager
from engine.evaluator            import evaluate_pipeline_output, write_evaluation_md


def clone_repo(url, target_dir):
    """Shallow-clone a GitHub repository to *target_dir*.

    Performs a ``git clone --depth=1`` to minimise network usage and disk
    space.  Raises :exc:`RuntimeError` if the clone fails.

    Args:
        url (str): GitHub repository URL
            (e.g. ``"https://github.com/owner/repo"``).
        target_dir (str): Local filesystem path where the repository will
            be cloned.

    Raises:
        RuntimeError: If ``git clone`` returns a non-zero exit code, with
            the stderr output included in the exception message.
    """
    print(f"  Cloning {url} -> {target_dir}")
    result = subprocess.run(
        ["git", "clone", "--depth=1", url, target_dir],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git clone failed:\n{result.stderr}")
    print("  [ok] Clone complete")


def repo_name_from_url(url):
    """Extract a sanitised repository name from a GitHub URL.

    Strips trailing slashes and ``.git`` suffixes, takes the final path
    segment, then replaces any character that is not alphanumeric, a
    hyphen, or an underscore with ``_``.

    Args:
        url (str): GitHub repository URL.

    Returns:
        str: A filesystem-safe repository name (e.g. ``"nopCommerce"``).
    """
    name = url.rstrip("/").rstrip(".git").split("/")[-1]
    return re.sub(r'[^\w\-]', '_', name)


def run_pipeline(repo_url, skip_ai=False):
    """Execute the full reverse engineering pipeline for *repo_url*.

    Clones the repository, analyses the source code, optionally calls the AI
    analysis layer, generates five output files (SDD JSON, HTML dashboard,
    Markdown report, quality evaluation, manifest), and prints a formatted
    summary to stdout.

    The temporary clone directory is deleted in the ``finally`` block even
    if an exception occurs during analysis.

    Args:
        repo_url (str): GitHub repository URL to analyse.
        skip_ai (bool): When ``True``, skip all Anthropic API calls and use
            deterministic heuristic fallbacks for executive summary,
            modernisation roadmap, and business logic analysis.  Defaults to
            ``False``.  Set to ``True`` when:

            - No ``ANTHROPIC_API_KEY`` is available.
            - Using GitHub Copilot Chat as the AI engine (recommended Copilot
              workflow: run with ``skip_ai=True``, then read the SDD JSON in
              Copilot Chat for AI-powered narrative).
            - Faster runs without API latency are preferred.

    Returns:
        None

    Side effects:
        - Creates ``outputs/{repo_name}/`` with five files.
        - Prints progress and a summary table to stdout.
    """
    print(f"\n{'='*60}")
    print(f"  Reverse Engineer Skill")
    print(f"  Repository: {repo_url}")
    print(f"{'='*60}\n")

    repo_name = repo_name_from_url(repo_url)
    tmp_dir   = tempfile.mkdtemp(prefix="rev_eng_")
    repo_path = os.path.join(tmp_dir, repo_name)

    try:
        # ----------------------------------------------------------------
        # 1. Clone
        # ----------------------------------------------------------------
        print("[1/8] Cloning repository...")
        clone_repo(repo_url, repo_path)

        # ----------------------------------------------------------------
        # 2. Load files
        # ----------------------------------------------------------------
        print("[2/8] Loading source files...")
        files = load_repo(repo_path)
        print(f"      Found {len(files)} source files")
        if not files:
            print("  [!] No source files found. Check the repository or supported extensions.")
            return

        # ----------------------------------------------------------------
        # 3. Parse (smart cap: prioritise controllers > services > repos)
        # ----------------------------------------------------------------
        print("[3/8] Parsing code structures...")
        FILE_CAP = 300
        if len(files) > FILE_CAP:
            from collections import defaultdict

            def _layer(f):
                """Classify a file into a layer bucket (0=highest priority)."""
                name     = os.path.basename(f["path"]).lower()
                path_low = f["path"].lower().replace("\\", "/")
                if "controller"                            in name: return 0
                if "service"                               in name: return 1
                if "repository" in name or "repo" in name: return 2
                # Domain/entity classes — guaranteed representation for DB schema detection
                if any(s in path_low for s in ["/domain/", "/entities/", "/entity/"]):
                    return 3
                if "model" in name or "dto" in name:       return 4
                return 5

            # Per-layer slot allocation guarantees domain/entity files always appear
            SLOTS = {0: 75, 1: 75, 2: 40, 3: 60, 4: 30, 5: 20}
            buckets = defaultdict(list)
            for f in files:
                buckets[_layer(f)].append(f)
            files = []
            for layer in sorted(SLOTS):
                files.extend(buckets[layer][:SLOTS[layer]])
            files = files[:FILE_CAP]
            print(
                f"      Capped to {len(files)} files "
                f"(layer-balanced: ctrl/svc/repo/domain/model)"
            )

        parsed, skipped = [], 0
        for f in files:
            result = parse_file(f)
            if result:
                parsed.append(result)
            else:
                skipped += 1
        if skipped:
            print(f"      [!] {skipped} files skipped (unsupported extension or parse error)")
        print(f"      Parsed {len(parsed)} / {len(files)} files")

        # ----------------------------------------------------------------
        # 4. Generate report & metrics
        # ----------------------------------------------------------------
        print("[4/8] Generating metrics report...")
        report   = generate_report(parsed)
        dep_map  = build_dependency_map(parsed)
        top_mods = find_top_modules(dep_map)
        mermaid  = generate_mermaid(parsed)

        # ----------------------------------------------------------------
        # 5. API & dead code
        # ----------------------------------------------------------------
        print("[5/8] Extracting APIs and detecting dead code...")
        endpoints    = extract_api_endpoints(parsed)
        openapi_spec = generate_openapi_spec(endpoints, repo_name)
        dead_code    = detect_dead_code(parsed)
        tech_stack   = detect_tech_stack(parsed, repo_path)
        db_schema    = detect_database_schema(parsed)
        block_diagram = generate_block_diagram(parsed, endpoints, db_schema, tech_stack)
        print(
            f"      {len(endpoints)} API endpoints | "
            f"{len(dead_code['dead_files'])} dead files | "
            f"{len(tech_stack)} tech stack items"
        )
        print(
            f"      {db_schema['entity_count']} data entities | "
            f"{db_schema['relationship_count']} relationships detected"
        )

        # ----------------------------------------------------------------
        # 6. AI analysis (skipped when skip_ai=True — heuristics used)
        # ----------------------------------------------------------------
        if skip_ai:
            print("[6/8] AI analysis skipped (--no-ai flag). Using heuristic fallbacks.")
            print("      Tip: Open Copilot Chat → attach 'Reverse Engineer a GitHub Repo'")
            print("           prompt to get AI narrative from GitHub Copilot.")
        else:
            print("[6/8] Running AI analysis (Claude claude-sonnet-4-6)...")

        # All three functions implement graceful heuristic fallbacks
        # automatically when ANTHROPIC_API_KEY is absent or skip_ai=True.
        import os as _os
        _saved_key = _os.environ.get("ANTHROPIC_API_KEY")
        if skip_ai:
            _os.environ.pop("ANTHROPIC_API_KEY", None)

        summary         = ai_executive_summary(parsed, report, repo_name)
        modernization   = ai_modernization_roadmap(parsed, report, repo_name, tech_stack)
        business_logic  = ai_business_logic_analysis(
            parsed, endpoints, db_schema, report, repo_name
        )

        if skip_ai and _saved_key:
            _os.environ["ANTHROPIC_API_KEY"] = _saved_key  # restore
        platform_str    = detect_platform(parsed)
        arch_layers     = detect_architecture_layers(parsed)
        data_boundaries = suggest_microservice_data_boundaries(db_schema, modernization)
        print(
            f"      Architecture: {summary.get('architecture_pattern')} | "
            f"Priority: {summary.get('modernization_priority')}"
        )
        print(
            f"      Business domain: {business_logic.get('business_domain', 'N/A')} | "
            f"Workflows: {len(business_logic.get('core_workflows', []))}"
        )
        print(
            f"      Platform: {platform_str} | Layers: {len(arch_layers)} | "
            f"Data boundaries: {len(data_boundaries)}"
        )

        # ----------------------------------------------------------------
        # 7. Generate & write outputs via OutputManager
        # ----------------------------------------------------------------
        print("[7/8] Generating 3 output files...")
        om = OutputManager(repo_name)

        # File 1: SDD JSON
        sdd_data = generate_sdd(
            repo_name, repo_url, parsed, report, dep_map, endpoints,
            openapi_spec, dead_code, mermaid, tech_stack, summary,
            modernization, repo_path,
            db_schema=db_schema,
            data_boundaries=data_boundaries,
            business_logic=business_logic,
            block_diagram=block_diagram,
        )
        sdd_path = om.write_json(f"{repo_name}_sdd.json", sdd_data)
        print(f"      [ok] SDD JSON -> {sdd_path}")

        # File 2: HTML Dashboard
        html_content = generate_html_dashboard(
            repo_name, repo_url, report, endpoints, dead_code, mermaid,
            tech_stack, summary, modernization, top_mods,
            platform=platform_str,
            arch_layers=arch_layers,
            db_schema=db_schema,
            data_boundaries=data_boundaries,
            business_logic=business_logic,
            block_diagram=block_diagram,
        )
        html_path = om.write_text(f"{repo_name}_dashboard.html", html_content)
        print(f"      [ok] HTML Dashboard -> {html_path}")

        # File 3: Markdown Report
        md_content = generate_md_report(
            repo_name, repo_url, report, parsed, dep_map, endpoints,
            openapi_spec, dead_code, mermaid, tech_stack, summary,
            modernization, top_mods,
            db_schema=db_schema,
            data_boundaries=data_boundaries,
            business_logic=business_logic,
            block_diagram=block_diagram,
        )
        md_path = om.write_text(f"{repo_name}_report.md", md_content)
        print(f"      [ok] MD Report -> {md_path}")

        # Manifest
        primary_lang = (
            max(report["languages"], key=report["languages"].get)
            if report["languages"]
            else "unknown"
        )
        om.write_manifest(
            files_analyzed=report["total_files"],
            classes=report["total_classes"],
            methods=report["total_methods"],
            api_endpoints=len(endpoints),
            dead_files=len(dead_code.get("dead_files", [])),
            primary_language=primary_lang,
        )

        # ----------------------------------------------------------------
        # 8. Evaluate pipeline outputs
        # ----------------------------------------------------------------
        print("[8/8] Evaluating pipeline output quality...")
        evaluation = evaluate_pipeline_output(
            parsed=parsed,
            report=report,
            endpoints=endpoints,
            dead_code=dead_code,
            dep_map=dep_map,
            mermaid_code=mermaid,
            tech_stack=tech_stack,
            summary=summary,
            modernization=modernization,
            db_schema=db_schema,
            data_boundaries=data_boundaries,
            repo_name=repo_name,
        )
        eval_md = write_evaluation_md(evaluation)
        eval_path = om.write_text(f"{repo_name}_evaluation.md", eval_md)
        print(f"      [ok] Evaluation Report -> {eval_path}")

        # ----------------------------------------------------------------
        # 9. Done — print summary
        # ----------------------------------------------------------------
        print("\n[9/9] Complete!\n")
        print(f"{'='*60}")
        print(f"  [DONE] Reverse engineering complete for: {repo_name}")
        print(f"{'='*60}")
        print(f"\n  Output files:")
        for line in om.summary_lines():
            print(line)
        print(f"\n  Analysis summary:")
        print(f"     Files analyzed    : {report['total_files']}")
        print(f"     Classes found     : {report['total_classes']}")
        print(f"     Methods found     : {report['total_methods']}")
        print(f"     API endpoints     : {len(endpoints)}")
        print(f"     Dead code files   : {len(dead_code['dead_files'])}")
        print(f"     Primary language  : {primary_lang}")
        print(f"     Tech stack        : {', '.join(tech_stack[:4]) or 'N/A'}")
        print(f"\n  AI priority         : {summary.get('modernization_priority', 'N/A')}")
        print(f"\n  Quality evaluation:")
        for line in evaluation["summary_lines"]:
            print(line)
        if evaluation["recommendations"]:
            print(f"\n  Recommendations:")
            for rec in evaluation["recommendations"][:3]:
                print(f"     • {rec}")
        print(f"\n{'='*60}\n")

    finally:
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass
