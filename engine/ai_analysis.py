"""
AI Analysis  (API-Key-Free Edition)
====================================
Produces three structured artefacts using **pure static heuristics** —
no LLM API calls, no API keys, no internet access required.

All analysis is derived entirely from the parsed codebase:
  - Language distribution, class/method names, import statements
  - ORM entity models, relationships, and field definitions
  - Detected API endpoints, HTTP methods, and route patterns
  - File naming conventions and directory structure

The three functions mirror the same return schema as the original
AI-powered versions so the rest of the pipeline is unchanged.

When running inside **Claude Code** or **GitHub Copilot**, the AI
assistant itself can read the generated ``*_sdd.json`` and
``*_report.md`` files and provide AI-quality narrative in the chat
without requiring any API key in the Python environment.
"""

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Executive summary
# ---------------------------------------------------------------------------

def ai_executive_summary(parsed, report, repo_name):
    """Generate a deterministic executive summary from static analysis.

    Analyses language distribution, class/method counts, and naming
    conventions to produce a structured summary dict without any API calls.

    Args:
        parsed (list[dict]): List of file records from parse_file().
        report (dict): Metrics dict from generate_report().
        repo_name (str): Human-readable repository name.

    Returns:
        dict: Keys: purpose, architecture_pattern, tech_debt_concerns,
              modernization_priority, priority_reasoning.
    """
    primary = (
        max(report["languages"], key=report["languages"].get)
        if report["languages"]
        else "unknown"
    )

    # Infer architecture pattern from file naming conventions
    all_names = " ".join(
        name.lower()
        for r in parsed
        for name in r.get("classes", [])
    )
    all_paths = " ".join(r.get("file", "").replace("\\", "/").lower() for r in parsed)
    corpus = all_names + " " + all_paths

    if any(k in corpus for k in ["controller", "mvc", "view", "model"]):
        pattern = "MVC Monolith"
    elif any(k in corpus for k in ["service", "repository", "dao"]):
        pattern = "Layered N-Tier (Service / Repository)"
    elif any(k in corpus for k in ["handler", "command", "query", "cqrs"]):
        pattern = "CQRS / Command-Query Separation"
    elif any(k in corpus for k in ["lambda", "function", "serverless"]):
        pattern = "Serverless / Function-as-a-Service"
    else:
        pattern = "Monolithic Application"

    # Tech debt concerns based on measurable signals
    concerns = []
    ext_count = len({
        dep for r in parsed for dep in r.get("dependencies", [])
        if dep and not dep.startswith(".")
    })
    if ext_count > 30:
        concerns.append(f"High external dependency count ({ext_count} packages) — audit for CVEs")
    elif ext_count > 10:
        concerns.append(f"Moderate dependency footprint ({ext_count} packages) — review for outdated versions")

    dead_signal = sum(1 for r in parsed if not r.get("classes") and not r.get("routes"))
    if dead_signal > len(parsed) * 0.2:
        concerns.append(f"{dead_signal} files have no classes or routes — potential dead code")

    total_methods = report.get("total_methods", 0)
    total_classes = report.get("total_classes", 1) or 1
    avg_methods = total_methods / total_classes
    if avg_methods > 15:
        concerns.append(f"High average methods-per-class ({avg_methods:.0f}) — consider splitting large classes")
    elif avg_methods < 2 and total_classes > 10:
        concerns.append("Many thin classes — consider consolidating related logic")

    if not concerns:
        concerns = [
            "Documentation coverage not measurable via static analysis",
            "Test suite metrics not assessed — recommend coverage tooling",
            "Dependency versions not validated — run a CVE audit",
        ]
    concerns = concerns[:3]

    # Priority based on size and complexity
    total_files = report.get("total_files", 0)
    if total_files > 200 or avg_methods > 20:
        priority = "HIGH"
        reasoning = (
            f"The codebase has {total_files} source files and an average of "
            f"{avg_methods:.0f} methods per class, indicating significant complexity "
            "that warrants prioritised modernisation planning."
        )
    elif total_files > 50:
        priority = "MEDIUM"
        reasoning = (
            f"With {total_files} source files the codebase is mid-sized. "
            "Targeted refactoring of high-complexity modules is recommended."
        )
    else:
        priority = "LOW"
        reasoning = (
            f"The repository has {total_files} source files — a manageable scope "
            "for incremental improvement without a full rewrite."
        )

    # Purpose derived from repo name + detected domain signals
    domain_hints = _detect_domain_label(parsed)
    purpose = (
        f"{repo_name} is a {primary.capitalize()} application in the "
        f"{domain_hints} domain. "
        f"The codebase contains {report['total_files']} source files, "
        f"{report['total_classes']} classes, and {report['total_methods']} methods "
        f"following a {pattern} architecture."
    )

    return {
        "purpose": purpose,
        "architecture_pattern": pattern,
        "tech_debt_concerns": concerns,
        "modernization_priority": priority,
        "priority_reasoning": reasoning,
    }


# ---------------------------------------------------------------------------
# Modernisation roadmap
# ---------------------------------------------------------------------------

def ai_modernization_roadmap(parsed, report, repo_name, tech_stack):
    """Generate a phased modernisation roadmap from static analysis heuristics.

    Target stack is derived from the detected primary language.

    Args:
        parsed (list[dict]): List of file records.
        report (dict): Metrics dict from generate_report().
        repo_name (str): Human-readable repository name.
        tech_stack (list[str]): Detected technology labels.

    Returns:
        dict: Keys: target_stack, phases, microservices_boundaries,
              estimated_total_effort, risk_factors.
    """
    primary = (
        max(report["languages"], key=report["languages"].get)
        if report["languages"]
        else "unknown"
    )

    lang_stack_map = {
        "dotnet":     ["ASP.NET Core 8", "Entity Framework Core", "Azure / AWS", "Docker", "Kubernetes"],
        "java":       ["Spring Boot 3", "Java 21", "Hibernate 6", "Kubernetes", "PostgreSQL"],
        "python":     ["FastAPI", "Python 3.12", "SQLAlchemy 2.0", "Docker", "Redis"],
        "javascript": ["Node.js 20 LTS", "TypeScript", "NestJS", "PostgreSQL", "Docker"],
        "typescript": ["Node.js 20 LTS", "TypeScript 5", "NestJS", "PostgreSQL", "Docker"],
    }
    target_stack = lang_stack_map.get(primary, ["Modern cloud-native stack", "Docker", "Kubernetes"])

    # Estimate effort from size
    total_files = report.get("total_files", 0)
    if total_files > 300:
        effort = "12-18 months"
        phases_detail = [
            {"phase": 1, "title": "Assessment & Audit",        "duration": "2-3 months", "risk": "LOW",    "tasks": ["Full code audit", "Map all dependencies", "Document critical paths"]},
            {"phase": 2, "title": "Foundation & Refactoring",  "duration": "3-4 months", "risk": "MEDIUM", "tasks": ["Introduce unit tests", "Refactor core modules", "Upgrade all dependencies"]},
            {"phase": 3, "title": "Migration & Modernization", "duration": "5-8 months", "risk": "HIGH",   "tasks": ["Migrate to target framework", "Decompose monolith into services", "Set up CI/CD pipeline"]},
            {"phase": 4, "title": "Validation & Launch",       "duration": "2-3 months", "risk": "MEDIUM", "tasks": ["End-to-end testing", "Performance benchmarking", "Production cutover & rollback plan"]},
        ]
    elif total_files > 100:
        effort = "8-13 months"
        phases_detail = [
            {"phase": 1, "title": "Assessment & Audit",        "duration": "1-2 months", "risk": "LOW",    "tasks": ["Complete code audit", "Map all dependencies", "Identify critical paths"]},
            {"phase": 2, "title": "Foundation & Refactoring",  "duration": "2-3 months", "risk": "MEDIUM", "tasks": ["Introduce unit tests", "Refactor core modules", "Upgrade dependencies"]},
            {"phase": 3, "title": "Migration & Modernization", "duration": "3-6 months", "risk": "HIGH",   "tasks": ["Migrate to modern framework", "Decompose monolith", "CI/CD pipeline"]},
            {"phase": 4, "title": "Validation & Launch",       "duration": "1-2 months", "risk": "MEDIUM", "tasks": ["End-to-end testing", "Performance validation", "Production cutover"]},
        ]
    else:
        effort = "4-8 months"
        phases_detail = [
            {"phase": 1, "title": "Assessment & Quick Wins",   "duration": "1 month",   "risk": "LOW",    "tasks": ["Code review", "Identify easy refactors", "Set up linting and CI"]},
            {"phase": 2, "title": "Incremental Modernization", "duration": "2-4 months","risk": "MEDIUM", "tasks": ["Upgrade dependencies", "Add test coverage", "Refactor hotspots"]},
            {"phase": 3, "title": "Cloud & Container Readiness","duration": "1-2 months","risk": "LOW",   "tasks": ["Dockerize application", "Add health checks", "Set up monitoring"]},
            {"phase": 4, "title": "Final Validation",          "duration": "1 month",   "risk": "LOW",   "tasks": ["Full regression tests", "Performance validation", "Go-live"]},
        ]

    # Risk factors from detected signals
    risk_factors = []
    all_deps = " ".join(dep for r in parsed for dep in r.get("dependencies", [])).lower()
    if any(k in all_deps for k in ["hibernate", "entityframework", "sqlalchemy"]):
        risk_factors.append("ORM migration complexity — data schema changes require careful sequencing")
    if total_files > 150:
        risk_factors.append(f"Large codebase ({total_files} files) — higher risk of undocumented dependencies")
    risk_factors.append("Team retraining required for new framework/toolchain")
    if len(tech_stack) > 5:
        risk_factors.append(f"High technology diversity ({len(tech_stack)} detected technologies) — consolidation needed")
    risk_factors = risk_factors[:4]

    # Microservice boundaries from detected layers
    boundaries = []
    all_names_lower = " ".join(
        c.lower() for r in parsed for c in r.get("classes", [])
    )
    boundary_keywords = {
        "User & Identity Service":    ["user", "auth", "account", "identity", "login", "register"],
        "Product & Catalog Service":  ["product", "catalog", "category", "sku", "inventory"],
        "Order & Payment Service":    ["order", "payment", "invoice", "cart", "checkout"],
        "Notification Service":       ["email", "sms", "notification", "mailer", "message"],
        "Reporting & Analytics":      ["report", "analytics", "dashboard", "metric", "log"],
        "Core Domain Service":        ["service", "manager", "handler", "processor"],
        "API Gateway":                ["gateway", "router", "proxy", "middleware"],
    }
    for svc, keywords in boundary_keywords.items():
        if any(k in all_names_lower for k in keywords):
            boundaries.append(svc)
    if not boundaries:
        boundaries = ["Core Domain Service", "API Gateway Service", "Auth & Identity Service"]
    boundaries = boundaries[:5]

    return {
        "target_stack": target_stack,
        "phases": phases_detail,
        "microservices_boundaries": boundaries,
        "estimated_total_effort": effort,
        "risk_factors": risk_factors,
    }


# ---------------------------------------------------------------------------
# Business logic analysis
# ---------------------------------------------------------------------------

def ai_business_logic_analysis(parsed, endpoints, db_schema, report, repo_name):
    """Generate a business logic analysis using static heuristics only.

    Infers domain, workflows, roles, rules, and entity meanings from
    entity names, class names, API endpoint paths, and dependency strings.

    Args:
        parsed (list[dict]): List of file records.
        endpoints (list[dict]): API endpoint records.
        db_schema (dict): Database schema dict.
        report (dict): Metrics dict from generate_report().
        repo_name (str): Human-readable repository name.

    Returns:
        dict: Keys: business_domain, what_it_does, core_workflows,
              user_roles, key_business_rules, data_entities_explained,
              integrations, fallback_used.
    """
    entity_names = [e.get("name", "") for e in (db_schema or {}).get("entities", [])[:20]]
    sample_classes = []
    for r in parsed[:30]:
        sample_classes.extend(r.get("classes", [])[:3])
    sample_classes = list(dict.fromkeys(sample_classes))[:25]

    all_names = " ".join(entity_names + sample_classes).lower()
    all_paths = " ".join(ep.get("path", "") for ep in endpoints).lower()
    corpus = all_names + " " + all_paths

    # 1. Domain detection
    business_domain = _detect_domain_label(parsed)

    # 2. Workflow inference from endpoint paths
    _skip_segments = {"api", "v1", "v2", "v3", "rest", "service", "services", "public", "private"}
    workflow_map: dict = {}
    for ep in endpoints[:60]:
        parts = [p for p in ep.get("path", "").split("/") if p and not p.startswith("{")]
        meaningful = next((p for p in parts if p.lower() not in _skip_segments), parts[0] if parts else None)
        segment = meaningful.replace("-", " ").replace("_", " ").title() if meaningful else "General"
        if segment not in workflow_map:
            workflow_map[segment] = {"paths": [], "methods": set()}
        workflow_map[segment]["paths"].append(ep.get("path", ""))
        workflow_map[segment]["methods"].update(ep.get("methods", []))

    core_workflows = []
    for name, data in list(workflow_map.items())[:5]:
        verbs = ", ".join(sorted(data["methods"]))
        core_workflows.append({
            "name": f"{name} Management",
            "description": f"Handles {name.lower()}-related operations ({verbs}).",
            "steps": [
                f"Client sends request to {data['paths'][0]}",
                "System validates input and applies business rules",
                "Response returned with updated state",
            ],
            "endpoints": data["paths"][:4],
        })
    if not core_workflows:
        core_workflows = [{
            "name": "Core Business Operation",
            "description": "Primary system workflow (API routes not detected via static analysis).",
            "steps": ["User authenticates", "User performs core action", "System records result"],
            "endpoints": [],
        }]

    # 3. User role detection
    _role_patterns = ["user", "customer", "admin", "vendor", "supplier", "employee",
                      "manager", "staff", "guest", "member", "operator", "agent",
                      "teacher", "student", "doctor", "patient", "driver", "partner"]
    user_roles = [p.capitalize() for p in _role_patterns if p in corpus]
    if not user_roles:
        user_roles = ["End User", "Administrator"]
    user_roles = list(dict.fromkeys(user_roles))[:6]

    # 4. Business rules from entity relationships + endpoint count
    key_business_rules = []
    for ent in (db_schema or {}).get("entities", [])[:8]:
        for rel in ent.get("relationships", [])[:2]:
            rel_type = rel.get("type", "")
            target   = rel.get("target", "")
            src      = ent.get("name", "")
            if rel_type and target and src:
                key_business_rules.append(f"{src} has a {rel_type} relationship with {target}.")
    if endpoints:
        key_business_rules.append(
            f"The system exposes {len(endpoints)} API endpoints enforcing structured data access."
        )
    if not key_business_rules:
        key_business_rules = [
            "Business rules enforced at the application layer.",
            "Data validation applied before persistence.",
            "Access control required for sensitive operations.",
        ]
    key_business_rules = key_business_rules[:6]

    # 5. Entity explanations
    _crud_ops = {
        "order":    ["Place order", "View order history", "Cancel order", "Track status"],
        "product":  ["Browse catalog", "View details", "Add to cart", "Manage inventory"],
        "user":     ["Register", "Login", "Update profile", "Manage permissions"],
        "customer": ["Create account", "Place orders", "View history", "Manage addresses"],
        "invoice":  ["Generate invoice", "View invoice", "Mark as paid", "Export PDF"],
        "payment":  ["Process payment", "Refund", "View transactions", "Reconcile"],
        "cart":     ["Add item", "Remove item", "View cart", "Proceed to checkout"],
        "shipment": ["Create shipment", "Track delivery", "Update status", "Return"],
        "category": ["Browse", "Filter products", "Create category", "Edit"],
        "employee": ["Onboard", "Manage details", "Assign role", "Deactivate"],
    }
    data_entities_explained = []
    for ent in entity_names[:10]:
        ent_lower = ent.lower()
        ops = next((v for k, v in _crud_ops.items() if k in ent_lower), ["Create", "Read", "Update", "Delete"])
        data_entities_explained.append({
            "entity": ent,
            "business_meaning": (
                f"Represents a {ent} record in the system, "
                "storing attributes and state required by business processes."
            ),
            "key_operations": ops,
        })

    # 6. Integration detection
    all_deps = " ".join(dep for r in parsed for dep in r.get("dependencies", [])).lower()
    _integration_keywords = {
        "Payment Gateway":  ["stripe", "paypal", "braintree", "adyen", "square", "payment"],
        "Email / SMTP":     ["mailkit", "sendgrid", "smtp", "mailgun", "email", "mailer"],
        "Message Broker":   ["rabbitmq", "kafka", "servicebus", "nservicebus", "masstransit"],
        "Cloud Storage":    ["azureblob", "s3", "awssdk", "blobstorage", "storage"],
        "Search Engine":    ["elasticsearch", "solr", "algolia", "opensearch"],
        "Cache / Redis":    ["redis", "stackexchange", "memcached", "cache"],
        "Authentication":   ["oauth", "jwt", "identityserver", "keycloak", "auth0", "openid"],
        "Database ORM":     ["entityframework", "hibernate", "sqlalchemy", "dapper", "typeorm"],
        "Logging":          ["serilog", "nlog", "log4net", "winston", "loguru"],
        "Containerisation": ["docker", "kubernetes", "helm"],
    }
    integrations = [
        integration for integration, keywords in _integration_keywords.items()
        if any(kw in all_deps for kw in keywords)
    ]
    if not integrations:
        integrations = ["Standard HTTP API", "Relational Database"]

    # 7. Plain-English summary
    primary_lang = (
        max(report["languages"], key=report["languages"].get)
        if report["languages"]
        else "software"
    )
    what_it_does = (
        f"{repo_name} is a {primary_lang.capitalize()} application operating in the "
        f"**{business_domain}** domain. "
        f"It serves {len(user_roles)} identified user role(s) — "
        f"{', '.join(user_roles)} — through {len(endpoints)} API endpoint(s) "
        f"backed by {len(entity_names)} data entity/entities.\n\n"
        f"The system manages core business data across {len(entity_names)} entities "
        f"and exposes its functionality via a structured API. "
        f"Key integrations detected include: {', '.join(integrations)}.\n\n"
        "This analysis was produced entirely from static code analysis — no AI API "
        "calls are made. For AI-powered narrative, open the generated report in "
        "Claude Code or GitHub Copilot and ask it to enhance the executive summary "
        "and business logic sections."
    )

    # 8. AI Codebase-to-Section Mapping
    # Identify which files/folders map to which logical sections of the report based on heuristics
    api_files = list(dict.fromkeys(ep.get("file", "") for ep in endpoints if ep.get("file")))[:10]
    entity_files = list(dict.fromkeys(ent.get("file", "") for ent in (db_schema or {}).get("entities", []) if ent.get("file")))[:10]
    
    # Classify controllers, services, repositories in the codebase for explicit mapping
    controllers_mapped = []
    services_mapped = []
    repos_mapped = []
    for item in parsed[:100]:
        filename = Path(item.get("file", "")).name
        for cls in item.get("classes", []):
            lower_cls = cls.lower()
            if any(k in lower_cls for k in ("controller", "handler", "router", "endpoint")):
                controllers_mapped.append(f"`{filename}` ({cls})")
            elif any(k in lower_cls for k in ("service", "manager", "usecase", "facade", "workflow")):
                services_mapped.append(f"`{filename}` ({cls})")
            elif any(k in lower_cls for k in ("repository", "repo", "dao", "store", "gateway", "adapter")):
                repos_mapped.append(f"`{filename}` ({cls})")
                
    controllers_mapped = list(dict.fromkeys(controllers_mapped))[:6]
    services_mapped = list(dict.fromkeys(services_mapped))[:6]
    repos_mapped = list(dict.fromkeys(repos_mapped))[:6]

    ai_codebase_mapping = {
        "what_the_repo_does": (
            f"The cloned repository `{repo_name}` is a software system implementing "
            f"core workflows in the **{business_domain}** domain. It is structured to process "
            f"business requests through the Presentation/API layer, orchestrate workflows via "
            f"logical services, and persist state using data repositories."
        ),
        "api_files": [Path(f).name for f in api_files],
        "entity_files": [Path(f).name for f in entity_files],
        "controllers_mapped": controllers_mapped,
        "services_mapped": services_mapped,
        "repos_mapped": repos_mapped,
    }

    return {
        "business_domain":          business_domain,
        "what_it_does":             what_it_does,
        "core_workflows":           core_workflows,
        "user_roles":               user_roles,
        "key_business_rules":       key_business_rules,
        "data_entities_explained":  data_entities_explained,
        "integrations":             integrations,
        "fallback_used":            False,   # not a "fallback" — this IS the engine
        "ai_codebase_mapping":      ai_codebase_mapping,
    }


# ---------------------------------------------------------------------------
# Shared domain-detection helper
# ---------------------------------------------------------------------------

def _detect_domain_label(parsed):
    """Infer the business domain from entity/class names and import strings.

    Args:
        parsed (list[dict]): Parsed file records.

    Returns:
        str: Domain label e.g. 'E-Commerce / Online Retail'.
    """
    all_names = " ".join(
        c.lower()
        for r in parsed
        for c in r.get("classes", []) + r.get("dependencies", [])
    )

    _domain_keywords = {
        "E-Commerce / Online Retail":    ["product", "order", "cart", "checkout", "payment", "shipping", "invoice", "catalog", "sku", "basket"],
        "Healthcare / Medical":          ["patient", "doctor", "appointment", "diagnosis", "prescription", "clinic", "medical", "health"],
        "Banking / Financial Services":  ["account", "transaction", "balance", "loan", "credit", "debit", "ledger", "finance"],
        "Human Resources / HR":          ["employee", "payroll", "leave", "attendance", "department", "recruitment", "salary"],
        "Content Management / CMS":      ["article", "post", "content", "page", "media", "blog", "publish", "tag", "category"],
        "Education / Learning":          ["student", "course", "grade", "enrollment", "lesson", "instructor", "assignment", "quiz"],
        "Project Management / Workflow": ["project", "task", "sprint", "ticket", "issue", "milestone", "board", "kanban"],
        "Logistics / Supply Chain":      ["shipment", "warehouse", "inventory", "supplier", "delivery", "freight", "stock"],
        "Real Estate / Property":        ["property", "listing", "tenant", "lease", "mortgage", "agent", "rent"],
        "Social / Community Platform":   ["user", "post", "like", "comment", "follow", "feed", "profile", "notification"],
    }

    best_domain = "General Business Application"
    best_score = 0
    for domain, keywords in _domain_keywords.items():
        score = sum(1 for kw in keywords if kw in all_names)
        if score > best_score:
            best_score = score
            best_domain = domain
    return best_domain
