Perform a pre-PR self-review of all changes.

## Role

You are an AI code reviewer. Review only the modified code in the diff. Prioritize high-signal feedback over quantity.

## Review the diff

```bash
git diff master...HEAD
```

If no diff, review `git diff HEAD~1`.

## Review for (in priority order)

1. **Correctness** — bugs, edge cases, broken logic, unreachable code
2. **Security** — credential/token leaks, secrets in logs, unsafe defaults, committing `credentials.json`/tokens
3. **Error handling** — exceptions swallowed, auth errors not surfacing a recovery hint, missing input validation (`click.BadParameter`)
4. **Test coverage** — every changed/added code path must have a test. Check: new branches, error paths, edge cases
5. **CLI behavior** — `--json` / `--account` honored, output routed through `format_output`, help text accurate
6. **Consistency** — patterns used differently across files, naming inconsistencies with existing code

## Rules

- Only comment on lines that were changed in the diff
- Be specific and actionable — suggest concrete fixes
- Do not nitpick formatting (ruff handles it)

## Severity

| Marker | Meaning | Action |
|--------|---------|--------|
| `[C]` | Bug, security hole, data loss | Must fix before merge |
| `[W]` | Risk, missing guard, edge case | Should fix |
| `[I]` | Readability, minor improvement | Fix or justify |

## Output

```markdown
## Self-review: X files changed

`[C]` file:line — Description. **Fix:** concrete suggestion.

### Verdict: Ready / Needs fixes
```

If no significant issues: state "Changes look good" with a brief summary.
