---
paths:
  - "src/gw/__init__.py"
  - "pyproject.toml"
  - ".claude-plugin/plugin.json"
  - ".claude-plugin/marketplace.json"
---

# Version Management

## Single Source of Truth

- The canonical version is `__version__` in `src/gw/__init__.py`
- `pyproject.toml` uses `dynamic = ["version"]` with `[tool.hatch.version]` to read it — never set `version = "..."` in `pyproject.toml`
- The two Claude Code plugin manifests carry their own `version` and must be kept in sync:
  - `.claude-plugin/plugin.json` → `version`
  - `.claude-plugin/marketplace.json` → `plugins[0].version`
- `/release` bumps all three in lockstep

## SemVer Rules

Format: `MAJOR.MINOR.PATCH` (e.g. `0.2.3`)

| Change type | Bump | Example |
|-------------|------|---------|
| Breaking change | MAJOR | Removing/renaming a CLI command or flag |
| New feature (backward compatible) | MINOR | Adding a new `gw` subcommand |
| Bug fix, docs, refactor | PATCH | Fixing an error message |

While `MAJOR` is `0`, breaking changes bump MINOR instead.

## Conventional Commits → Version

| Commit prefix | Version bump |
|---------------|-------------|
| `feat` | MINOR (or PATCH if 0.x) |
| `fix`, `perf` | PATCH |
| `BREAKING CHANGE` footer or `!` suffix | MAJOR (or MINOR if 0.x) |
| `docs`, `chore`, `refactor`, `test`, `ci` | No bump |

## Release Flow

Use `/release patch|minor|major` to:
1. Bump `__version__` in `src/gw/__init__.py`
2. Sync `version` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
3. `uv lock` and `uv build` (verify)
4. Commit: `chore(release): vX.Y.Z`
5. Tag: `vX.Y.Z`
6. Push commit + tag → the `Publish to PyPI` workflow publishes to PyPI

### Test release

Manual trigger via GitHub Actions → `Publish to PyPI` → Run workflow → `testpypi`

## Release Infrastructure (Trusted Publishing)

Publishing uses PyPI's OIDC Trusted Publisher — **no API tokens**. Configure once:

- **PyPI project**: `google-workspace-cli`
- **Owner / repo**: `JFK/gw-cli`
- **Workflow**: `publish.yml`
- **Environments**: `pypi` (production) and `testpypi` — create both as GitHub Environments and register each as a Trusted Publisher on PyPI / TestPyPI
