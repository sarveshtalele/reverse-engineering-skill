# Changelog — Agent SDK Skill

## [3.0.0] — 2026-05-28

### Added
- `ReverseEngineerAgent` class with `.run(url)` method returning a structured dict
- `mode` parameter: `"heuristic"` (no key, default) or `"ai"` (Claude API tool-use loop)
- `model` parameter: configurable Claude model (default: `claude-sonnet-4-6`)
- `skill_manifest.json` — JSON Schema tool definition for Claude tool-use conversations
- Structured return dict with `output_files`, `metrics`, `summary`, `ai_narrative`
- CLI entry point with `--ai` and `--model=` flags
- Graceful fallback: auto-switches to heuristic if `ANTHROPIC_API_KEY` is not set in AI mode
- `python-dotenv` support (optional) for loading API key from `.env` file
- Full AI mode tool-use loop: 2-turn Anthropic Messages conversation
  - Turn 1: Claude calls `reverse_engineer_repo` tool
  - Tool execution: runs `engine/pipeline.py` and returns SDD JSON
  - Turn 2: Claude reads results and produces AI narrative
- `_build_result()` static method normalises raw pipeline output into the public return shape
- Reads `_sdd.json` directly to populate `metrics` and `summary` if pipeline result is incomplete

### Changed
- Agent uses `claude-sonnet-4-6` by default (configurable via `model=` param)
- Tool schema loaded from `skill_manifest.json` at runtime (with inline fallback)

## [1.0.0] — earlier

- Initial agent wrapper (prototype)
