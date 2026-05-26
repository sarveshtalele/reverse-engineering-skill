"""
Analysis Engine
===============
Derives high-level architectural insights from the list of parsed file
records produced by :mod:`engine.parsers`.

Functions in this module operate purely on in-memory data structures — no
filesystem access occurs here (except for ``detect_tech_stack``, which
inspects known config-file locations relative to the repository root).

Typical call order inside the pipeline:

1. :func:`generate_report` — aggregate totals
2. :func:`build_dependency_map` — module-level dependency graph
3. :func:`generate_mermaid` — Mermaid diagram string
4. :func:`extract_api_endpoints` — flat list of routes
5. :func:`generate_openapi_spec` — OpenAPI 3.0 spec dict
6. :func:`detect_dead_code` — unreferenced files and classes
7. :func:`detect_tech_stack` — frameworks and tooling
8. :func:`detect_platform` — runtime platform
9. :func:`detect_architecture_layers` — N-tier layer labels
10. :func:`find_top_modules` — most-connected modules
11. :func:`extract_external_deps` — sorted external dependency list
"""

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Metrics aggregation
# ---------------------------------------------------------------------------

def generate_report(parsed):
    """Aggregate top-level codebase metrics from all parsed records.

    Args:
        parsed (list[dict]): List of file records as returned by
            :func:`engine.parsers.parse_file`.

    Returns:
        dict: A metrics dict with the following keys:

        - ``"total_files"`` (int): Number of parsed files.
        - ``"languages"`` (dict[str, int]): File count per language.
        - ``"total_classes"`` (int): Sum of classes across all files.
        - ``"total_methods"`` (int): Sum of methods/functions across all
          files.
    """
    report = {
        "total_files": len(parsed),
        "languages": {},
        "total_classes": 0,
        "total_methods": 0,
    }
    for item in parsed:
        lang = item.get("language", "unknown")
        report["languages"][lang] = report["languages"].get(lang, 0) + 1
        report["total_classes"]  += len(item.get("classes", []))
        report["total_methods"]  += len(item.get("methods", []))
    return report


# ---------------------------------------------------------------------------
# Dependency graph
# ---------------------------------------------------------------------------

def build_dependency_map(parsed):
    """Build a module-to-dependencies mapping from parsed records.

    Each module is identified by its filename stem (without extension or
    directory path).  Its value is the set of dependency identifiers
    extracted from ``import`` / ``using`` / ``require`` statements.

    Args:
        parsed (list[dict]): List of file records.

    Returns:
        dict[str, set[str]]: Mapping of ``{module_stem: {dep, …}}``.
    """
    dep_map = {}
    for item in parsed:
        name = Path(item["file"]).stem
        dep_map[name] = set(dep.strip() for dep in item.get("dependencies", []))
    return dep_map


def generate_mermaid(parsed, max_links=80):
    """Generate a Mermaid ``graph TD`` diagram of inter-module dependencies.

    Standard library / framework root packages are ignored to keep the graph
    readable.  Node identifiers are sanitised to contain only alphanumeric
    characters and underscores.

    Args:
        parsed (list[dict]): List of file records.
        max_links (int): Maximum number of edges to emit.  Defaults to 80.

    Returns:
        str: A Mermaid ``graph TD`` diagram as a multi-line string, suitable
        for embedding in a ``<pre class="mermaid">`` block or a fenced
        Markdown code block.
    """
    IGNORE = {
        "java", "javax", "org", "com", "System", "Microsoft", "Newtonsoft",
        "os", "sys", "re", "json", "typing", "collections", "datetime", "math",
        "time", "subprocess", "ast", "pathlib", "abc", "enum", "functools",
        "react", "lodash", "express", "next", "angular", "vue",
    }
    lines = ["graph TD"]
    seen, count = set(), 0
    for item in parsed:
        if count >= max_links:
            break
        src = re.sub(r'[^a-zA-Z0-9_]', '_', Path(item["file"]).stem)
        for dep in item.get("dependencies", []):
            root = dep.split(".")[0]
            if root in IGNORE or not root:
                continue
            tgt = re.sub(r'[^a-zA-Z0-9_]', '_', dep.replace(".", "_"))
            if src == tgt or (src, tgt) in seen:
                continue
            seen.add((src, tgt))
            lines.append(f"    {src} --> {tgt}")
            count += 1
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# API extraction
# ---------------------------------------------------------------------------

def extract_api_endpoints(parsed):
    """Flatten all route records from parsed files into a single endpoint list.

    Args:
        parsed (list[dict]): List of file records, each potentially
            containing a ``"routes"`` list.

    Returns:
        list[dict]: Each element has the following keys:

        - ``"file"`` (str): Source file path.
        - ``"class"`` (str | None): Containing class name.
        - ``"method"`` (str | None): Handler method name.
        - ``"path"`` (str): HTTP path (e.g. ``"/api/orders/{id}"``).
        - ``"methods"`` (list[str]): HTTP verbs (e.g. ``["GET"]``).
    """
    endpoints = []
    for item in parsed:
        for r in item.get("routes", []):
            endpoints.append({
                "file":    item["file"],
                "class":   r.get("class"),
                "method":  r.get("method"),
                "path":    r.get("path", "/"),
                "methods": r.get("methods", ["GET"]),
            })
    return endpoints


def generate_openapi_spec(endpoints, repo_name):
    """Build an OpenAPI 3.0 specification dict from extracted endpoints.

    Path parameters are normalised from ``<name>`` (Python/Flask style) to
    ``{name}`` (OpenAPI style).  When no endpoints are found a minimal health
    check path is inserted so the spec remains valid.

    Args:
        endpoints (list[dict]): Endpoint records as returned by
            :func:`extract_api_endpoints`.
        repo_name (str): Repository name used in the spec ``info`` block.

    Returns:
        dict: An OpenAPI 3.0 specification suitable for serialisation to JSON
        or YAML.
    """
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": f"{repo_name} API",
            "version": "1.0.0",
            "description": f"Auto-extracted OpenAPI 3.0 spec from {repo_name}",
        },
        "paths": {},
    }
    for ep in endpoints:
        path = ep["path"]
        if not path.startswith("/"):
            path = "/" + path
        path = path.replace("<", "{").replace(">", "}")
        if path not in spec["paths"]:
            spec["paths"][path] = {}
        for verb in ep["methods"]:
            spec["paths"][path][verb.lower()] = {
                "summary": f"{ep.get('class') or 'global'}.{ep.get('method') or 'handler'}()",
                "description": f"Defined in `{Path(ep['file']).name}`",
                "responses": {"200": {"description": "Success"}},
            }
    if not spec["paths"]:
        spec["paths"]["/health"] = {
            "get": {"summary": "Health check", "responses": {"200": {"description": "OK"}}}
        }
    return spec


# ---------------------------------------------------------------------------
# Dead code detection
# ---------------------------------------------------------------------------

def detect_dead_code(parsed):
    """Heuristically identify unreferenced files and classes.

    A file is considered potentially dead when:
    - Its stem does not appear in any other file's imports/dependencies.
    - None of the classes it defines are referenced by other files.
    - Its name does not contain a well-known entry-point term (``main``,
      ``app``, ``index``, etc.).

    A class is considered potentially dead when its name does not appear in
    any file's import/dependency list and it is not a known entry-point class.

    Args:
        parsed (list[dict]): List of file records.

    Returns:
        dict: A report dict with the following keys:

        - ``"dead_files"`` (list[str]): Absolute paths of potentially
          unreferenced files.
        - ``"dead_classes"`` (list[dict]): Each element has ``"class"`` and
          ``"file"`` keys.

    Note:
        This is a heuristic — dynamic imports, reflection, and unconventional
        naming conventions can produce false positives.  Results should be
        manually reviewed before any code is removed.
    """
    all_refs = set()
    classes_defined = {}
    for item in parsed:
        for dep in item.get("imports", []) + item.get("dependencies", []):
            all_refs.add(dep)
            for part in dep.split("."):
                all_refs.add(part)
        for cls in item.get("classes", []):
            classes_defined[cls] = item["file"]

    entry_terms   = {"main", "setup", "app", "build", "index", "program", "startup", "run", "init"}
    skip_classes  = {"Program", "Startup", "App", "Main", "Application", "Index", "Bootstrap"}

    # For .NET/Java, files are referenced by convention (MVC routing, DI
    # containers, annotation scanning) rather than explicit import statements.
    # Skip well-known architectural-role suffixes to avoid massive false-positive
    # rates — otherwise almost every Controller/Service/Repository gets flagged.
    CONVENTION_SUFFIXES = {
        "controller", "service", "repository", "repo", "model", "viewmodel",
        "factory", "provider", "handler", "extension", "helper", "manager",
        "builder", "configuration", "middleware", "filter", "validator",
        "mapper", "profile", "module", "command", "query", "event",
        "decorator", "interceptor", "adapter", "facade", "gateway",
    }

    dead_files = []
    for item in parsed:
        name      = Path(item["file"]).stem
        name_low  = name.lower()
        if any(t in name_low for t in entry_terms):
            continue
        # Skip files whose names follow a well-known architectural convention
        # in languages where DI/routing resolves references at runtime.
        if item.get("language") in ("dotnet", "java"):
            if any(name_low.endswith(suf) for suf in CONVENTION_SUFFIXES):
                continue
        if name in all_refs:
            continue
        if any(cls in all_refs for cls in item.get("classes", [])):
            continue
        dead_files.append(item["file"])

    dead_classes = []
    for cls, fp in classes_defined.items():
        if cls in skip_classes:
            continue
        if cls not in all_refs:
            dead_classes.append({"class": cls, "file": fp})

    return {"dead_files": dead_files, "dead_classes": dead_classes}


# ---------------------------------------------------------------------------
# Tech stack detection
# ---------------------------------------------------------------------------

def detect_tech_stack(parsed, repo_path):
    """Detect frameworks and tooling from import names and config files.

    Two strategies are combined:

    1. **Import-based**: Checks whether dependency strings (lowercased)
       contain known framework identifiers.
    2. **Config-file-based**: Checks for the presence of well-known config
       files (``package.json``, ``pom.xml``, ``Dockerfile``, etc.) in the
       repository root.

    Args:
        parsed (list[dict]): List of file records.
        repo_path (str): Absolute path to the cloned repository root.

    Returns:
        list[str]: Sorted, deduplicated list of detected technology names
        (e.g. ``["ASP.NET Core", "Docker", "Entity Framework"]``).
    """
    all_deps = set()
    for item in parsed:
        for dep in item.get("dependencies", []):
            all_deps.add(dep.lower())

    techs = []
    checks = [
        ({"microsoft.aspnetcore", "system.web.mvc"},        "ASP.NET Core"),
        ({"system.web"},                                     "ASP.NET Framework (Legacy)"),
        ({"entityframework", "microsoft.entityframeworkcore"}, "Entity Framework"),
        ({"dapper"},                                         "Dapper ORM"),
        ({"nop."},                                           "nopCommerce"),
        ({"org.springframework"},                            "Spring Framework"),
        ({"hibernate"},                                      "Hibernate ORM"),
        ({"django"},                                         "Django"),
        ({"flask"},                                          "Flask"),
        ({"fastapi"},                                        "FastAPI"),
        ({"sqlalchemy"},                                     "SQLAlchemy"),
        ({"react"},                                          "React"),
        ({"angular"},                                        "Angular"),
        ({"express"},                                        "Express.js"),
        ({"nestjs"},                                         "NestJS"),
        ({"next"},                                           "Next.js"),
    ]
    for triggers, label in checks:
        if any(any(t in dep for dep in all_deps) for t in triggers):
            techs.append(label)

    config_checks = [
        ("package.json",       "Node.js"),
        ("pom.xml",            "Apache Maven"),
        ("build.gradle",       "Gradle"),
        ("requirements.txt",   "Python pip"),
        ("Dockerfile",         "Docker"),
        ("docker-compose.yml", "Docker Compose"),
        ("*.csproj",           ".NET Project File"),
        ("*.sln",              ".NET Solution"),
        ("Gemfile",            "Ruby Bundler"),
        ("go.mod",             "Go Modules"),
    ]
    for pattern, label in config_checks:
        if "*" in pattern:
            if list(Path(repo_path).rglob(pattern)):
                techs.append(label)
        elif (Path(repo_path) / pattern).exists():
            techs.append(label)

    return sorted(set(techs))


# ---------------------------------------------------------------------------
# Platform and architecture detection
# ---------------------------------------------------------------------------

def detect_platform(parsed):
    """Infer the primary runtime platform from the dominant language.

    Args:
        parsed (list[dict]): List of file records.

    Returns:
        str: A human-readable platform label such as ``".NET / Windows Server"``
        or ``"Cross-platform"``.
    """
    langs = {r.get("language") for r in parsed}
    if "dotnet"     in langs: return ".NET / Windows Server"
    if "java"       in langs: return "JVM / Linux"
    if "python"     in langs: return "Python / Linux"
    if "typescript" in langs or "javascript" in langs: return "Node.js"
    return "Cross-platform"


def detect_architecture_layers(parsed):
    """Infer N-tier architecture layers from file-path keywords.

    File paths are matched (case-insensitively) against a set of keywords
    associated with each layer.  Any file that matches contributes its layer
    label to the result set.

    Args:
        parsed (list[dict]): List of file records.

    Returns:
        list[str]: Sorted list of detected layer labels, e.g.
        ``["API / Presentation Layer", "Business Logic Layer",
        "Data Access Layer"]``.
    """
    layers = set()
    for item in parsed:
        p = item["file"].lower()
        if any(x in p for x in ["controller", "api", "endpoint", "route", "handler"]):
            layers.add("API / Presentation Layer")
        if any(x in p for x in ["service", "business", "domain", "core", "logic"]):
            layers.add("Business Logic Layer")
        if any(x in p for x in ["repository", "data", "dal", "model", "entity", "db", "database"]):
            layers.add("Data Access Layer")
        if any(x in p for x in ["helper", "util", "common", "shared", "extension"]):
            layers.add("Utility / Shared Layer")
        if any(x in p for x in ["config", "setting", "startup", "program"]):
            layers.add("Configuration / Bootstrap Layer")
        if any(x in p for x in ["view", "template", "razor", "html"]):
            layers.add("View / Template Layer")
    return sorted(layers)


# ---------------------------------------------------------------------------
# Module ranking and dependency extraction
# ---------------------------------------------------------------------------

def find_top_modules(dep_map, n=10):
    """Return the *n* modules with the most outgoing dependency references.

    Args:
        dep_map (dict[str, set[str]]): Dependency map as returned by
            :func:`build_dependency_map`.
        n (int): Number of top modules to return.  Defaults to 10.

    Returns:
        list[tuple[str, int]]: List of ``(module_stem, connection_count)``
        tuples sorted in descending order of connection count.
    """
    counts = {mod: len(deps) for mod, deps in dep_map.items()}
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]


def extract_external_deps(parsed):
    """Collect and sort a deduplicated list of all unique dependency identifiers.

    Args:
        parsed (list[dict]): List of file records.

    Returns:
        list[str]: Up to 100 dependency identifiers sorted alphabetically.
    """
    all_deps = set()
    for item in parsed:
        for dep in item.get("dependencies", []):
            all_deps.add(dep)
    return sorted(all_deps)[:100]


# ---------------------------------------------------------------------------
# Database schema and microservice data boundaries
# ---------------------------------------------------------------------------

def detect_database_schema(parsed):
    """Aggregate database entity definitions from all parsed file records.

    Collects ``db_entities`` lists emitted by the language-specific parsers
    and merges duplicate entity names (the same entity class appearing in
    multiple files gets its fields and relationships combined).

    Args:
        parsed (list[dict]): List of file records from
            :func:`engine.parsers.parse_file`.

    Returns:
        dict: A schema summary with the following keys:

        - ``"entities"`` (list[dict]): Merged entity records, each with
          ``"name"``, ``"table"``, ``"fields"``, ``"relationships"``, and
          ``"file"`` keys.
        - ``"entity_count"`` (int): Total unique entities detected.
        - ``"relationship_count"`` (int): Total relationship links found.
        - ``"has_schema"`` (bool): ``True`` when at least one entity was
          detected.
        - ``"context_files"`` (list[str]): Paths of DbContext /
          SessionFactory / declarative-base files.
    """
    seen          = {}
    context_files = []

    for item in parsed:
        for entity in item.get("db_entities", []):
            name = entity.get("name")
            if not name:
                continue
            if entity.get("is_dbcontext"):
                context_files.append(item["file"])
                # Register the entity by name even without full field details yet.
                if name not in seen:
                    seen[name] = {
                        "name":          name,
                        "table":         entity.get("table", name),
                        "fields":        [],
                        "relationships": [],
                        "file":          entity.get("file", item["file"]),
                    }
                continue
            if name not in seen:
                seen[name] = {
                    "name":          name,
                    "table":         entity.get("table", name),
                    "fields":        list(entity.get("fields", [])),
                    "relationships": list(entity.get("relationships", [])),
                    "file":          entity.get("file", item["file"]),
                }
            else:
                existing  = seen[name]
                new_flds  = [f for f in entity.get("fields", [])
                             if f not in existing["fields"]]
                existing["fields"].extend(new_flds)
                existing["relationships"].extend(entity.get("relationships", []))

    entities  = list(seen.values())
    rel_count = sum(len(e["relationships"]) for e in entities)

    return {
        "entities":           entities,
        "entity_count":       len(entities),
        "relationship_count": rel_count,
        "has_schema":         len(entities) > 0,
        "context_files":      list(set(context_files)),
    }


def suggest_microservice_data_boundaries(db_schema, modernization=None):
    """Group entities into bounded contexts for microservice decomposition.

    Uses semantic domain keywords to cluster entity names.  When no entities
    are detected, falls back to the ``microservices_boundaries`` list from the
    AI modernisation roadmap if one is supplied.

    Args:
        db_schema (dict): Schema dict from :func:`detect_database_schema`.
        modernization (dict | None): AI modernisation roadmap dict.  Used as
            a fallback when no entities are detected.

    Returns:
        list[dict]: Each element has the following keys:

        - ``"name"`` (str): Bounded context / proposed microservice name.
        - ``"entities"`` (list[str]): Entity names belonging to this context.
        - ``"color"`` (str): CSS hex colour for visualisation.
        - ``"entity_count"`` (int): Number of entities in this context.
    """
    entities = db_schema.get("entities", [])
    COLORS   = [
        "#0071e3", "#30d158", "#ff9f0a", "#bf5af2",
        "#ff453a", "#5ac8fa", "#ff9500", "#64d2ff",
    ]

    if not entities:
        # Fall back to AI-generated microservice boundaries
        if modernization:
            boundaries = modernization.get("microservices_boundaries", [])
            return [
                {
                    "name":         b,
                    "entities":     [],
                    "color":        COLORS[i % len(COLORS)],
                    "entity_count": 0,
                }
                for i, b in enumerate(boundaries)
            ]
        return []

    # Semantic domain clusters (keywords → bounded context)
    domain_clusters = [
        ("Customer / Identity",  ["customer", "user", "account", "identity", "member",
                                   "profile", "address", "contact", "login", "auth",
                                   "permission", "role", "claim", "token"]),
        ("Product / Catalog",    ["product", "catalog", "category", "item", "sku",
                                   "inventory", "stock", "price", "attribute",
                                   "specification", "brand", "manufacturer", "vendor",
                                   "supplier", "tag", "picture"]),
        ("Order / Commerce",     ["order", "cart", "checkout", "purchase", "payment",
                                   "invoice", "transaction", "shipment", "delivery",
                                   "return", "refund", "discount", "coupon", "gift",
                                   "voucher", "basket"]),
        ("Content / Media",      ["content", "blog", "post", "news", "article", "page",
                                   "topic", "forum", "thread", "message", "comment",
                                   "review", "rating", "media", "file", "image",
                                   "document", "upload", "poll"]),
        ("Notification / Comms", ["notification", "email", "sms", "alert", "campaign",
                                   "newsletter", "subscription", "log", "audit",
                                   "activity", "event"]),
        ("Configuration",        ["setting", "configuration", "config", "locale",
                                   "language", "currency", "tax", "store", "country",
                                   "state", "region", "option", "parameter"]),
        ("Search / Analytics",   ["search", "index", "analytics", "report", "stat",
                                   "metric", "tracking", "session", "visit", "history"]),
    ]

    assigned   = {}
    unassigned = []

    for entity in entities:
        name_low = entity["name"].lower()
        placed   = False
        for domain_name, keywords in domain_clusters:
            if any(kw in name_low for kw in keywords):
                assigned.setdefault(domain_name, []).append(entity["name"])
                placed = True
                break
        if not placed:
            unassigned.append(entity["name"])

    result = []
    for i, (domain_name, entity_names) in enumerate(assigned.items()):
        result.append({
            "name":         domain_name,
            "entities":     entity_names,
            "color":        COLORS[i % len(COLORS)],
            "entity_count": len(entity_names),
        })

    if unassigned:
        result.append({
            "name":         "Core / Infrastructure",
            "entities":     unassigned,
            "color":        COLORS[len(result) % len(COLORS)],
            "entity_count": len(unassigned),
        })

    return result


# ---------------------------------------------------------------------------
# Block diagram generator
# ---------------------------------------------------------------------------

def generate_block_diagram(parsed, endpoints, db_schema, tech_stack):
    """Generate a Mermaid ``flowchart TB`` block diagram of the analysed system.

    The diagram is derived entirely from static analysis — no AI call required.
    It classifies parsed classes into architectural layers (controller, service,
    repository/DAO) and adds entity nodes for the database layer.

    Args:
        parsed (list[dict]): File records from :func:`engine.parsers.parse_file`.
        endpoints (list[dict]): API endpoint records from
            :func:`extract_api_endpoints`.
        db_schema (dict): Schema dict from :func:`detect_database_schema`.
        tech_stack (list[str]): Detected tech stack from
            :func:`detect_tech_stack`.

    Returns:
        str: A valid Mermaid ``flowchart TB`` diagram string ready for
        rendering in the dashboard or Markdown report.
    """
    from pathlib import Path as _Path

    # ----------------------------------------------------------------
    # Classify classes into layers
    # ----------------------------------------------------------------
    controllers, services, repositories, models = [], [], [], []
    seen: set = set()

    for item in parsed[:80]:
        for cls in item.get("classes", []):
            if cls in seen or not cls:
                continue
            seen.add(cls)
            lower = cls.lower()
            if any(k in lower for k in ("controller", "handler", "router", "endpoint")):
                controllers.append(cls)
            elif any(k in lower for k in ("service", "manager", "usecase", "facade", "workflow")):
                services.append(cls)
            elif any(k in lower for k in ("repository", "repo", "dao", "store", "gateway", "adapter")):
                repositories.append(cls)
            elif any(k in lower for k in ("model", "entity", "dto", "viewmodel", "schema")):
                models.append(cls)

    # Cap each layer for diagram readability
    controllers  = controllers[:6]
    services     = services[:6]
    repositories = repositories[:5]
    entities     = [e["name"] for e in db_schema.get("entities", [])[:6]]

    # ----------------------------------------------------------------
    # Helper: safe node ID (alphanumeric + underscore)
    # ----------------------------------------------------------------
    import re as _re
    def _safe(name):
        return _re.sub(r'[^A-Za-z0-9]', '_', name)

    lines = ["flowchart TB"]

    # ── Client ──────────────────────────────────────────────────────
    lines.append('    Client(["👤 User / Client"])')
    lines.append("")

    # ── API / Presentation Layer ─────────────────────────────────────
    if controllers or endpoints:
        lines.append('    subgraph API["🌐 API / Presentation Layer"]')
        if controllers:
            for c in controllers:
                lines.append(f'        {_safe(c)}["{c}"]')
        else:
            # Fall back to showing grouped endpoints by first segment
            _ep_groups: dict = {}
            for ep in endpoints[:8]:
                parts = [p for p in ep["path"].split("/")
                         if p and not p.startswith("{") and p.lower() not in ("api","v1","v2","v3")]
                seg = parts[0].title() if parts else "API"
                _ep_groups.setdefault(seg, 0)
                _ep_groups[seg] += 1
            for seg, cnt in list(_ep_groups.items())[:5]:
                lines.append(f'        {_safe(seg)}Handler["{seg} Handler ({cnt} routes)"]')
        lines.append('    end')
        lines.append("")

    # ── Business Logic / Service Layer ───────────────────────────────
    if services:
        lines.append('    subgraph BL["⚙️ Business Logic / Service Layer"]')
        for s in services:
            lines.append(f'        {_safe(s)}["{s}"]')
        lines.append('    end')
        lines.append("")

    # ── Data Access Layer ────────────────────────────────────────────
    if repositories:
        lines.append('    subgraph DAL["🗄️ Data Access / Repository Layer"]')
        for r in repositories:
            lines.append(f'        {_safe(r)}["{r}"]')
        lines.append('    end')
        lines.append("")
    elif entities:
        lines.append('    subgraph DAL["🗄️ Data Access / Repository Layer"]')
        lines.append('        ORM["ORM / Data Mapper"]')
        lines.append('    end')
        lines.append("")

    # ── Database ─────────────────────────────────────────────────────
    if entities:
        lines.append('    subgraph DB["🗃️ Database"]')
        for e in entities:
            lines.append(f'        db_{_safe(e)}[("{e}")]')
        lines.append('    end')
        lines.append("")

    # ── External integrations (from tech stack) ──────────────────────
    ext_map = {
        "redis":    ("cache", "🔴 Redis Cache"),
        "kafka":    ("queue", "📨 Kafka / MQ"),
        "rabbitmq": ("queue", "📨 RabbitMQ"),
        "email":    ("email", "📧 Email / SMTP"),
        "smtp":     ("email", "📧 Email / SMTP"),
        "s3":       ("storage", "☁️ Cloud Storage"),
        "azure":    ("cloud",   "☁️ Azure"),
        "aws":      ("cloud",   "☁️ AWS"),
        "stripe":   ("payment", "💳 Payment Gateway"),
        "paypal":   ("payment", "💳 Payment Gateway"),
        "oauth":    ("auth",    "🔐 Auth / OAuth"),
        "jwt":      ("auth",    "🔐 Auth / JWT"),
    }
    shown_ext: set = set()
    ext_nodes = []
    stack_lower = " ".join(tech_stack).lower()
    for kw, (group, label) in ext_map.items():
        if kw in stack_lower and group not in shown_ext:
            shown_ext.add(group)
            node_id = f"ext_{group}"
            ext_nodes.append((node_id, label))

    if ext_nodes:
        lines.append('    subgraph EXT["🔌 External Services"]')
        for nid, label in ext_nodes[:4]:
            lines.append(f'        {nid}["{label}"]')
        lines.append('    end')
        lines.append("")

    # ── Connections ──────────────────────────────────────────────────
    # Client → controllers (or handlers)
    if controllers:
        for c in controllers[:3]:
            lines.append(f'    Client -->|"HTTP request"| {_safe(c)}')
    elif endpoints:
        first_handler = _safe(list(_ep_groups.keys())[0]) + "Handler" if '_ep_groups' in dir() else "API_Entry"
        lines.append(f'    Client -->|"HTTP request"| {first_handler}')
    lines.append("")

    # controllers → services
    if controllers and services:
        for i, c in enumerate(controllers[:4]):
            svc = services[min(i, len(services) - 1)]
            lines.append(f'    {_safe(c)} -->|"calls"| {_safe(svc)}')
        lines.append("")

    # services → repositories
    if services and (repositories or entities):
        for i, s in enumerate(services[:4]):
            if repositories:
                repo = repositories[min(i, len(repositories) - 1)]
                lines.append(f'    {_safe(s)} -->|"data ops"| {_safe(repo)}')
            else:
                lines.append(f'    {_safe(s)} -->|"data ops"| ORM')
        lines.append("")

    # repositories → DB
    if repositories and entities:
        for r in repositories[:3]:
            ent = entities[0]
            lines.append(f'    {_safe(r)} -->|"SQL / ORM"| db_{_safe(ent)}')
    elif entities:
        lines.append(f'    ORM -->|"SQL / ORM"| db_{_safe(entities[0])}')
    lines.append("")

    # services → external
    if services and ext_nodes:
        svc0 = _safe(services[0])
        for nid, _ in ext_nodes[:2]:
            lines.append(f'    {svc0} -->|"uses"| {nid}')

    return "\n".join(lines)
