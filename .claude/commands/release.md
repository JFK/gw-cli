---
description: Bump version, commit, tag, and push a release
arguments:
  - name: level
    description: "patch, minor, or major"
    required: true
---

Release gw-cli with a version bump.

## Prerequisites

Before releasing, ensure:
1. `/quality` has been run and passes
2. Current branch is `master`

## Steps

### 1. Validate preconditions

- Argument: `$ARGUMENTS` (must be `patch`, `minor`, or `major`)
- Verify current branch is `master` (`git branch --show-current`). Abort if not.

### 2. Read current version

Read `src/gw/__init__.py` and extract `__version__`.

### 3. Calculate new version

Apply SemVer bump:
- `patch`: 0.1.0 → 0.1.1
- `minor`: 0.1.0 → 0.2.0
- `major`: 0.1.0 → 1.0.0

(While MAJOR is 0, treat breaking changes as `minor`.)

### 4. Update version in all three locations

Keep these in lockstep (see `.claude/rules/versioning.md`):
1. `src/gw/__init__.py` → `__version__`
2. `.claude-plugin/plugin.json` → `version`
3. `.claude-plugin/marketplace.json` → `plugins[0].version`

### 5. Lock and build

```bash
uv lock
uv build
```

Verify the build produces `dist/google_workspace_cli-X.Y.Z-*.whl` and `dist/google_workspace_cli-X.Y.Z.tar.gz`.

### 6. Commit and tag

```bash
git add src/gw/__init__.py .claude-plugin/plugin.json .claude-plugin/marketplace.json uv.lock
git commit -m "chore(release): vX.Y.Z"
git tag vX.Y.Z
```

### 7. Push

```bash
git push && git push --tags
```

This triggers the `Publish to PyPI` workflow → publishes `google-workspace-cli` to PyPI and creates a GitHub Release.

### 8. Update CHANGELOG and write release notes

1. `git log --oneline vPREVIOUS..vX.Y.Z` to review commits in this release.
2. Add a new section to the top of `CHANGELOG.md` for `vX.Y.Z`.
3. Write release notes grouped as **New features** / **Improvements** / **Bug fixes** (omit empty sections), referencing issue/PR numbers with `#N`. Add a `## Migration` section if any commit is a breaking change.

### 9. Report

Print the new version, the GitHub Release link, and the Actions run URL.
