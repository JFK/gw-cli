---
paths:
  - "src/**"
  - "tests/**"
---

# Python Coding Rules

## Style
- snake_case for functions/variables, PascalCase for classes
- Type hints required on all function signatures
- `from __future__ import annotations` at the top of modules using new-style unions on 3.10
- Google-style docstrings on public functions and Click commands (the docstring is the `--help` text)
- Target Python 3.10+; keep syntax compatible with 3.10/3.11/3.12

## CLI (Click)
- Every command is a `@click.command` / `@click.group` with explicit `@click.option` / `@click.argument`
- User-facing output goes through `click.echo`, formatted via `gw.output.format_output` — never bare `print()`
- Respect the global `--json` / `--account` flags from `ctx.obj`; pass them into `format_output`
- Validate user input with `click.BadParameter`, not bare exceptions

## Error Handling
- Raise `RuntimeError` (or `click.BadParameter` for bad input) with an actionable message; the top-level CLI maps these to friendly errors
- Never swallow exceptions silently — re-raise or surface a clear message
- Auth/credential failures must tell the user how to recover (e.g. "Run 'gw auth login'")

## Google API
- Build services lazily; reuse credentials from the token store
- Never assume a field exists in an API response — use `.get(...)` with sensible defaults
- Request only the scopes a command needs

## Security
- Never commit `credentials.json`, tokens, or `.env` (see `.gitignore`)
- Never log access/refresh tokens or full credential payloads
- Store tokens under the config dir with restrictive permissions; never write secrets to `os.environ`

## Testing
- `pytest`; mock the Google API client (no live network calls in unit tests)
- Use Click's `CliRunner` for command tests; pass `--config-dir` to isolate state
- Test error paths (missing account, bad input, API failure), not just the happy path
- Every changed/added code path needs a test
