# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- `gw auth login` now prints actionable first-time-setup guidance (link to `/gw-setup`
  and the README Setup guide) when the `--credentials` file is missing, instead of a raw
  "path does not exist" error. `gw auth list` / `gw auth status` point first-time users to
  setup as well.

## [0.1.0]

### Added
- Initial release: multi-account Google Workspace CLI (`gw`) for Calendar, Gmail, and Drive
  with OAuth, plus a Claude Code plugin with 7 skills.
- PyPI packaging: published as `google-workspace-cli` via hatchling with the version sourced from
  `src/gw/__init__.py`.
- GitHub Actions: `ci.yml` (lint + type check + test on Python 3.10/3.11/3.12) and
  `publish.yml` (OIDC Trusted Publishing to PyPI/TestPyPI + GitHub Release).
- Claude Code dev config: `CLAUDE.md`, `.claude/rules/`, and `.claude/commands/`
  (`/quality`, `/test`, `/self-review`, `/release`).
- `CONTRIBUTING.md`.

[Unreleased]: https://github.com/JFK/gw-cli/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/JFK/gw-cli/releases/tag/v0.1.0
