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
3. :func:`generate_dep_graph_data` — structured dependency graph (nodes + edges)
4. :func:`extract_api_endpoints` — flat list of routes
5. :func:`generate_openapi_spec` — OpenAPI 3.0 spec dict
6. :func:`detect_dead_code` — unreferenced files and classes
7. :func:`detect_tech_stack` — frameworks and tooling
8. :func:`detect_platform` — runtime platform
9. :func:`detect_architecture_layers` — N-tier layer labels
10. :func:`find_top_modules` — most-connected modules
11. :func:`extract_external_deps` — sorted external dependency list
12. :func:`generate_block_diagram` — structured block diagram (layers + edges)
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


def generate_dep_graph_data(parsed, max_links=80):
    """Build a structured dependency graph from parsed records.

    Returns a JSON-serialisable dict of nodes and directed edges suitable
    for rendering with vis.js (Architecture tab) or any SVG renderer.
    Standard-library / framework root packages are filtered out.

    Args:
        parsed (list[dict]): List of file records.
        max_links (int): Maximum number of edges to emit.  Defaults to 80.

    Returns:
        dict: ``{"nodes": [{"id", "label", "group"}], "edges": [{"from", "to"}]}``
    """
    IGNORE = {
        "java", "javax", "org", "com", "System", "Microsoft", "Newtonsoft",
        "os", "sys", "re", "json", "typing", "collections", "datetime", "math",
        "time", "subprocess", "ast", "pathlib", "abc", "enum", "functools",
        "react", "lodash", "express", "next", "angular", "vue",
    }
    node_ids: dict = {}   # label -> int id
    nodes:    list = []
    edges:    list = []
    seen_edges: set = set()
    nid = 0
    edge_count = 0

    def _get_node(label, group):
        nonlocal nid
        if label not in node_ids:
            node_ids[label] = nid
            nodes.append({"id": nid, "label": label, "group": group})
            nid += 1
        return node_ids[label]

    for item in parsed:
        if edge_count >= max_links:
            break
        src_raw = re.sub(r'[^a-zA-Z0-9_]', '_', Path(item["file"]).stem)
        src_id  = _get_node(src_raw, "module")
        for dep in item.get("dependencies", []):
            root = dep.split(".")[0]
            if root in IGNORE or not root:
                continue
            tgt_raw = re.sub(r'[^a-zA-Z0-9_]', '_', dep.replace(".", "_"))
            if src_raw == tgt_raw or (src_raw, tgt_raw) in seen_edges:
                continue
            seen_edges.add((src_raw, tgt_raw))
            tgt_display = dep.replace("_", ".")
            tgt_id = _get_node(tgt_display, "dependency")
            edges.append({"from": src_id, "to": tgt_id})
            edge_count += 1

    return {"nodes": nodes, "edges": edges}


def generate_graphviz_dot(dep_graph_data):
    """Generate a Graphviz DOT string from dependency graph data dictionary.

    Args:
        dep_graph_data (dict): Dict with "nodes" and "edges" lists.

    Returns:
        str: Valid Graphviz DOT language string.
    """
    dot = [
        "digraph G {",
        "  rankdir=LR;",
        "  splines=true;",
        "  node [shape=box, style=filled, fillcolor=\"#aeaeb2\", color=\"#8e8e93\", fontcolor=\"#1d1d1f\", fontname=\"Helvetica\", fontsize=10];",
        "  edge [color=\"#c7c7cc\", fontname=\"Helvetica\", fontsize=8];"
    ]
    
    nodes = dep_graph_data.get("nodes", [])
    edges = dep_graph_data.get("edges", [])
    
    # Custom node colors by role
    for n in nodes:
        lbl = n.get("label", "")
        nid = n.get("id", "")
        if "controller" in lbl.lower() or "handler" in lbl.lower():
            fill, border, font = "#0071e3", "#005bb5", "#ffffff"
            shape = "box"
        elif "service" in lbl.lower() or "manager" in lbl.lower():
            fill, border, font = "#30d158", "#1a8c3a", "#ffffff"
            shape = "box"
        elif "repository" in lbl.lower() or "repo" in lbl.lower():
            fill, border, font = "#ff9f0a", "#c47900", "#ffffff"
            shape = "box"
        else:
            fill, border, font = "#aeaeb2", "#8e8e93", "#1d1d1f"
            shape = "ellipse"
            
        dot.append(f"  node_{nid} [label=\"{lbl}\", fillcolor=\"{fill}\", color=\"{border}\", fontcolor=\"{font}\", shape=\"{shape}\"];")
        
    for e in edges:
        dot.append(f"  node_{e['from']} -> node_{e['to']};")
        
    dot.append("}")
    return "\n".join(dot)


# Keep the old name as an alias so existing code that may import it still works
def generate_mermaid(parsed, max_links=80):
    """Alias for backward compatibility — returns Graphviz DOT string."""
    return generate_graphviz_dot(generate_dep_graph_data(parsed, max_links))


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
    """Generate a structured block diagram of the analysed system.

    Returns a JSON-serialisable dict with ``layers`` (list of layer groups,
    each containing named nodes) and ``edges`` (directed connections between
    layers).  The dashboard renders this with a pure-SVG custom renderer —
    no Mermaid.js or external library required.

    Args:
        parsed (list[dict]): File records from :func:`engine.parsers.parse_file`.
        endpoints (list[dict]): API endpoint records.
        db_schema (dict): Schema dict from :func:`detect_database_schema`.
        tech_stack (list[str]): Detected tech stack.

    Returns:
        dict: ``{"layers": [{"id", "label", "color", "nodes": [{"id", "label"}]}],
                "edges": [{"from", "to", "label"}]}``
    """
    import re as _re

    def _safe(name):
        return _re.sub(r'[^A-Za-z0-9]', '_', str(name))

    # Classify files and classes into layers using both class names and path heuristics
    controllers, services, repositories = [], [], []
    seen_classes = set()
    seen_components = set()

    for item in parsed[:150]:
        file_path = item.get("file", "")
        file_lower = file_path.lower()
        
        # Check folder structure
        is_presentation = any(k in file_lower for k in ("/controllers/", "/api/", "/endpoints/", "/handlers/", "/pages/", "/views/", "\\controllers\\", "\\api\\", "\\endpoints\\", "\\handlers\\", "\\pages\\", "\\views\\")) or file_lower.endswith((".aspx", ".html", ".js", ".ts"))
        is_logic = any(k in file_lower for k in ("/services/", "/managers/", "/usecases/", "/business/", "/logic/", "/workflows/", "\\services\\", "\\managers\\", "\\usecases\\", "\\business\\", "\\logic\\", "\\workflows\\"))
        is_data = any(k in file_lower for k in ("/repositories/", "/repos/", "/dao/", "/dal/", "/store/", "/data/", "/db/", "\\repositories\\", "\\repos\\", "\\dao\\", "\\dal\\", "\\store\\", "\\data\\", "\\db\\"))

        # Check classes defined in this file
        for cls in item.get("classes", []):
            if cls in seen_classes or not cls:
                continue
            seen_classes.add(cls)
            lower_cls = cls.lower()
            
            if any(k in lower_cls for k in ("controller", "handler", "router", "endpoint")) or is_presentation:
                if cls not in controllers:
                    controllers.append(cls)
            elif any(k in lower_cls for k in ("service", "manager", "usecase", "facade", "workflow")) or is_logic:
                if cls not in services:
                    services.append(cls)
            elif any(k in lower_cls for k in ("repository", "repo", "dao", "store", "gateway", "adapter", "context")) or is_data:
                if cls not in repositories:
                    repositories.append(cls)

        # Fallback if no classes defined but the file itself maps to a layer
        if not item.get("classes"):
            stem = Path(file_path).stem
            if stem not in seen_components and stem:
                seen_components.add(stem)
                if is_presentation or any(k in file_lower for k in ("controller", "handler", "router", "endpoint")):
                    controllers.append(stem)
                elif is_logic or any(k in file_lower for k in ("service", "manager", "usecase", "facade", "workflow")):
                    services.append(stem)
                elif is_data or any(k in file_lower for k in ("repository", "repo", "dao", "store", "gateway", "adapter", "context")):
                    repositories.append(stem)

    controllers  = controllers[:5]
    services     = services[:5]
    repositories = repositories[:4]
    entities     = [e["name"] for e in (db_schema or {}).get("entities", [])[:5]]

    layers = []
    edges  = []

    # Layer 0: Client
    layers.append({
        "id": "client",
        "label": "User / Client",
        "color": "#6e6e73",
        "icon": "user",
        "nodes": [{"id": "client_node", "label": "Client"}],
    })

    # Layer 1: API / Controllers
    api_nodes = []
    if controllers:
        api_nodes = [{"id": _safe(c), "label": c} for c in controllers]
    elif endpoints:
        ep_groups: dict = {}
        for ep in endpoints[:6]:
            parts = [p for p in ep["path"].split("/")
                     if p and not p.startswith("{") and p.lower() not in ("api", "v1", "v2", "v3")]
            seg = parts[0].title() if parts else "API"
            ep_groups.setdefault(seg, 0)
            ep_groups[seg] += 1
        api_nodes = [{"id": _safe(s) + "_handler", "label": f"{s} ({c} routes)"}
                     for s, c in list(ep_groups.items())[:5]]

    if api_nodes:
        layers.append({
            "id": "api",
            "label": "API / Presentation Layer",
            "color": "#0071e3",
            "icon": "api",
            "nodes": api_nodes,
        })
        for n in api_nodes[:3]:
            edges.append({"from": "client_node", "to": n["id"], "label": "HTTP"})

    # Layer 2: Service / Business Logic
    if services:
        svc_nodes = [{"id": _safe(s), "label": s} for s in services]
        layers.append({
            "id": "service",
            "label": "Business Logic / Service Layer",
            "color": "#30d158",
            "icon": "service",
            "nodes": svc_nodes,
        })
        for i, an in enumerate(api_nodes[:4]):
            sn = svc_nodes[min(i, len(svc_nodes) - 1)]
            edges.append({"from": an["id"], "to": sn["id"], "label": "calls"})

    # Layer 3: Repository / Data Access
    if repositories:
        repo_nodes = [{"id": _safe(r), "label": r} for r in repositories]
        layers.append({
            "id": "repo",
            "label": "Data Access / Repository Layer",
            "color": "#ff9f0a",
            "icon": "repo",
            "nodes": repo_nodes,
        })
        src_layer = services if services else (controllers if controllers else [])
        for i, s in enumerate(src_layer[:4]):
            rn = repo_nodes[min(i, len(repo_nodes) - 1)]
            edges.append({"from": _safe(s), "to": rn["id"], "label": "data ops"})
    elif entities:
        orm_nodes = [{"id": "orm_node", "label": "ORM / Data Mapper"}]
        layers.append({
            "id": "repo",
            "label": "Data Access Layer",
            "color": "#ff9f0a",
            "icon": "repo",
            "nodes": orm_nodes,
        })

    # Layer 4: Database entities
    if entities:
        db_nodes = [{"id": "db_" + _safe(e), "label": e} for e in entities]
        layers.append({
            "id": "database",
            "label": "Database",
            "color": "#bf5af2",
            "icon": "db",
            "nodes": db_nodes,
        })
        repo_layer = next((l for l in layers if l["id"] == "repo"), None)
        if repo_layer:
            for i, rn in enumerate(repo_layer["nodes"][:3]):
                dn = db_nodes[min(i, len(db_nodes) - 1)]
                edges.append({"from": rn["id"], "to": dn["id"], "label": "SQL/ORM"})

    # Layer 5: External Services (from tech stack)
    ext_map = {
        "redis":    ("cache",   "Redis Cache"),
        "kafka":    ("queue",   "Kafka / MQ"),
        "rabbitmq": ("queue",   "RabbitMQ"),
        "email":    ("email",   "Email / SMTP"),
        "smtp":     ("email",   "Email / SMTP"),
        "s3":       ("storage", "Cloud Storage"),
        "azure":    ("cloud",   "Azure"),
        "aws":      ("cloud",   "AWS"),
        "stripe":   ("payment", "Payment Gateway"),
        "paypal":   ("payment", "Payment Gateway"),
        "oauth":    ("auth",    "Auth / OAuth"),
        "jwt":      ("auth",    "Auth / JWT"),
    }
    shown_ext: set = set()
    ext_nodes = []
    stack_lower = " ".join(tech_stack).lower()
    for kw, (group, label) in ext_map.items():
        if kw in stack_lower and group not in shown_ext:
            shown_ext.add(group)
            ext_nodes.append({"id": "ext_" + group, "label": label})

    if ext_nodes[:4]:
        layers.append({
            "id": "external",
            "label": "External Services",
            "color": "#ff453a",
            "icon": "ext",
            "nodes": ext_nodes[:4],
        })
        # Connect service layer (or API layer) to external services
        src_ids = ([_safe(s) for s in services[:2]] or
                   [n["id"] for n in api_nodes[:2]])
        for sid in src_ids:
            for en in ext_nodes[:2]:
                edges.append({"from": sid, "to": en["id"], "label": "integrates"})

    return {"layers": layers, "edges": edges}


def generate_block_diagram_dot(block_diagram_data):
    """Generate a Graphviz DOT string for the block diagram layers.

    Args:
        block_diagram_data (dict): Dict with "layers" and "edges" lists.

    Returns:
        str: Graphviz DOT representation of block diagram.
    """
    if not block_diagram_data or "layers" not in block_diagram_data:
        return "digraph G { A [label=\"No diagram generated\"]; }"
        
    dot = [
        "digraph G {",
        "  rankdir=TB;",
        "  splines=ortho;",
        "  nodesep=0.4;",
        "  ranksep=0.5;",
        "  bgcolor=\"transparent\";",
        "  node [shape=box, style=\"filled,rounded\", fontname=\"Helvetica\", fontsize=11, fillcolor=\"#f5f5f7\", fontcolor=\"#1d1d1f\", penwidth=1.5];",
        "  edge [color=\"#8e8e93\", fontname=\"Helvetica\", fontsize=9, fontcolor=\"#8e8e93\", arrowhead=vee, arrowsize=0.7];"
    ]
    
    layers = block_diagram_data.get("layers", [])
    edges = block_diagram_data.get("edges", [])
    
    for i, layer in enumerate(layers):
        dot.append(f"  subgraph cluster_{i} {{")
        dot.append(f"    label = \"{layer.get('label', '')}\";")
        dot.append(f"    color = \"{layer.get('color', '#aeaeb2')}\";")
        dot.append(f"    style = \"dashed,rounded\";")
        dot.append(f"    fontname = \"Helvetica\";")
        dot.append(f"    fontsize = 12;")
        dot.append(f"    fontcolor = \"{layer.get('color', '#1d1d1f')}\";")
        dot.append(f"    penwidth = 2.0;")
        
        for node in layer.get("nodes", []):
            dot.append(f"    \"{node['id']}\" [label=\"{node.get('label', '')}\", fillcolor=\"{layer.get('color', '#f5f5f7')}\", fontcolor=\"#ffffff\", style=\"filled,rounded\", penwidth=0];")
        dot.append("  }")
        
    for edge in edges:
        dot.append(f"  \"{edge['from']}\" -> \"{edge['to']}\" [label=\"{edge.get('label', '')}\"];")
        
    dot.append("}")
    return "\n".join(dot)


def generate_block_diagram_svg(block_diagram_data):
    """Generate a premium, responsive SVG image for the layered block diagram.

    Args:
        block_diagram_data (dict): Layer and edge data structures.

    Returns:
        str: Self-contained XML SVG content.
    """
    if not block_diagram_data or "layers" not in block_diagram_data:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="50"><text x="10" y="30">No diagram generated</text></svg>'

    layers = block_diagram_data.get("layers", [])
    edges = block_diagram_data.get("edges", [])

    layer_height = 100
    layer_gap = 40
    total_layers = len(layers)
    total_height = 20 + total_layers * (layer_height + layer_gap) - layer_gap + 20

    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="700" height="{total_height}" viewBox="0 0 700 {total_height}">',
        '  <style>',
        '    .layer-bg { fill: #f5f5f7; stroke: #e5e5ea; stroke-width: 1.5; }',
        '    .node-pill { fill: #ffffff; stroke: #d1d1d6; stroke-width: 1.5; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.03)); }',
        '    .node-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 11px; fill: #1d1d1f; font-weight: 600; text-anchor: middle; dominant-baseline: middle; }',
        '    .layer-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }',
        '    .connector-line { stroke: #aeaeb2; stroke-width: 2; stroke-dasharray: 4 3; }',
        '    .connector-arrow { fill: #aeaeb2; }',
        '    .connector-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 9px; fill: #8e8e93; font-weight: 600; text-anchor: start; }',
        '  </style>',
    ]

    for idx, layer in enumerate(layers):
        y = 20 + idx * (layer_height + layer_gap)
        color = layer.get("color", "#8e8e93")
        label = layer.get("label", "Layer").upper()
        nodes = layer.get("nodes", [])

        # Background card
        svg_parts.append(f'  <!-- Layer {idx}: {label} -->')
        svg_parts.append(f'  <rect x="25" y="{y}" width="650" height="{layer_height}" rx="12" class="layer-bg" />')
        
        # Color indicator path
        svg_parts.append(f'  <path d="M 25 {y + 6} L 25 {y + layer_height - 6}" stroke="{color}" stroke-width="5" stroke-linecap="round" />')
        
        # Layer title
        svg_parts.append(f'  <text x="40" y="{y + 24}" fill="{color}" class="layer-title">{label}</text>')

        # Node pills
        if nodes:
            num_nodes = len(nodes)
            spacing = min(130, 580 // (num_nodes - 1)) if num_nodes > 1 else 130
            y_offset = y + 58
            pill_w = 114
            pill_h = 32
            
            for j, node in enumerate(nodes):
                node_x_center = 350 - (num_nodes - 1) * spacing // 2 + j * spacing
                pill_x = node_x_center - pill_w // 2
                pill_y = y_offset - pill_h // 2
                node_lbl = node.get("label", "")
                
                svg_parts.append(f'  <rect x="{pill_x}" y="{pill_y}" width="{pill_w}" height="{pill_h}" rx="8" class="node-pill" />')
                # Bullet dot indicator
                svg_parts.append(f'  <circle cx="{pill_x + 12}" cy="{y_offset}" r="3.5" fill="{color}" />')
                # Text
                svg_parts.append(f'  <text x="{node_x_center + 6}" y="{y_offset + 1}" class="node-text">{node_lbl}</text>')

        # Connector
        if idx < total_layers - 1:
            current_node_ids = {n["id"] for n in nodes}
            next_nodes = layers[idx+1].get("nodes", [])
            next_node_ids = {n["id"] for n in next_nodes}
            
            layer_edge_labels = []
            for edge in edges:
                if edge.get("from") in current_node_ids and edge.get("to") in next_node_ids:
                    lbl = edge.get("label", "")
                    if lbl and lbl not in layer_edge_labels:
                        layer_edge_labels.append(lbl)
            
            connector_label = f"{', '.join(layer_edge_labels)}" if layer_edge_labels else ""
            y_connector_start = y + layer_height
            y_connector_end = y_connector_start + layer_gap
            
            svg_parts.append(f'  <!-- Connector Layer {idx} -> {idx+1} -->')
            svg_parts.append(f'  <line x1="350" y1="{y_connector_start}" x2="350" y2="{y_connector_end - 6}" class="connector-line" />')
            svg_parts.append(f'  <polygon points="346,{y_connector_end - 6} 354,{y_connector_end - 6} 350,{y_connector_end}" class="connector-arrow" />')
            if connector_label:
                svg_parts.append(f'  <text x="365" y="{y_connector_start + layer_gap // 2 + 3}" class="connector-text">{connector_label}</text>')

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def generate_dep_graph_svg(dep_graph_data):
    """Generate a premium, responsive SVG image for the module dependency graph.
    Uses a pure-Python force-directed layout that is fast and completely self-contained.

    Args:
        dep_graph_data (dict): Dependency graph with "nodes" and "edges" lists.

    Returns:
        str: Self-contained XML SVG content.
    """
    if not dep_graph_data or "nodes" not in dep_graph_data:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="50"><text x="10" y="30">No graph generated</text></svg>'

    nodes = dep_graph_data.get("nodes", [])
    edges = dep_graph_data.get("edges", [])

    if not nodes:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="50"><text x="10" y="30">No nodes in graph</text></svg>'

    import math
    import random

    # Seed random for a deterministic layout of the same graph
    random.seed(42)

    width, height = 800, 600
    iterations = 100
    num_nodes = len(nodes)

    # Initialize positions along a circle to avoid overlapping starts
    pos = {}
    for i, node in enumerate(nodes):
        angle = i * (2 * math.pi / max(1, num_nodes))
        r = 180 + (i % 3) * 20
        pos[node["id"]] = [
            width / 2 + r * math.cos(angle),
            height / 2 + r * math.sin(angle)
        ]

    # Force-directed layout parameters
    k = math.sqrt((700 * 500) / max(1, num_nodes))
    c_rep = 0.8
    c_att = 1.2
    t = 80.0
    dt = t / iterations

    for _ in range(iterations):
        disp = {n["id"]: [0.0, 0.0] for n in nodes}

        # Repulsive forces between all nodes
        for i in range(num_nodes):
            n1 = nodes[i]["id"]
            for j in range(num_nodes):
                if i == j:
                    continue
                n2 = nodes[j]["id"]
                dx = pos[n1][0] - pos[n2][0]
                dy = pos[n1][1] - pos[n2][1]
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 0.1
                f = (k * k * c_rep) / dist
                disp[n1][0] += (dx / dist) * f
                disp[n1][1] += (dy / dist) * f

        # Attractive forces along edges
        for edge in edges:
            u, v = edge["from"], edge["to"]
            if u not in pos or v not in pos:
                continue
            dx = pos[u][0] - pos[v][0]
            dy = pos[u][1] - pos[v][1]
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 0.1
            f = (dist * dist * c_att) / k
            disp[u][0] -= (dx / dist) * f
            disp[u][1] -= (dy / dist) * f
            disp[v][0] += (dx / dist) * f
            disp[v][1] += (dy / dist) * f

        # Apply displacement limited by temperature
        for n in nodes:
            nid = n["id"]
            dx, dy = disp[nid]
            dist = math.hypot(dx, dy)
            if dist > 0:
                limited_dist = min(dist, t)
                pos[nid][0] += (dx / dist) * limited_dist
                pos[nid][1] += (dy / dist) * limited_dist

            pos[nid][0] = max(60, min(width - 60, pos[nid][0]))
            pos[nid][1] = max(40, min(height - 40, pos[nid][1]))

        t -= dt

    # Pre-calculate pill widths for exact boundary drawing
    pill_widths = {}
    pill_height = 24
    for n in nodes:
        lbl = n.get("label", "")
        pill_widths[n["id"]] = max(70, len(lbl) * 7 + 16)

    # Normalize positions to fit the canvas perfectly with comfortable, width-aware margins
    xs = [pos[n["id"]][0] for n in nodes]
    ys = [pos[n["id"]][1] for n in nodes]

    if len(nodes) > 1:
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max_x - min_x
        span_y = max_y - min_y

        for n in nodes:
            nid = n["id"]
            w = pill_widths[nid]
            
            # Constrain horizontally so that the pill is always fully visible (with a 15px margin)
            min_allowed_x = w / 2 + 15
            max_allowed_x = width - (w / 2 + 15)
            
            if span_x > 0:
                pos_pct_x = (pos[nid][0] - min_x) / span_x
                pos[nid][0] = min_allowed_x + pos_pct_x * (max_allowed_x - min_allowed_x)
            else:
                pos[nid][0] = width / 2

            # Constrain vertically so that the pill is always fully visible (with a 20px margin)
            min_allowed_y = pill_height / 2 + 20
            max_allowed_y = height - (pill_height / 2 + 20)
            
            if span_y > 0:
                pos_pct_y = (pos[nid][1] - min_y) / span_y
                pos[nid][1] = min_allowed_y + pos_pct_y * (max_allowed_y - min_allowed_y)
            else:
                pos[nid][1] = height / 2
    else:
        for n in nodes:
            pos[n["id"]] = [width / 2, height / 2]



    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">',
        '  <defs>',
        '    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8e8e93" />',
        '    </marker>',
        '  </defs>',
        '  <rect width="100%" height="100%" fill="#fafafa" rx="16" stroke="#e5e5ea" stroke-width="1.5" />',
        '  <style>',
        '    .edge-line { stroke: #aeaeb2; stroke-width: 1.5; fill: none; marker-end: url(#arrow); }',
        '    .node-rect { stroke-width: 1.5; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.03)); }',
        '    .node-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 10px; font-weight: 600; text-anchor: middle; dominant-baseline: middle; }',
        '    .graph-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; font-weight: 700; fill: #1d1d1f; }',
        '  </style>',
        '  <text x="30" y="35" class="graph-title">Module Dependency Graph</text>',
    ]

    # Draw edge lines connecting the pill boundaries exactly
    for edge in edges:
        u_id, v_id = edge["from"], edge["to"]
        if u_id not in pos or v_id not in pos:
            continue

        # Find node dicts
        u_node = next((n for n in nodes if n["id"] == u_id), None)
        v_node = next((n for n in nodes if n["id"] == v_id), None)
        if not u_node or not v_node:
            continue

        x1, y1 = pos[u_id]
        x2, y2 = pos[v_id]

        dx = x2 - x1
        dy = y2 - y1
        d = math.hypot(dx, dy)
        if d > 0:
            ux = dx / d
            uy = dy / d

            w1 = pill_widths[u_id]
            h1 = pill_height
            offset1 = min((w1 / 2) / max(0.001, abs(ux)), (h1 / 2) / max(0.001, abs(uy)))

            w2 = pill_widths[v_id]
            h2 = pill_height
            offset2 = min((w2 / 2) / max(0.001, abs(ux)), (h2 / 2) / max(0.001, abs(uy)))

            x_start = x1 + ux * offset1
            y_start = y1 + uy * offset1
            x_end = x2 - ux * (offset2 + 7)  # leave space for the arrow head marker
            y_end = y2 - uy * (offset2 + 7)

            svg_parts.append(f'  <line x1="{x_start:.1f}" y1="{y_start:.1f}" x2="{x_end:.1f}" y2="{y_end:.1f}" class="edge-line" />')

    # Draw node pills
    for n in nodes:
        lbl = n.get("label", "")
        nid = n["id"]
        x, y = pos[nid]
        w = pill_widths[nid]
        h = pill_height

        rx = x - w / 2
        ry = y - h / 2

        # Role-based color matching
        if "controller" in lbl.lower() or "handler" in lbl.lower():
            fill, stroke, font = "#0071e3", "#005bb5", "#ffffff"
        elif "service" in lbl.lower() or "manager" in lbl.lower():
            fill, stroke, font = "#30d158", "#1a8c3a", "#ffffff"
        elif "repository" in lbl.lower() or "repo" in lbl.lower():
            fill, stroke, font = "#ff9f0a", "#c47900", "#ffffff"
        elif "entity" in lbl.lower() or "model" in lbl.lower() or "dto" in lbl.lower() or "domain" in lbl.lower():
            fill, stroke, font = "#af52de", "#7a22b8", "#ffffff"
        else:
            fill, stroke, font = "#ffffff", "#d1d1d6", "#1d1d1f"

        svg_parts.append(f'  <!-- Node {nid}: {lbl} -->')
        svg_parts.append(f'  <rect x="{rx:.1f}" y="{ry:.1f}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" class="node-rect" />')
        svg_parts.append(f'  <text x="{x:.1f}" y="{y + 1:.1f}" fill="{font}" class="node-text">{lbl}</text>')

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)

