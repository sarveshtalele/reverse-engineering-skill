# Changelog — GitHub Copilot Skill

## [3.0.0] — 2026-05-28

### Added
- `--heuristic` flag passed automatically so the script skips the interactive mode prompt in the Copilot-opened terminal
- Output file list updated to include `_block_diagram.svg` and `_dependency_graph.svg`
- Step 2b fallback (manual analysis path when script is not found)
- VS Code `settings.json` configuration instructions for enabling prompt files
- Troubleshooting table in `INSTALL.md`

### Changed
- **Step 6 (write AI content) is now automatic** — Copilot writes directly into `_report.md` without asking for confirmation
- Step 2 now runs `python reverse_engineer_skill.py <URL> --heuristic` directly (was interactive)
- INSTALL.md rewritten end-to-end with 7-step guide, prerequisites table, and troubleshooting

### Fixed
- Completion report in Step 7 now lists all 7 output files (added SVG files that were missing)
- Prompt file picker instructions updated for VS Code 1.90+ prompt attachment flow

## [2.0.0] — 2026-01-15

### Added
- Initial `.github/prompts/reverse-engineer.prompt.md` prompt file
- 7-step agent workflow (validate URL → run script → read SDD → AI analysis → write report → report completion)
- Manual fallback path (Step 2b) when `reverse_engineer_skill.py` is not found

## [1.0.0] — earlier

- Placeholder prompt file for GitHub Copilot Chat integration
