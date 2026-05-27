"""
Markdown Report Generator
=========================
Produces a comprehensive, human-readable Markdown technical report that
documents every facet of the reverse engineering analysis:

- Executive summary (AI-generated or heuristic fallback)
- Codebase metrics and language distribution table
- Architecture overview with a fenced Mermaid diagram
- Module inventory (first 40 files, remainder summarised)
- API catalog with an OpenAPI 3.0 JSON block
- Dependency analysis and most-connected modules
- Dead code analysis (files and classes)
- Tech-debt inventory
- Phased modernisation roadmap
- Risk assessment table

The report is self-contained and renders correctly in any Markdown
viewer that supports GitHub Flavored Markdown (GFM) and Mermaid diagrams
(e.g. GitHub, GitLab, Obsidian, Typora).
"""

import json
import datetime
from pathlib import Path

from engine.analyzer import (
    detect_platform,
    detect_architecture_layers,
    extract_external_deps,
)


def render_ascii_block_diagram(block_diagram_data):
    if not block_diagram_data or not isinstance(block_diagram_data, dict) or "layers" not in block_diagram_data:
        return "No system architecture block diagram available."

    lines = []
    box_width = 72
    inner_width = box_width - 2

    layers = block_diagram_data.get("layers", [])
    edges = block_diagram_data.get("edges", [])

    for idx, layer in enumerate(layers):
        # Top border
        lines.append("┌" + "─" * inner_width + "┐")
        
        # Layer title
        title = f" {layer.get('label', 'Layer').upper()} "
        lines.append("│" + title.center(inner_width, " ") + "│")
        
        # Divider
        lines.append("├" + "─" * inner_width + "┤")
        
        # Nodes
        nodes = layer.get("nodes", [])
        if not nodes:
            lines.append("│" + " (No components detected) ".center(inner_width) + "│")
        else:
            # Format nodes in rows of 2 for clean readability
            node_labels = [f"• {n.get('label', '')}" for n in nodes]
            row = []
            for i, label in enumerate(node_labels):
                row.append(label)
                if len(row) == 2 or i == len(node_labels) - 1:
                    # Render row
                    if len(row) == 2:
                        left = row[0]
                        right = row[1]
                        col_width = inner_width // 2
                        left_part = left.ljust(col_width - 2)
                        right_part = right.ljust(inner_width - len(left_part) - 4)
                        lines.append(f"│  {left_part}  {right_part}  │")
                    else:
                        left = row[0]
                        lines.append(f"│  {left.ljust(inner_width - 4)}  │")
                    row = []
                    
        # Bottom border
        lines.append("└" + "─" * inner_width + "┘")

        # If not the last layer, add flow connector
        if idx < len(layers) - 1:
            current_node_ids = {n["id"] for n in nodes}
            next_nodes = layers[idx+1].get("nodes", [])
            next_node_ids = {n["id"] for n in next_nodes}
            
            layer_edge_labels = []
            for edge in edges:
                if edge.get("from") in current_node_ids and edge.get("to") in next_node_ids:
                    lbl = edge.get("label", "")
                    if lbl and lbl not in layer_edge_labels:
                        layer_edge_labels.append(lbl)
            
            connector_label = f" ({', '.join(layer_edge_labels)})" if layer_edge_labels else ""
            
            lines.append(" ")
            lines.append("│".center(box_width).rstrip() + connector_label)
            lines.append("▼".center(box_width).rstrip())
            lines.append(" ")

    return "\n".join(lines)


def generate_md_report(
    repo_name,
    repo_url,
    report,
    parsed,
    dep_map,
    endpoints,
    openapi_spec,
    dead_code,
    tech_stack,
    summary,
    modernization,
    top_mods,
    db_schema=None,
    data_boundaries=None,
    business_logic=None,
    block_diagram=None,
):
    """Build and return a comprehensive Markdown technical report.

    Args:
        repo_name (str): Human-readable repository name used in headings.
        repo_url (str): Original GitHub clone URL for the repository link.
        report (dict): Metrics dict from
            :func:`engine.analyzer.generate_report`.
        parsed (list[dict]): List of file records from
            :func:`engine.parsers.parse_file`.
        dep_map (dict[str, set[str]]): Module dependency map from
            :func:`engine.analyzer.build_dependency_map`.
        endpoints (list[dict]): API endpoint records from
            :func:`engine.analyzer.extract_api_endpoints`.
        openapi_spec (dict): OpenAPI 3.0 spec from
            :func:`engine.analyzer.generate_openapi_spec`.
        dead_code (dict): Dead-code report from
            :func:`engine.analyzer.detect_dead_code`.
        mermaid_code (str): Mermaid diagram string from
            :func:`engine.analyzer.generate_mermaid`.
        tech_stack (list[str]): Detected technologies from
            :func:`engine.analyzer.detect_tech_stack`.
        summary (dict): AI executive summary from
            :func:`engine.ai_analysis.ai_executive_summary`.
        modernization (dict): AI modernisation roadmap from
            :func:`engine.ai_analysis.ai_modernization_roadmap`.
        top_mods (list[tuple[str, int]]): Most-connected modules from
            :func:`engine.analyzer.find_top_modules`.
        db_schema (dict | None): Database schema dict from
            :func:`engine.analyzer.detect_database_schema`.
        data_boundaries (list[dict] | None): Microservice data boundary dicts
            from :func:`engine.analyzer.suggest_microservice_data_boundaries`.
        business_logic (dict | None): Business logic analysis dict from
            :func:`engine.ai_analysis.ai_business_logic_analysis`.  When
            ``None`` the Business Logic section is populated with heuristic
            fallback text.

    Returns:
        str: A complete Markdown document as a string, ready to be written
        to a ``.md`` file.  The document has 12 sections plus an appendix:

        1. Executive Summary
        2. Business Logic & Functional Overview  *(new)*
        3. Codebase Metrics
        4. Architecture Overview
        5. Module Inventory
        6. API Catalog
        7. Dependency Analysis
        8. Dead Code Analysis
        9. Tech Debt Inventory
        10. Modernization Roadmap
        11. Data Architecture & Microservices Decomposition
        12. Risk Assessment
    """
    now     = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    primary = (
        max(report["languages"], key=report["languages"].get)
        if report["languages"]
        else "unknown"
    )

    # ------------------------------------------------------------------
    # Language distribution table
    # ------------------------------------------------------------------
    lang_rows = "\n".join(
        f"| {lang.capitalize()} | {count} | "
        f"{round(count / report['total_files'] * 100 if report['total_files'] else 0)}% |"
        for lang, count in sorted(
            report["languages"].items(), key=lambda x: x[1], reverse=True
        )
    )

    # ------------------------------------------------------------------
    # Stack strings
    # ------------------------------------------------------------------
    tech_stack_str = (
        ", ".join(f"`{t}`" for t in tech_stack) if tech_stack else "_None detected_"
    )
    target_stack_str = (
        ", ".join(f"`{t}`" for t in modernization.get("target_stack", []))
        if modernization.get("target_stack")
        else "_See modernization plan_"
    )

    # ------------------------------------------------------------------
    # Inline markdown fragments
    # ------------------------------------------------------------------
    concerns_md    = "\n".join(f"- {c}" for c in summary.get("tech_debt_concerns", []))
    risk_factors_md = "\n".join(f"- {r}" for r in modernization.get("risk_factors", []))

    # Module inventory (first 40 files)
    modules_md = ""
    for item in parsed[:40]:
        fname      = Path(item["file"]).name
        classes    = ", ".join(f"`{c}`" for c in item.get("classes", [])[:5]) or "_none_"
        methods    = ", ".join(f"`{m}`" for m in item.get("methods", [])[:5]) or "_none_"
        dep_count  = len(item.get("dependencies", []))
        route_count = len(item.get("routes", []))
        modules_md += f"\n#### `{fname}`\n"
        modules_md += f"- **Language**: {item.get('language', 'unknown').capitalize()}\n"
        modules_md += f"- **Classes**: {classes}\n"
        modules_md += f"- **Methods (top 5)**: {methods}\n"
        modules_md += f"- **Dependencies**: {dep_count} imports\n"
        if route_count:
            modules_md += f"- **API Routes**: {route_count} route(s)\n"

    if len(parsed) > 40:
        modules_md += (
            f"\n_...and {len(parsed) - 40} more files. "
            "See the SDD JSON for the complete inventory._\n"
        )

    # API endpoints table
    if endpoints:
        api_rows = "\n".join(
            f"| `{', '.join(ep['methods'])}` | `{ep['path']}` | "
            f"`{ep.get('class') or 'global'}.{ep.get('method') or 'handler'}()` | "
            f"`{Path(ep['file']).name}` |"
            for ep in endpoints[:50]
        )
        api_table = (
            f"| Method | Path | Handler | File |\n"
            f"|--------|------|---------|------|\n"
            f"{api_rows}"
        )
        if len(endpoints) > 50:
            api_table += f"\n\n_...and {len(endpoints) - 50} more endpoints._"
    else:
        api_table = (
            "_No API routes detected via static analysis. "
            "Routes may use dynamic registration patterns._"
        )

    # Top dependency modules table
    top_deps_md = "\n".join(
        f"| `{m}` | {c} |" for m, c in top_mods[:10]
    )

    # Dead code lists
    dead_files_md = (
        "\n".join(f"- `{Path(f).name}`" for f in dead_code.get("dead_files", [])[:20])
        or "_None detected_"
    )
    dead_classes_md = (
        "\n".join(
            f"- `{d['class']}` in `{Path(d['file']).name}`"
            for d in dead_code.get("dead_classes", [])[:20]
        )
        or "_None detected_"
    )

    # Modernization phases
    phases_md = ""
    for ph in modernization.get("phases", []):
        risk_marker = {"LOW": "LOW", "MEDIUM": "MEDIUM", "HIGH": "HIGH"}.get(
            ph.get("risk", ""), ""
        )
        tasks_md = "\n".join(f"  - {t}" for t in ph.get("tasks", []))
        phases_md += (
            f"\n**Phase {ph.get('phase')}: {ph.get('title')}** "
            f"`{risk_marker} risk` — _{ph.get('duration')}_\n{tasks_md}\n"
        )

    microservices_md = "\n".join(
        f"- **{s}**" for s in modernization.get("microservices_boundaries", [])
    )

    # ------------------------------------------------------------------
    # Business logic section fragments
    # ------------------------------------------------------------------
    bl = business_logic or {}
    bl_domain     = bl.get("business_domain", "General Business Application")
    bl_what       = bl.get("what_it_does", "_Business logic analysis unavailable. Set ANTHROPIC_API_KEY for AI-powered analysis._")
    bl_roles      = bl.get("user_roles", [])
    bl_rules      = bl.get("key_business_rules", [])
    bl_workflows  = bl.get("core_workflows", [])
    bl_entities   = bl.get("data_entities_explained", [])
    bl_integrations = bl.get("integrations", [])
    bl_fallback   = bl.get("fallback_used", True)

    # Mapped codebase information for stakeholder mapping chapter
    mapping = bl.get("ai_codebase_mapping", {})
    what_repo_does = mapping.get("what_the_repo_does", f"The cloned repository implements core business workflows.")
    api_files_mapped = [f"`{f}`" for f in mapping.get("api_files", [])]
    entity_files_mapped = [f"`{f}`" for f in mapping.get("entity_files", [])]
    controllers_mapped = mapping.get("controllers_mapped", [])
    services_mapped = mapping.get("services_mapped", [])
    repos_mapped = mapping.get("repos_mapped", [])
    entity_names = [e.get("name", "") for e in (db_schema or {}).get("entities", [])[:20]]

    bl_mapping_md = f"""## 13. AI Codebase Mapping & Stakeholder Guide

This section explains how the cloned repository `{repo_name}` maps to the business architecture and technical sections in this report, serving as a structured guide for AI assistants (like Claude, Copilot, or ChatGPT) to explain the codebase's domain operations.

### Repository Purpose & Domain Map

Based on static codebase mapping and naming pattern heuristics:
- **Core Domain:** {bl_domain}
- **Detected User Roles:** {', '.join(bl_roles)}
- **Entity Count:** {len(entity_names)}
- **Mapped Codebase Entities:** {', '.join(f'`{e}`' for e in entity_names[:10]) or 'None detected'}

### How Codebase Files Map to Report Sections

AI engines and stakeholders can navigate the cloned codebase files to verify and dive deep into each section of the report using this mapping:

1. **Executive Summary & Business Logic (Sections 1 & 2):**
   - *Mapped Files:* Codebase files with naming structures of domain models or context files map directly to the system purpose and business terminology defined in these sections.
   - *Key Files:* {', '.join(entity_files_mapped[:5]) or 'Inferred from context classes'}

2. **System Block Diagram & Architecture (Section 4):**
   - *Mapped Files:* Controller and presenter files map to the API/Presentation layer, while service/manager files map to the Business Logic layer, and repository/DAO files map to the Data Access layer.
   - *Key Controller Files:* {', '.join(controllers_mapped[:3]) or 'N/A (inferred from endpoints)'}
   - *Key Service Files:* {', '.join(services_mapped[:3]) or 'N/A (inferred from codebase structure)'}
   - *Key Repository Files:* {', '.join(repos_mapped[:3]) or 'N/A (inferred from data access patterns)'}

3. **API Catalog & OpenAPI Specifications (Section 6):**
   - *Mapped Files:* Files containing routing attributes (e.g. `@GetMapping`, `[Route]`, annotations) map directly to our API path catalog.
   - *Key Files:* {', '.join(api_files_mapped[:5]) or 'No explicit endpoint files detected'}

4. **Data Architecture & Microservice Boundaries (Section 11):**
   - *Mapped Files:* ORM models, Fluent API configurations, and database contexts map directly to microservice database schema boundaries.
   - *Key Files:* {', '.join(entity_files_mapped[:5]) or 'Inferred from data layers'}
"""

    # Roles table
    bl_roles_md = "\n".join(f"- **{r}**" for r in bl_roles) or "_No roles detected_"

    # Business rules list
    bl_rules_md = "\n".join(f"- {rule}" for rule in bl_rules) or "_No business rules inferred_"

    # Workflows
    bl_workflows_md = ""
    for wf in bl_workflows:
        steps_md = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(wf.get("steps", [])))
        eps_md   = ", ".join(f"`{e}`" for e in wf.get("endpoints", [])) or "_N/A_"
        bl_workflows_md += (
            f"\n#### {wf.get('name', 'Workflow')}\n"
            f"{wf.get('description', '')}\n\n"
            f"**Steps:**\n{steps_md}\n\n"
            f"**Key endpoints:** {eps_md}\n"
        )
    if not bl_workflows_md:
        bl_workflows_md = "_No workflows inferred from API structure._"

    # Entity glossary table
    if bl_entities:
        bl_entity_rows = "\n".join(
            f"| `{e.get('entity','')}` | {e.get('business_meaning','')} | "
            f"{', '.join(e.get('key_operations', [])[:3])} |"
            for e in bl_entities
        )
        bl_entities_md = (
            "| Entity | Business Meaning | Key Operations |\n"
            "|--------|-----------------|----------------|\n"
            + bl_entity_rows
        )
    else:
        bl_entities_md = "_No entity definitions detected in analyzed files._"

    # Integrations
    bl_integrations_md = "\n".join(f"- `{i}`" for i in bl_integrations) or "_None detected_"

    # Fallback notice — now always False since heuristics IS the engine
    bl_notice = ""

    # ------------------------------------------------------------------
    # Risk assessment table rows
    # ------------------------------------------------------------------
    ext_dep_count = len(extract_external_deps(parsed))
    risk_rows = "\n".join([
        (
            f"| Technical Debt | "
            f"{'HIGH' if report['total_files'] > 50 else 'MEDIUM'} | "
            f"{report['total_files']} files with accumulated debt | "
            f"Systematic refactoring backlog |"
        ),
        (
            f"| Dead Code | "
            f"{'MEDIUM' if len(dead_code.get('dead_files', [])) > 5 else 'LOW'} | "
            f"{len(dead_code.get('dead_files', []))} unreferenced files | "
            f"Review and prune |"
        ),
        (
            f"| API Coverage | "
            f"{'HIGH' if not endpoints else 'LOW'} | "
            f"{len(endpoints)} endpoints documented | "
            f"Full OpenAPI spec required |"
        ),
        (
            f"| Dependencies | MEDIUM | "
            f"{ext_dep_count} external deps detected | "
            f"CVE audit recommended |"
        ),
    ])

    # ------------------------------------------------------------------
    # Block Diagram formatting
    # ------------------------------------------------------------------
    ascii_diagram = ""
    if isinstance(block_diagram, dict):
        ascii_diagram = render_ascii_block_diagram(block_diagram)
    else:
        ascii_diagram = "No visual diagram available."

    # ------------------------------------------------------------------
    # Assemble the full report
    # ------------------------------------------------------------------
    report_md = f"""# {repo_name} — Reverse Engineering Report

> **Auto-generated** by the Reverse Engineer Skill (API-key-free static analysis) · {now}
> Repository: [{repo_url}]({repo_url})
> Primary Language: **{primary.capitalize()}**
> Analysis Engine: **Pure static heuristics — no API keys required**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Logic & Functional Overview](#2-business-logic--functional-overview)
3. [Codebase Metrics](#3-codebase-metrics)
4. [Architecture Overview](#4-architecture-overview)
5. [Module Inventory](#5-module-inventory)
6. [API Catalog](#6-api-catalog)
7. [Dependency Analysis](#7-dependency-analysis)
8. [Dead Code Analysis](#8-dead-code-analysis)
9. [Tech Debt Inventory](#9-tech-debt-inventory)
10. [Modernization Roadmap](#10-modernization-roadmap)
11. [Data Architecture & Microservices Decomposition](#11-data-architecture--microservices-decomposition)
12. [Risk Assessment](#12-risk-assessment)

---

## 1. Executive Summary

{summary.get('purpose', '_AI summary not available. Set ANTHROPIC_API_KEY for richer analysis._')}

| Attribute | Value |
|-----------|-------|
| **Architecture Pattern** | {summary.get('architecture_pattern', 'Monolithic')} |
| **Modernization Priority** | {summary.get('modernization_priority', 'HIGH')} |
| **Platform** | {detect_platform(parsed)} |
| **Tech Stack** | {tech_stack_str} |
| **Total Files** | {report['total_files']} |
| **Total Classes** | {report['total_classes']} |
| **Total Methods** | {report['total_methods']} |

**Priority Reasoning:**
{summary.get('priority_reasoning', 'Full AI reasoning unavailable.')}

---

## 2. Business Logic & Functional Overview

> How this system works for its users — extracted from API endpoints, class names,
> ORM entity model, and AI analysis.
{bl_notice}
**Business Domain:** {bl_domain}

### What the System Does

{bl_what}

### Core Business Workflows
{bl_workflows_md}

### User Roles & Actors

{bl_roles_md}

### Key Business Rules

{bl_rules_md}

### Domain Entities in Business Terms

{bl_entities_md}

### Detected Integrations

{bl_integrations_md}

---

## 3. Codebase Metrics

### Language Distribution

| Language | Files | Share |
|----------|-------|-------|
{lang_rows}

### Key Counts

| Metric | Value |
|--------|-------|
| Files Analyzed | **{report['total_files']}** |
| Classes Defined | **{report['total_classes']}** |
| Methods & Functions | **{report['total_methods']}** |
| API Endpoints Extracted | **{len(endpoints)}** |
| Unreferenced Files | **{len(dead_code.get('dead_files', []))}** |
| Unreferenced Classes | **{len(dead_code.get('dead_classes', []))}** |
| External Dependencies | **{ext_dep_count}** |

---

## 4. Architecture Overview

**Pattern:** {summary.get('architecture_pattern', 'Monolithic')}

### Architectural Layers Detected

{chr(10).join(f'- {layer}' for layer in detect_architecture_layers(parsed)) or '- _No distinct layers inferred from file paths_'}

### System Block Diagram

![System Architecture Block Diagram]({repo_name}_block_diagram.svg)

<details>
<summary><b>Show ASCII/Unicode Text Block Diagram (Offline View)</b></summary>

```text
{ascii_diagram}
```
</details>

> The block diagram above shows the detected architectural layers — controllers,
> services, repositories, database entities, and external integrations — auto-generated
> from static class name analysis. No AI or API key required.

### Module Dependency Graph

![Module Dependency Graph]({repo_name}_dependency_graph.svg)

> The dependency graph above shows inter-module dependencies extracted from
> import/using statements. Standard library imports are excluded.

---

## 5. Module Inventory

_Showing first 40 of {report['total_files']} files._

{modules_md}

---

## 6. API Catalog

**Total Endpoints Extracted:** {len(endpoints)}

{api_table}

### OpenAPI 3.0 Specification

```json
{json.dumps(openapi_spec, indent=2)}
```

---

## 7. Dependency Analysis

### Top 10 Most Connected Modules

| Module | Outgoing References |
|--------|-------------------|
{top_deps_md or '| _No dependency data_ | — |'}

### External Dependencies Sample

```
{chr(10).join(extract_external_deps(parsed)[:30]) or 'No external dependencies detected'}
```

---

## 8. Dead Code Analysis

> Static analysis heuristic — results require manual validation before deletion.

### Potentially Unreferenced Files ({len(dead_code.get('dead_files', []))})

{dead_files_md}

### Potentially Unreferenced Classes ({len(dead_code.get('dead_classes', []))})

{dead_classes_md}

---

## 9. Tech Debt Inventory

{concerns_md}

### Key Tech Debt Areas

| Area | Severity | Details |
|------|----------|---------|
| Legacy Dependencies | HIGH | {ext_dep_count} external deps — audit for CVEs and outdated versions |
| Documentation | MEDIUM | Auto-generated docs; manual review required for accuracy |
| Test Coverage | UNKNOWN | Test suite metrics not assessed |
| Dead Code | {'MEDIUM' if len(dead_code.get('dead_files', [])) > 5 else 'LOW'} | {len(dead_code.get('dead_files', []))} unreferenced files identified |
| API Documentation | {'HIGH' if not endpoints else 'LOW'} | {'Full API documentation missing' if not endpoints else f'{len(endpoints)} endpoints documented'} |

---

## 10. Modernization Roadmap

### Target Technology Stack

{target_stack_str}

### Migration Phases

{phases_md}

### Proposed Microservice Boundaries

{microservices_md or '- _Microservice decomposition analysis pending_'}

### Risk Factors

{risk_factors_md}

**Estimated Total Effort:** {modernization.get('estimated_total_effort', 'N/A')}

---

## 11. Data Architecture & Microservices Decomposition

> Entity definitions extracted by static analysis. Results depend on which files were included
> in the 300-file analysis cap. For large repos, run against a focused subset for best results.

### Schema Summary

| Metric | Value |
|--------|-------|
| Entities Detected | **{(db_schema or {{}}).get('entity_count', 0)}** |
| Relationships Detected | **{(db_schema or {{}}).get('relationship_count', 0)}** |
| Bounded Contexts Identified | **{len(data_boundaries or [])}** |

{('### Detected Entities' + chr(10) + chr(10) + '| Entity | Table | Fields | Relationships |' + chr(10) + '|--------|-------|--------|---------------|' + chr(10) + chr(10).join('| `' + e.get('name','') + '` | `' + e.get('table','') + '` | ' + str(len(e.get('fields',[]))) + ' | ' + str(len(e.get('relationships',[]))) + ' |' for e in (db_schema or {{}}).get('entities', []))) if (db_schema or {{}}).get('entities') else '_No entity definitions detected in the analyzed files. Entity/model files may fall outside the 300-file cap._'}

### Proposed Microservice Data Boundaries

Each bounded context below represents a candidate microservice that should own
its own dedicated database (**Database-Per-Service** pattern).

{chr(10).join(('#### ' + b['name'] + chr(10) + ('Entities: ' + ', '.join('`' + e + '`' for e in b['entities']) if b['entities'] else '_From AI roadmap — no entity definitions in parsed files_') + chr(10)) for b in (data_boundaries or [])) or '_No data boundaries identified._'}

### Migration Guidance

When decomposing the monolithic database for microservices migration:

1. **Start with the loosest coupling** — identify entities with few cross-domain foreign keys.
2. **Introduce the Strangler Fig pattern** — new microservices own their tables, the monolith
   references them via API calls.
3. **Use the Outbox Pattern** for cross-service consistency — write events to an outbox table
   atomically, then publish via a message broker (e.g. RabbitMQ, Kafka).
4. **Avoid distributed transactions** — favour eventual consistency and compensating transactions.
5. **Data synchronisation phase** — run dual-write during transition; cut over once stable.

---

## 12. Risk Assessment

| Category | Severity | Description | Recommendation |
|----------|----------|-------------|----------------|
{risk_rows}

---

{bl_mapping_md}

---

## Appendix

### How This Report Was Generated

This report was produced by the **Reverse Engineer Skill** — a pure static analysis engine that:

1. Cloned the repository from GitHub
2. Walked all source files (`.py`, `.java`, `.cs`, `.ts`, `.js`, etc.)
3. Applied regex-based AST extraction to identify classes, methods, imports, and API routes
4. Built a dependency graph from import/using statements
5. Applied dead-code heuristics (unreferenced module detection)
6. Generated an OpenAPI 3.0 specification from routing annotations
7. Used static naming-convention heuristics to infer executive summary, business domain,
   modernisation roadmap, and architecture pattern — **no API keys or LLM accounts required**

> **To get AI-powered narrative on top of these results:**
> - **Claude Code**: Run `/reverse-engineer {repo_url}` — Claude reads the output and provides
>   AI explanation in chat.
> - **GitHub Copilot**: Use `.github/prompts/reverse-engineer.prompt.md` — Copilot reads the
>   SDD JSON and narrates the findings.
> - **Any other LLM**: Open this report or the `*_sdd.json` file and ask your AI assistant
>   to explain or enhance any section.

### Limitations

- Static analysis only — no runtime behaviour captured
- API extraction relies on common patterns (ASP.NET attributes, Spring annotations,
  Flask decorators, Express routes)
- Dead code detection is heuristic and may have false positives/negatives
- Business logic and domain labels inferred from naming conventions — review for accuracy

---

_Generated by Reverse Engineer Skill · Static Analysis Engine · {now}_
"""
    return report_md
