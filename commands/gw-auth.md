---
name: gw-auth
description: Manage Google Workspace accounts — login, list, switch, status, remove. Use when the user wants to add, switch, or manage Google accounts for gw-cli.
---

# Google Workspace Account Management

Use the `gw auth` CLI to manage Google accounts.

## Commands

- `gw auth login --credentials <path>` — Add a new Google account (opens browser for OAuth)
- `gw auth list` — Show all registered accounts (active marked with *)
- `gw auth status` — Show the current active account
- `gw auth switch <email>` — Switch the active account
- `gw auth remove <email>` — Remove an account

## Usage

When the user wants to add an account, they need a `credentials.json` from Google Cloud Console.
Run `gw auth login --credentials ./credentials.json` and guide them through the process.

Always run `gw auth status` first to confirm which account is active before performing operations.
