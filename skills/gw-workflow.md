---
name: gw-workflow
description: Cross-service Google Workspace workflows — save email attachments to Drive, create calendar events from emails. Use when the user's request spans multiple Google services.
---

# Cross-Service Workflows

Combine `gw mail`, `gw cal`, and `gw drive` commands for complex workflows.

## Common Workflows

### Save email attachment to Drive
1. `gw mail attachments MESSAGE_ID --json` — List attachments
2. `gw mail to-drive MESSAGE_ID --attachment-id ATT_ID [--folder FOLDER_ID] --json` — Save to Drive

### Download and review attachment
1. `gw mail attachments MESSAGE_ID --json` — List attachments
2. `gw mail download MESSAGE_ID --attachment-id ATT_ID --out ./filename` — Download locally
3. Read the downloaded file to review contents

### Create meeting from email context
1. `gw mail read MESSAGE_ID --json` — Read email for context
2. `gw cal create --title "..." --start "..." --end "..." --meet --attendee EMAIL --json` — Create meeting

### Check availability then schedule
1. `gw cal free --date YYYY-MM-DD --account EMAIL --json` — Check free/busy for each participant
2. `gw cal create --title "..." --start "..." --end "..." --meet --json` — Create at available time

## Guidelines

- Always confirm the workflow plan with the user before executing
- When spanning accounts, be explicit about which account each operation uses
- For attachment to Drive, use `to-drive` (direct transfer, no local download needed)
