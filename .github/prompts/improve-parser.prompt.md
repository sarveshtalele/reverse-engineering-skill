---
mode: ask
description: Add a new language parser or improve an existing parser in the Reverse Engineer Skill engine
tools:
  - read_file
  - insert_edit_into_file
  - grep_search
---

# Add / Improve a Language Parser

You are improving the static analysis parsers in the **Reverse Engineer Skill** (`engine/parsers.py`).

## Parser Architecture

Parsers live in `engine/parsers.py`. Each parser:
- Receives a file path (str) and source code (str)
- Returns a dict with exactly 8 keys
- Uses regex only — no AST libraries, no runtime execution

The dispatcher `parse_file(file_record)` calls `detect_language()` and routes to the correct `parse_X()`.

## Parser Return Contract

Every parser function MUST return this exact dict structure:

```python
{
    "file":         str,          # Absolute path to the source file
    "language":     str,          # "python" | "java" | "dotnet" | "typescript" | "javascript"
    "classes":      list[str],    # Class and interface names defined in this file
    "methods":      list[str],    # Method/function names (language keywords excluded)
    "imports":      list[str],    # Raw import strings as written in source
    "dependencies": list[str],    # Deduplicated top-level dependency namespaces
    "routes":       list[dict],   # API route dicts — see format below
    "db_entities":  list[dict],   # ORM entity dicts — see format below
}
```

**Route dict:**
```python
{
    "path":    "/api/users/{id}",   # URL path (OpenAPI-style params)
    "methods": ["GET"],             # HTTP verbs — uppercase
    "class":   "UserController",    # Controller/class name or None
    "method":  "GetUser"            # Handler method name or None
}
```

**DB entity dict:**
```python
{
    "name":          "Customer",
    "table":         "Customers",       # from annotation or class name
    "fields":        [{"name": "Email", "type": "string"}, ...],
    "relationships": [{"type": "OneToMany", "target": "Order"}, ...],
    "file":          "Customer.cs"
}
```

If the language has no ORM framework or no entities are detected, return `"db_entities": []`.

---

## How to Register a New Language

**Step 1** — Add the file extension to `detect_language()` in `engine/parsers.py`:
```python
".go": "go",
```

**Step 2** — Add the extension to `SUPPORTED_EXTENSIONS` in `engine/loaders.py`:
```python
".go",
```

**Step 3** — Write the `parse_X(file_path, code)` function.

**Step 4** — Add the dispatch case to `parse_file()` in `engine/parsers.py`:
```python
if lang == "go":
    return parse_go(path, code)
```

**Step 5** — Optionally add tech stack detection signatures to `detect_tech_stack()` in `engine/analyzer.py`.

---

## Example — Adding Go Support

```python
# engine/parsers.py

def parse_go(file_path, code):
    """Parse a Go source file to extract types, functions, imports, and Gin HTTP routes.

    Args:
        file_path (str): Absolute path to the .go file.
        code (str): Full source code of the file.

    Returns:
        dict: Standard parser return contract with 8 keys.
            db_entities is always [] for Go (no standard Go ORM annotation pattern).
    """
    # Struct and interface types
    classes = re.findall(r'^type\s+(\w+)\s+(?:struct|interface)', code, re.MULTILINE)

    # Top-level and method functions
    funcs = re.findall(
        r'^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(',
        code, re.MULTILINE
    )
    _kw = {"init", "main", "New", "Error", "String"}
    funcs = [f for f in funcs if f not in _kw]

    # Quoted import paths
    raw_imports = re.findall(r'"([^"]+)"', code)
    deps = list({imp.split("/")[-1] for imp in raw_imports if "/" in imp})

    # Gin / Echo HTTP routes
    routes = []
    for verb, path in re.findall(
        r'\.(?:GET|POST|PUT|DELETE|PATCH)\s*\(\s*"([^"]+)"', code
    ):
        routes.append({
            "path":    path,
            "methods": [verb],
            "class":   None,
            "method":  "handler",
        })

    return {
        "file":         file_path,
        "language":     "go",
        "classes":      classes,
        "methods":      funcs,
        "imports":      raw_imports,
        "dependencies": deps,
        "routes":       routes,
        "db_entities":  [],  # Go ORM (GORM) uses struct tags — add _extract_db_entities_go() to detect
    }
```

---

## Current Parser Coverage

| Language | Extensions | API Framework | ORM Entity Detection |
|----------|-----------|--------------|---------------------|
| Python | `.py` | Flask `@route`, FastAPI `@get/post/...` | SQLAlchemy `Column()`, Django `models.Model` |
| Java | `.java` | Spring `@GetMapping`, `@RequestMapping` | JPA `@Entity`, `@ManyToOne`, `@OneToMany` |
| C# / .NET | `.cs` | ASP.NET `[HttpGet]`, `[Route]` (two-pass) | EF Core `DbSet<X>`, domain namespace, `BaseEntity` |
| TypeScript | `.ts .tsx` | Express `app.get/post/...` | (none) |
| JavaScript | `.js .jsx` | Express `app.get/post/...` | (none) |

**Note for C# parser:** The class regex uses `(?:(?:abstract|sealed|partial|static)\s+)*class` — the `partial` modifier is critical for detecting `public partial class X` which is default in .NET code-gen.

---

## What to Improve?

Describe which parser you want to add or improve, and specify:
1. What language / file extension?
2. What framework patterns need extracting? (routes, entities, etc.)
3. What's the current failure mode? (0 classes, wrong routes, etc.)

I'll make targeted edits to `engine/parsers.py` following the contract above.
