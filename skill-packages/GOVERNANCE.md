# Governance — Reverse Engineer Skill

## Ownership

| Role | Responsibility |
|------|---------------|
| **Skill Owner** | Approves breaking changes, owns versioning |
| **Contributor** | Submits PRs against `main`; follows this guide |
| **Consumer** | Uses packaged ZIPs; reports issues via the owner |

---

## Versioning (Semantic)

```
MAJOR.MINOR.PATCH
  │     │     └── Bug fixes, doc updates, non-breaking tweaks
  │     └──────── New features (backwards compatible)
  └────────────── Breaking changes (schema change, removed param, renamed file)
```

Current version: **3.0.0**

Update `CHANGELOG.md` in ALL THREE packages on every release.

---

## Branching

| Branch | Purpose |
|--------|---------|
| `main` | Stable, always deployable |
| `feat/*` | New features |
| `fix/*` | Bug fixes |
| `release/vX.Y.Z` | Release prep |

---

## Release Checklist

- [ ] All tests pass: `python -m pytest` (if tests exist)
- [ ] Syntax-check engine: `python -c "import engine.pipeline"`
- [ ] Run smoke test: `python reverse_engineer_skill.py <any-public-repo> --heuristic`
- [ ] Bump version in `CHANGELOG.md` for all 3 packages
- [ ] Run `python build_packages.py` — verify 3 ZIPs are created
- [ ] Tag the commit: `git tag v3.x.x`

---

## Adding New Languages / Parsers

1. Add parser in `engine/parsers.py` following the existing pattern
2. Add extension to `SUPPORTED_EXTENSIONS` in `engine/loaders.py`
3. Update `ARCHITECTURE.md` and `COMPONENTS.md`
4. Bump MINOR version

---

## Breaking Changes Policy

- Document in CHANGELOG with migration guide
- Provide 1 MINOR version deprecation notice before removal
- Update ALL THREE package `INSTALL.md` files

---

## Support

- Bugs: open an issue with the output of `manifest.json` attached
- Questions: read `ARCHITECTURE.md` first
