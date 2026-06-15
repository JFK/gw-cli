# Contributing

## Setup

```bash
git clone https://github.com/JFK/gw-cli.git
cd gw-cli
uv sync --dev
```

Run the CLI locally:

```bash
uv run gw --help
```

## Development with Claude Code

This project is developed with [Claude Code](https://claude.com/claude-code). Slash commands automate the workflow:

| Command | Description |
|---------|-------------|
| `/quality` | Run lint, format check, type check, tests |
| `/test` | Run the test suite |
| `/self-review` | Pre-PR review (correctness, security, coverage, etc.) |
| `/release patch\|minor\|major` | Bump version, tag, publish to PyPI, create GitHub Release |

### Recommended flow

```
# ... implement ...
/quality            # All checks pass?
/self-review        # Ready for PR?
```

## Workflow

1. Pick an issue from the [Issue Tracker](https://github.com/JFK/gw-cli/issues)
2. Create a branch: `git checkout -b {issue-number}-{type}/{description} master`
3. Implement (commit frequently, Conventional Commits)
4. Run `/quality` → `/self-review`
5. Push and create a PR
6. CI must pass (lint + test on Python 3.10/3.11/3.12)
7. Squash merge to `master`

## Commit Convention

```
<type>(<scope>): <subject>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`

## Quality Checks

```bash
uv run ruff check src/ tests/   # Lint
uv run ruff format src/ tests/  # Format
uv run pyright src/             # Type check
uv run pytest tests/ -v         # Test
```

## Code Style

- Python 3.10+, type hints required
- Click commands; output via `format_output`, never bare `print()`
- Google-style docstrings on public functions and commands
- Errors via `RuntimeError` / `click.BadParameter` with a recovery hint
- Never commit credentials/tokens; never log secrets

See `.claude/rules/python.md` for the full coding rules.

## Releasing

Maintainers only. `/release patch|minor|major` bumps `src/gw/__init__.py` plus the two
`.claude-plugin/*.json` manifests, tags `vX.Y.Z`, and pushes. The `Publish to PyPI` workflow
publishes the `google-workspace-cli` package via OIDC Trusted Publishing (no API tokens). See
`.claude/rules/versioning.md`.
