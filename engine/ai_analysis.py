"""
AI Analysis
===========
Calls the Anthropic Claude API to produce three AI-powered artefacts:

1. **Executive summary** — purpose, architecture pattern, tech-debt concerns,
   and modernisation priority.
2. **Modernisation roadmap** — phased migration plan, target stack,
   microservice boundaries, and risk factors.
3. **Business logic analysis** — what the system does for its end-users:
   business domain, core workflows, user roles, business rules, and a
   plain-English explanation of each data entity.

All three functions implement a graceful fallback: when the ``anthropic``
package is not installed, when ``ANTHROPIC_API_KEY`` is not set, or when the
API call fails for any reason, a deterministic heuristic result is returned
instead so that the pipeline always completes successfully.
"""

import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Low-level API helper
# ---------------------------------------------------------------------------

def claude_analyze(prompt, max_tokens=2000):
    """Call the Anthropic Claude API with *prompt* and return the response text.

    The function imports ``anthropic`` lazily so that the module can be loaded
    even when the package is not installed (the caller handles the ``None``
    fallback).

    Args:
        prompt (str): The user message to send to the model.
        max_tokens (int): Upper bound on response tokens.  Defaults to 2000.

    Returns:
        str | None: The model's text response, or ``None`` when the API is
        unavailable or the call fails.

    Raises:
        Nothing — all exceptions are caught and a warning is printed.
    """
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except ImportError:
        return None
    except Exception as e:
        print(f"  [WARN] Claude API call failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Executive summary
# ---------------------------------------------------------------------------

def ai_executive_summary(parsed, report, repo_name):
    """Generate an AI executive summary for the analysed repository.

    Sends a concise sample of the parsed codebase to Claude and asks for a
    structured JSON response.  If the API is unavailable or the response
    cannot be parsed as JSON, a deterministic fallback dict is returned.

    Args:
        parsed (list[dict]): List of file records from
            :func:`engine.parsers.parse_file`.
        report (dict): Metrics dict from
            :func:`engine.analyzer.generate_report`.
        repo_name (str): Human-readable repository name.

    Returns:
        dict: A dict with the following keys:

        - ``"purpose"`` (str): 2–3 sentence description of the system.
        - ``"architecture_pattern"`` (str): e.g. ``"MVC Monolith"``.
        - ``"tech_debt_concerns"`` (list[str]): Up to three concerns.
        - ``"modernization_priority"`` (str): ``"HIGH"``, ``"MEDIUM"``, or
          ``"LOW"``.
        - ``"priority_reasoning"`` (str): 1–2 sentence explanation.

    Note:
        The fallback result always sets ``"modernization_priority"`` to
        ``"HIGH"`` and includes a note directing the user to set
        ``ANTHROPIC_API_KEY`` for richer analysis.
    """
    sample = [
        {
            "file":    Path(r["file"]).name,
            "classes": r.get("classes", [])[:5],
            "methods": r.get("methods", [])[:5],
        }
        for r in parsed[:20]
    ]
    prompt = f"""You are a senior software architect performing a reverse engineering audit.

Repository: {repo_name}
Files: {report['total_files']}, Classes: {report['total_classes']}, Methods: {report['total_methods']}
Languages: {report['languages']}
Sample modules: {json.dumps(sample)}

Respond ONLY with a valid JSON object (no markdown fences) matching this schema exactly:
{{
  "purpose": "2-3 sentence description of what this system does",
  "architecture_pattern": "e.g. MVC Monolith / Layered N-Tier / Microservices / CQRS",
  "tech_debt_concerns": ["concern1", "concern2", "concern3"],
  "modernization_priority": "HIGH or MEDIUM or LOW",
  "priority_reasoning": "1-2 sentence explanation"
}}"""

    raw = claude_analyze(prompt, max_tokens=800)
    if raw:
        try:
            cleaned = re.sub(r'```(?:json)?', '', raw).strip()
            return json.loads(cleaned)
        except Exception:
            pass

    # Deterministic fallback when API is unavailable.
    primary = (
        max(report["languages"], key=report["languages"].get)
        if report["languages"]
        else "unknown"
    )
    return {
        "purpose": (
            f"{repo_name} is a legacy {primary} application with "
            f"{report['total_files']} source files, "
            f"{report['total_classes']} classes, and {report['total_methods']} methods. "
            "Full AI analysis unavailable — set ANTHROPIC_API_KEY for richer insights."
        ),
        "architecture_pattern": "Monolithic (inferred)",
        "tech_debt_concerns": [
            "Legacy dependencies detected",
            "Documentation gaps",
            "Test coverage unknown",
        ],
        "modernization_priority": "HIGH",
        "priority_reasoning": (
            "Legacy codebases typically require prioritised modernisation planning."
        ),
    }


# ---------------------------------------------------------------------------
# Modernisation roadmap
# ---------------------------------------------------------------------------

def ai_modernization_roadmap(parsed, report, repo_name, tech_stack):
    """Generate a phased modernisation roadmap for the repository.

    Sends codebase metadata and a sample of dependencies to Claude and asks
    for a structured JSON roadmap.  Falls back to a language-appropriate
    heuristic plan when the API is unavailable.

    Args:
        parsed (list[dict]): List of file records.
        report (dict): Metrics dict from
            :func:`engine.analyzer.generate_report`.
        repo_name (str): Human-readable repository name.
        tech_stack (list[str]): Detected technology labels from
            :func:`engine.analyzer.detect_tech_stack`.

    Returns:
        dict: A dict with the following keys:

        - ``"target_stack"`` (list[str]): Recommended target technologies.
        - ``"phases"`` (list[dict]): Each phase has ``"phase"``, ``"title"``,
          ``"duration"``, ``"tasks"``, and ``"risk"`` keys.
        - ``"microservices_boundaries"`` (list[str]): Proposed service names.
        - ``"estimated_total_effort"`` (str): e.g. ``"8-13 months"``.
        - ``"risk_factors"`` (list[str]): Key risks.

    Note:
        When the API is unavailable, the target stack is chosen from a
        hard-coded mapping of primary language to modern equivalents.
    """
    primary = (
        max(report["languages"], key=report["languages"].get)
        if report["languages"]
        else "unknown"
    )
    sample = [
        {"file": Path(r["file"]).name, "deps": r.get("dependencies", [])[:5]}
        for r in parsed[:15]
    ]
    prompt = f"""You are a modernization architect. Create a phased modernization roadmap for '{repo_name}'.

Primary language: {primary}
Tech stack detected: {tech_stack}
Codebase: {report['total_files']} files, {report['total_classes']} classes
Sample deps: {json.dumps(sample)}

Respond ONLY with a valid JSON object (no markdown fences):
{{
  "target_stack": ["recommended technology 1", "..."],
  "phases": [
    {{"phase": 1, "title": "Assessment & Audit", "duration": "1-2 months", "tasks": ["task1", "task2", "task3"], "risk": "LOW"}},
    {{"phase": 2, "title": "Foundation & Refactoring", "duration": "2-3 months", "tasks": ["task1", "task2", "task3"], "risk": "MEDIUM"}},
    {{"phase": 3, "title": "Migration & Modernization", "duration": "3-6 months", "tasks": ["task1", "task2", "task3"], "risk": "HIGH"}},
    {{"phase": 4, "title": "Validation & Launch", "duration": "1-2 months", "tasks": ["task1", "task2", "task3"], "risk": "MEDIUM"}}
  ],
  "microservices_boundaries": ["Service 1", "Service 2", "Service 3"],
  "estimated_total_effort": "6-12 months",
  "risk_factors": ["risk1", "risk2", "risk3"]
}}"""

    raw = claude_analyze(prompt, max_tokens=1200)
    if raw:
        try:
            cleaned = re.sub(r'```(?:json)?', '', raw).strip()
            return json.loads(cleaned)
        except Exception:
            pass

    # Deterministic fallback — language-appropriate target stack.
    lang_stack_map = {
        "dotnet":     ["ASP.NET Core 8", "Entity Framework Core", "Azure / AWS", "Docker", "Kubernetes"],
        "java":       ["Spring Boot 3", "Java 21", "Hibernate 6", "Kubernetes", "PostgreSQL"],
        "python":     ["FastAPI", "Python 3.12", "SQLAlchemy 2.0", "Docker", "Redis"],
        "javascript": ["Node.js 20 LTS", "TypeScript", "NestJS", "PostgreSQL", "Docker"],
        "typescript": ["Node.js 20 LTS", "TypeScript 5", "NestJS", "PostgreSQL", "Docker"],
    }
    return {
        "target_stack": lang_stack_map.get(
            primary, ["Modern cloud-native stack", "Docker", "Kubernetes"]
        ),
        "phases": [
            {
                "phase": 1,
                "title": "Assessment & Audit",
                "duration": "1-2 months",
                "tasks": ["Complete code audit", "Map all dependencies", "Identify critical paths"],
                "risk": "LOW",
            },
            {
                "phase": 2,
                "title": "Foundation & Refactoring",
                "duration": "2-3 months",
                "tasks": ["Introduce unit tests", "Refactor core modules", "Upgrade dependencies"],
                "risk": "MEDIUM",
            },
            {
                "phase": 3,
                "title": "Migration & Modernization",
                "duration": "3-6 months",
                "tasks": ["Migrate to modern framework", "Decompose monolith", "CI/CD pipeline"],
                "risk": "HIGH",
            },
            {
                "phase": 4,
                "title": "Validation & Launch",
                "duration": "1-2 months",
                "tasks": ["End-to-end testing", "Performance validation", "Production cutover"],
                "risk": "MEDIUM",
            },
        ],
        "microservices_boundaries": [
            "Core Domain Service",
            "API Gateway Service",
            "Auth & Identity Service",
        ],
        "estimated_total_effort": "8-13 months",
        "risk_factors": [
            "Breaking changes in major version upgrades",
            "Team retraining required",
            "Data migration complexity",
        ],
    }


# ---------------------------------------------------------------------------
# Business logic analysis
# ---------------------------------------------------------------------------

def ai_business_logic_analysis(parsed, endpoints, db_schema, report, repo_name):
    """Generate a plain-English business logic analysis of the analysed repository.

    Sends a curated payload — API endpoints, entity names, class names, and
    codebase metadata — to Claude and asks for a structured JSON response that
    explains *what the system does* for its end-users: the business domain,
    key workflows, user roles, business rules, and a plain-English gloss of
    each data entity.

    When the API is unavailable or the response cannot be parsed as JSON a
    deterministic heuristic result is returned instead so the pipeline always
    completes successfully.

    Args:
        parsed (list[dict]): List of file records from
            :func:`engine.parsers.parse_file`.
        endpoints (list[dict]): API endpoint records from
            :func:`engine.analyzer.extract_api_endpoints`.
        db_schema (dict): Database schema dict from
            :func:`engine.analyzer.detect_database_schema`.
        report (dict): Metrics dict from
            :func:`engine.analyzer.generate_report`.
        repo_name (str): Human-readable repository name.

    Returns:
        dict: A dict with the following keys:

        - ``"business_domain"`` (str): e.g. ``"E-Commerce / Online Retail"``.
        - ``"what_it_does"`` (str): 2–3 paragraph plain-English explanation of
          the system from the user's perspective.
        - ``"core_workflows"`` (list[dict]): Each workflow has ``"name"``,
          ``"description"``, ``"steps"`` (list[str]), and ``"endpoints"``
          (list[str]) keys.
        - ``"user_roles"`` (list[str]): Detected user/actor types.
        - ``"key_business_rules"`` (list[str]): Inferred rules the system
          enforces (e.g. ``"Orders require at least one item before checkout"``).
        - ``"data_entities_explained"`` (list[dict]): Each entry has
          ``"entity"``, ``"business_meaning"``, and ``"key_operations"`` keys.
        - ``"integrations"`` (list[str]): External service integrations
          detected (e.g. ``"Payment gateway"``, ``"Email / SMTP"``).
        - ``"fallback_used"`` (bool): ``True`` when heuristic fallback was used.

    Note:
        The fallback uses a keyword map over entity/class/endpoint names to
        infer domain, workflows, and roles without any API call.
    """
    # Collect curated context for the prompt.
    entity_names = [e.get("name", "") for e in (db_schema or {}).get("entities", [])[:20]]
    sample_classes = []
    for r in parsed[:30]:
        sample_classes.extend(r.get("classes", [])[:3])
    sample_classes = list(dict.fromkeys(sample_classes))[:25]  # dedup, cap 25

    ep_sample = [
        {"method": ep["methods"][0] if ep["methods"] else "GET", "path": ep["path"]}
        for ep in endpoints[:40]
    ]

    prompt = f"""You are a business analyst performing a reverse engineering audit of an existing software system.

Repository: {repo_name}
Primary language: {max(report['languages'], key=report['languages'].get) if report['languages'] else 'unknown'}
Classes detected: {sample_classes[:20]}
Data entities (ORM models): {entity_names}
API endpoints sample: {json.dumps(ep_sample[:30])}

Analyse the above artefacts and explain what this software system DOES from the perspective of its end-users and business stakeholders — NOT how it is implemented technically.

Respond ONLY with a valid JSON object (no markdown fences) matching this schema exactly:
{{
  "business_domain": "Short domain label e.g. E-Commerce / Online Retail",
  "what_it_does": "2-3 paragraph plain-English explanation of what the system does for its users",
  "core_workflows": [
    {{
      "name": "Workflow name e.g. Customer Checkout",
      "description": "One sentence description",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "endpoints": ["/api/example"]
    }}
  ],
  "user_roles": ["Role 1", "Role 2"],
  "key_business_rules": ["Rule 1", "Rule 2", "Rule 3"],
  "data_entities_explained": [
    {{
      "entity": "EntityName",
      "business_meaning": "Plain English: what this data represents",
      "key_operations": ["Create", "Read", "Update"]
    }}
  ],
  "integrations": ["Payment gateway", "Email / SMTP"]
}}"""

    raw = claude_analyze(prompt, max_tokens=2000)
    if raw:
        try:
            cleaned = re.sub(r'```(?:json)?', '', raw).strip()
            result = json.loads(cleaned)
            result["fallback_used"] = False
            return result
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Deterministic heuristic fallback
    # ------------------------------------------------------------------

    # 1. Domain detection — keyword map over entity names, class names,
    #    endpoint paths.
    all_names = " ".join(entity_names + sample_classes).lower()
    all_paths = " ".join(ep["path"] for ep in endpoints).lower()
    corpus = all_names + " " + all_paths

    _domain_keywords = {
        "E-Commerce / Online Retail":     ["product", "order", "cart", "checkout", "payment", "shipping", "invoice", "catalog", "sku", "basket"],
        "Healthcare / Medical":           ["patient", "doctor", "appointment", "diagnosis", "prescription", "clinic", "medical", "health", "physician"],
        "Banking / Financial Services":   ["account", "transaction", "balance", "loan", "credit", "debit", "ledger", "bank", "finance", "payment"],
        "Human Resources / HR":           ["employee", "payroll", "leave", "attendance", "department", "recruitment", "salary", "hr", "staff"],
        "Content Management / CMS":       ["article", "post", "content", "page", "media", "blog", "cms", "publish", "tag", "category"],
        "Education / Learning":           ["student", "course", "grade", "enrollment", "lesson", "instructor", "assignment", "quiz", "class"],
        "Project Management / Workflow":  ["project", "task", "sprint", "ticket", "issue", "milestone", "board", "kanban", "backlog"],
        "Logistics / Supply Chain":       ["shipment", "warehouse", "inventory", "supplier", "delivery", "freight", "stock", "dispatch"],
        "Real Estate / Property":         ["property", "listing", "tenant", "lease", "mortgage", "agent", "rent", "landlord"],
        "Social / Community Platform":    ["user", "post", "like", "comment", "follow", "feed", "profile", "message", "notification"],
    }

    business_domain = "General Business Application"
    best_score = 0
    for domain, keywords in _domain_keywords.items():
        score = sum(1 for kw in keywords if kw in corpus)
        if score > best_score:
            best_score = score
            business_domain = domain

    # 2. Workflow inference — group endpoints by first meaningful path segment.
    #    Skip generic prefixes like "api", "v1", "v2" etc.
    _skip_segments = {"api", "v1", "v2", "v3", "rest", "service", "services", "public", "private"}
    workflow_map: dict = {}
    for ep in endpoints[:60]:
        parts = [p for p in ep["path"].split("/") if p and not p.startswith("{")]
        # Find first non-generic segment
        meaningful = next((p for p in parts if p.lower() not in _skip_segments), parts[0] if parts else None)
        segment = meaningful.replace("-", " ").replace("_", " ").title() if meaningful else "General"
        if segment not in workflow_map:
            workflow_map[segment] = {"paths": [], "methods": set()}
        workflow_map[segment]["paths"].append(ep["path"])
        workflow_map[segment]["methods"].update(ep["methods"])

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

    # 3. User role detection — match entity/class names against role patterns.
    _role_patterns = ["user", "customer", "admin", "vendor", "supplier", "employee",
                      "manager", "staff", "guest", "member", "operator", "agent",
                      "teacher", "student", "doctor", "patient", "driver", "partner"]
    user_roles = []
    for pattern in _role_patterns:
        if pattern in corpus:
            user_roles.append(pattern.capitalize())
    if not user_roles:
        user_roles = ["End User", "Administrator"]
    user_roles = list(dict.fromkeys(user_roles))[:6]

    # 4. Business rules — infer from entity relationships and endpoint counts.
    key_business_rules = []
    for ent in (db_schema or {}).get("entities", [])[:8]:
        for rel in ent.get("relationships", [])[:2]:
            rel_type  = rel.get("type", "")
            target    = rel.get("target", "")
            src       = ent.get("name", "")
            if rel_type and target and src:
                key_business_rules.append(
                    f"{src} has a {rel_type} relationship with {target}."
                )
    if len(endpoints) > 0:
        key_business_rules.append(
            f"The system exposes {len(endpoints)} API endpoints enforcing data access rules."
        )
    if not key_business_rules:
        key_business_rules = [
            "Business rules enforced at the application layer (details require runtime analysis).",
            "Data validation applied before persistence.",
            "Access control required for sensitive operations.",
        ]
    key_business_rules = key_business_rules[:6]

    # 5. Entity explanations — plain-English gloss from name.
    _crud_ops = {
        "order": ["Place order", "View order history", "Cancel order", "Track status"],
        "product": ["Browse catalog", "View details", "Add to cart", "Manage inventory"],
        "user": ["Register", "Login", "Update profile", "Manage permissions"],
        "customer": ["Create account", "Place orders", "View history", "Manage addresses"],
        "invoice": ["Generate invoice", "View invoice", "Mark as paid", "Export PDF"],
        "payment": ["Process payment", "Refund", "View transactions", "Reconcile"],
        "cart": ["Add item", "Remove item", "View cart", "Proceed to checkout"],
        "shipment": ["Create shipment", "Track delivery", "Update status", "Return"],
        "category": ["Browse", "Filter products", "Create category", "Edit"],
        "employee": ["Onboard", "Manage details", "Assign role", "Deactivate"],
    }
    data_entities_explained = []
    for ent in entity_names[:10]:
        ent_lower = ent.lower()
        ops = next(
            (v for k, v in _crud_ops.items() if k in ent_lower),
            ["Create", "Read", "Update", "Delete"],
        )
        data_entities_explained.append({
            "entity": ent,
            "business_meaning": (
                f"Represents a {ent} record in the system, "
                "storing the attributes and state needed by business processes."
            ),
            "key_operations": ops,
        })

    # 6. Integration detection — scan dependency strings.
    all_deps = " ".join(
        dep for r in parsed for dep in r.get("dependencies", [])
    ).lower()
    _integration_keywords = {
        "Payment Gateway":        ["stripe", "paypal", "braintree", "adyen", "square", "payment"],
        "Email / SMTP":           ["mailkit", "sendgrid", "smtp", "mailgun", "email", "mailer"],
        "Message Broker":         ["rabbitmq", "kafka", "servicebus", "nservicebus", "masstransit", "bus"],
        "Cloud Storage":          ["azureblob", "s3", "awssdk", "blobstorage", "storage"],
        "Search Engine":          ["elasticsearch", "solr", "lucene", "algolia", "opensearch"],
        "Cache / Redis":          ["redis", "stackexchange", "memcached", "cache"],
        "Authentication":         ["oauth", "jwt", "identityserver", "keycloak", "auth0", "openid"],
        "Database ORM":           ["entityframework", "hibernate", "sqlalchemy", "dapper", "typeorm"],
        "Logging":                ["serilog", "nlog", "log4net", "winston", "loguru"],
        "Containerisation":       ["docker", "kubernetes", "helm", "container"],
    }
    integrations = []
    for integration, keywords in _integration_keywords.items():
        if any(kw in all_deps for kw in keywords):
            integrations.append(integration)
    if not integrations:
        integrations = ["Standard HTTP API", "Relational Database"]

    # 7. Plain-English "what it does" paragraph (heuristic).
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
        "For a richer, AI-generated explanation of the business logic, "
        "set the ANTHROPIC_API_KEY environment variable before running the skill."
    )

    return {
        "business_domain":        business_domain,
        "what_it_does":           what_it_does,
        "core_workflows":         core_workflows,
        "user_roles":             user_roles,
        "key_business_rules":     key_business_rules,
        "data_entities_explained": data_entities_explained,
        "integrations":           integrations,
        "fallback_used":          True,
    }
