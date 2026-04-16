---
name: gw-mail
description: Gmail operations — list/read/send/reply to emails, manage labels, mark read/unread, handle attachments. Use when the user asks about email, messages, inbox, or attachments.
---

# Gmail Operations

Use the `gw mail` CLI for email operations. Always use `--json` for parsing results.

## Commands

- `gw mail list [--query "..."] [--limit N] [--since DATETIME] [--account EMAIL] --json` — List messages
- `gw mail read MESSAGE_ID [--account EMAIL] --json` — Read message (does NOT mark as read)
- `gw mail send --to EMAIL --subject "..." --body "..." [--account EMAIL]` — Send message
- `gw mail reply MESSAGE_ID --body "..." [--account EMAIL]` — Reply to message
- `gw mail labels [--account EMAIL] --json` — List labels
- `gw mail label MESSAGE_ID --add "LABEL" --remove "LABEL" [--account EMAIL]` — Modify labels
- `gw mail mark MESSAGE_ID --read [--account EMAIL]` — Mark as read
- `gw mail mark MESSAGE_ID --unread [--account EMAIL]` — Mark as unread
- `gw mail attachments MESSAGE_ID [--account EMAIL] --json` — List attachments
- `gw mail download MESSAGE_ID --attachment-id ATT_ID --out ./path [--account EMAIL]` — Download attachment
- `gw mail to-drive MESSAGE_ID --attachment-id ATT_ID [--folder FOLDER_ID] [--account EMAIL] --json` — Save attachment to Drive

## Guidelines

- Reading a message does NOT automatically mark it as read. Use `gw mail mark --read` explicitly.
- Always confirm before sending or replying to emails
- For unread mail checking: `gw mail list --query "is:unread" --json`
- Gmail search query syntax: is:unread, from:, to:, subject:, has:attachment, after:YYYY/MM/DD
- For loop-based checking, use `--since` to get only new messages
