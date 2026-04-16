# gw-cli

Google Workspace CLI for Claude Code. Manage Calendar, Gmail, and Drive across multiple Google accounts.

## Install

```bash
pip install git+https://github.com/<user>/gw-cli.git
```

## Setup

1. Create an OAuth client in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Application type: Desktop app
   - Enable Calendar API, Gmail API, Drive API

2. Download the credentials JSON file

3. Add your account:
```bash
gw auth login --credentials ./credentials.json
```

4. Verify:
```bash
gw auth status
```

## Usage

```bash
# Calendar
gw cal list --days 7
gw cal create --title "Meeting" --start "2026-04-17 10:00" --end "2026-04-17 11:00" --meet

# Gmail
gw mail list --query "is:unread"
gw mail read MESSAGE_ID
gw mail send --to "user@example.com" --subject "Hello" --body "Hi there"

# Drive
gw drive list
gw drive upload ./file.pdf
gw drive create --type doc --title "New Document"

# Multi-account
gw auth login --credentials ./work-credentials.json    # Add another account
gw auth switch work@company.com                         # Switch active account
gw mail list                                            # Uses active account
gw mail list --account personal@gmail.com               # Override for one command
```

## Claude Code Plugin

Install as a Claude Code plugin for natural language interaction:

```bash
claude plugin add <github-url>
```

Then use naturally: "Show me my unread emails", "Schedule a meeting tomorrow at 10am with Meet".

## Config

```bash
gw config show
gw config set defaults.calendar.days 14
gw config set defaults.mail.limit 50
```

Config stored at `~/.config/google-workspace-cli/config.json`.

## License

MIT
