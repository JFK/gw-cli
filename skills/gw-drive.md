---
name: gw-drive
description: Google Drive operations — list/search files, upload, create Google Docs/Sheets/Slides, manage sharing. Use when the user asks about files, documents, Drive, or sharing.
---

# Google Drive Operations

Use the `gw drive` CLI for Drive operations. Always use `--json` for parsing results.

## Commands

- `gw drive list [--folder FOLDER_ID] [--query "..."] [--account EMAIL] --json` — List files
- `gw drive upload FILE_PATH [--folder FOLDER_ID] [--account EMAIL] --json` — Upload file
- `gw drive create --type doc|sheet|slide|form --title "..." [--folder FOLDER_ID] [--account EMAIL] --json` — Create Google Doc/Sheet/Slide/Form
- `gw drive share FILE_ID --email EMAIL --role reader|writer|commenter [--account EMAIL]` — Share file
- `gw drive unshare FILE_ID --email EMAIL [--account EMAIL]` — Remove sharing

## Guidelines

- Drive search query syntax: `name contains 'keyword'`, `mimeType = 'application/pdf'`
- Always confirm before sharing or removing sharing
- Present file lists with name, type, modified date, and link
- For folder operations, use the folder ID (visible in the Drive URL)
