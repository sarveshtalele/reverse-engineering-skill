# Changelog — Claude Code Skill

## [3.0.0] — 2026-05-28

### Added
- `.claude/skills/reverse-engineer/SKILL.md` — skill registered in the current Claude Code `skills/` format
- Global install instructions (`~/.claude/skills/reverse-engineer/`) for cross-project use
- Block diagram SVG output (`{repo}_block_diagram.svg`) — layered architecture with tinted fills and class counts
- Dependency graph SVG output (`{repo}_dependency_graph.svg`) — hierarchical SOURCES/HUBS/TARGETS/ISOLATED column layout
- Web Forms (`.aspx.cs`) detection in block diagram layer classification
- Broader class-name patterns for service/controller detection across frameworks (Java, .NET, Python)
- Step 5c in SKILL.md — Architecture Block Diagram Walkthrough section
- `INSTALL.md` rewritten end-to-end with global vs. project-level install options

### Changed
- **Step 7 (write AI content) is now automatic** — Claude Code writes directly into `_report.md` without asking for confirmation
- Slash command runs `python reverse_engineer_skill.py $ARGUMENTS --heuristic` (was interactive prompt)
- Interactive vis.js dependency graph replaced with static SVG (reliable across all browsers)
- Graphviz DOT source removed from `report.md` (SVG image used instead)
- Output file count updated: 7 files (added `_block_diagram.svg` and `_dependency_graph.svg`)
- SDD section count corrected: 14 sections (was 13)
- Pipeline stage count updated: 9 stages

### Fixed
- `None` iteration crash in `generate_block_diagram_dot()` when edges list was absent
- False-positive class detection: `"page"` no longer matches `"homepage"`
- JSON extraction now uses brace-balanced parsing (robust against nested objects)
- `KeyboardInterrupt` and `SystemExit` now propagate correctly
- Invalid mode input in CLI now warns instead of silently defaulting

## [2.0.0] — 2026-01-15

### Added
- Initial `.claude/commands/reverse-engineer.md` slash command
- 8-step agent workflow
- Heuristic-only static analysis

## [1.0.0] — earlier

- Prototype slash command
