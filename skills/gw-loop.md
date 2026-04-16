---
name: gw-loop
description: Set up periodic Google Workspace monitoring — unread email checks, upcoming calendar reminders, Drive file change detection. Use when the user wants to set up recurring checks or notifications with the /loop skill.
---

# Periodic Monitoring with /loop

Use the `/loop` skill to run gw-cli checks at regular intervals.

## Unread Email Monitor

Check for new unread emails every 5 minutes:

```
/loop 5m gw mail list --query "is:unread" --limit 10 --json
```

Behavior:
- Every 5 minutes, runs `gw mail list --query "is:unread" --json`
- Report new unread messages found
- If no new messages, stay silent

### With specific account:

```
/loop 5m gw mail list --query "is:unread" --account work@company.com --json
```

### With sender filter:

```
/loop 5m gw mail list --query "is:unread from:boss@company.com" --json
```

## Calendar Reminder

Check upcoming events every 30 minutes:

```
/loop 30m gw cal list --days 1 --json
```

Behavior:
- Show events happening in the next 24 hours
- Highlight events starting within 1 hour

## Drive File Monitor

Check for recently modified files every 10 minutes:

```
/loop 10m gw drive list --query "modifiedTime > 'YYYY-MM-DDTHH:MM:SS'" --json
```

## Multi-Account Monitoring

Monitor multiple accounts by running separate loops:

```
/loop 5m gw mail list --query "is:unread" --account personal@gmail.com --json
/loop 5m gw mail list --query "is:unread" --account work@company.com --json
```

## Workflow: Email + Calendar Morning Briefing

Run once at start of day:

```
/loop 60m gw-morning-briefing
```

The briefing combines:
1. `gw cal list --days 1 --json` — Today's schedule
2. `gw mail list --query "is:unread" --limit 10 --json` — Unread emails
3. Summarize both in a concise report

## Configuration Defaults

Set default check intervals and queries in config:

```bash
gw config set defaults.mail.check_query "is:unread"
gw config set defaults.mail.limit 20
gw config set defaults.calendar.days 1
```

## Tips

- Use `--json` flag for all loop commands so Claude Code can parse and summarize results
- Set shorter intervals (2-5m) for email, longer (15-30m) for calendar and drive
- Use Gmail search query syntax for targeted monitoring: `is:unread from:`, `has:attachment`, `subject:`
- Combine with `gw mail mark --read` to auto-acknowledge reviewed messages
