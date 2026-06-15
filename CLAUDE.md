# gw-cli — Development Guide

## Overview

Google Workspace CLI for Claude Code. A Click-based, synchronous CLI (`gw`) over the Google
Calendar, Gmail, and Drive APIs with multi-account OAuth. Also ships as a Claude Code plugin.

- **PyPI package**: `google-workspace-cli` (the `gw-cli` name was taken) — import package and command are both `gw`
- **Plugin**: `.claude-plugin/` + `commands/gw-*.md` (7 skills)

Modules (`src/gw/`):
- `cli.py` — Click root group, global `--json` / `--account` flags
- `auth.py` — OAuth login/switch/list/remove, token store
- `calendar.py`, `gmail.py`, `drive.py` — per-service command groups
- `config.py` — config dir + account state
- `output.py` — `format_output` (text/JSON rendering)

## Development Workflow

See `.claude/rules/development-workflow.md` for the full flow (auto-loaded).

**Key sequence**: Issue → Branch → Implement → `/quality` → `/self-review` → PR → Merge

## Commands

```bash
uv sync --dev                    # Install deps (incl. dev)
uv run pytest tests/ -v          # Tests
uv run ruff check src/ tests/    # Lint
uv run ruff format src/ tests/   # Format
uv run pyright src/              # Type check
```

**Slash commands**: `/quality`, `/test`, `/self-review`, `/release patch|minor|major`

## Conventions

- Click commands; user output via `click.echo(format_output(...))`, never bare `print()`
- Honor global `--json` / `--account` from `ctx.obj`
- Errors: `RuntimeError` / `click.BadParameter` with an actionable recovery hint
- Never commit `credentials.json`, tokens, or `.env`; never log tokens
- Full rules: `.claude/rules/python.md` (auto-loaded)

## Versioning & Release

Version lives in `src/gw/__init__.py` (`pyproject.toml` reads it via `dynamic`). The two
`.claude-plugin/*.json` manifests carry their own `version` and must stay in sync.
`/release` bumps all three, tags `vX.Y.Z`, and the `Publish to PyPI` workflow publishes `google-workspace-cli`
via OIDC Trusted Publishing. See `.claude/rules/versioning.md`.

## Branch Strategy

- Branch from `master` for every issue: `{issue-number}-{type}/{description}`
- Conventional Commits; squash merge to `master`
