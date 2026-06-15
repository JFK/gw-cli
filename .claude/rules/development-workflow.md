---
paths:
  - "**"
---

# Development Workflow

## Flow

1. **Start**: `gh issue view <number>` → understand the task
2. **Branch**: `git checkout -b {issue-number}-{type}/{description} master`
3. **Implement**: Write code keeping self-review criteria in mind from the start
4. **Quality**: Run `/quality` (lint, format, type-check, tests)
5. **Self-review**: Run `/self-review` — fix all `[C]` and `[W]` findings
6. **PR**: Create PR linking the issue. Only when the user explicitly asks.
7. **Merge**: Only after user approval. Never auto-merge.

## Commit Discipline

- Commit frequently with meaningful messages
- Follow Conventional Commits: `<type>(<scope>): <subject>`
- Each commit should be atomic — one logical change per commit
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`

## PR Rules

- Run `/quality` → `/self-review` before every PR
- PR title: Under 70 characters, Conventional Commits format
- Squash merge to `master`
- Delete branch after merge
- Never skip self-review before merge
