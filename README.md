# gw-cli

Google Workspace CLI for Claude Code. Manage Calendar, Gmail, and Drive across multiple Google accounts.

## Features

- **Multi-account support** — Register multiple Google accounts (personal, work, client projects) and switch between them instantly
- **Calendar** — List, create, update, delete events. Google Meet setup. Free/busy check across accounts
- **Gmail** — Search, read, send, reply. Label management. Mark read/unread. Attachment download and save to Drive
- **Drive** — List, search, upload, create Google Docs/Sheets/Slides. Share/unshare files
- **Claude Code integration** — All commands support `--json` output for seamless skill parsing
- **Periodic monitoring** — Use with `/loop` for unread email checks, calendar reminders
- **WSL2 compatible** — Automatic fallback to manual OAuth flow when localhost callback is unreachable

## Install

```bash
pip install git+https://github.com/JFK/gw-cli.git
```

Or clone and install locally:

```bash
git clone https://github.com/JFK/gw-cli.git
cd gw-cli
pip install -e .
```

## Setup

### 1. Create GCP Project

```bash
gcloud projects create gw-cli-$(date +%Y%m%d) --name="gw-cli"
gcloud config set project gw-cli-YYYYMMDD
```

### 2. Enable APIs

```bash
gcloud services enable calendar-json.googleapis.com gmail.googleapis.com drive.googleapis.com --project=PROJECT_ID
```

### 3. OAuth Consent Screen

Open in browser: `https://console.cloud.google.com/apis/credentials/consent?project=PROJECT_ID`

- User Type: **External**
- App name: `gw-cli`
- Add your email as a **test user** (required, otherwise login fails with 403)

### 4. Create OAuth Client

Open in browser: `https://console.cloud.google.com/apis/credentials/oauthclient?project=PROJECT_ID`

- Application type: **Desktop app**
- Download the JSON file

### 5. Login

```bash
gw auth login --credentials ./credentials.json
```

On WSL2/remote environments, the tool automatically falls back to manual URL paste mode when the localhost callback is unreachable.

### 6. Verify

```bash
gw auth status
gw cal list --days 3
gw mail list --query "is:unread" --limit 5
```

## Usage

```bash
# Calendar
gw cal list --days 7
gw cal create --title "Meeting" --start "2026-04-17 10:00" --end "2026-04-17 11:00" --meet
gw cal create --title "1on1" --start "2026-04-18 14:00" --end "2026-04-18 14:30" --meet --attendee colleague@example.com
gw cal free --date 2026-04-17
gw cal delete EVENT_ID

# Gmail
gw mail list --query "is:unread"
gw mail read MESSAGE_ID
gw mail send --to "user@example.com" --subject "Hello" --body "Hi there"
gw mail reply MESSAGE_ID --body "Thanks!"
gw mail mark MESSAGE_ID --read
gw mail attachments MESSAGE_ID
gw mail to-drive MESSAGE_ID --attachment-id ATT_ID --folder FOLDER_ID

# Drive
gw drive list
gw drive list --query "name contains 'report'"
gw drive upload ./file.pdf
gw drive create --type doc --title "New Document"
gw drive share FILE_ID --email user@example.com --role writer
gw drive unshare FILE_ID --email user@example.com

# Multi-account
gw auth login --credentials ./work-credentials.json
gw auth list
gw auth switch work@company.com
gw mail list                                    # Uses active account
gw mail list --account personal@gmail.com       # Override for one command

# Config
gw config show
gw config set defaults.calendar.days 14
gw config set defaults.mail.limit 50
```

## Output

All commands support `--json` for machine-readable output:

```bash
gw cal list --json
gw mail list --query "is:unread" --json
```

Human-readable output always shows the active account:

```
[fumikazu.kiyota@gmail.com] 
  evt1 | Team standup | 2026-04-17T10:00:00+09:00 | ...
```

## Claude Code Plugin

Install as a Claude Code plugin:

```bash
claude plugin add github:JFK/gw-cli
```

Then use naturally:
- "Show me my unread emails"
- "Schedule a meeting tomorrow at 10am with Meet"
- "Save that email attachment to Drive"
- "What's on my calendar this week?"

## Periodic Monitoring

Use with the `/loop` skill for continuous monitoring:

```
/loop 5m gw mail list --query "is:unread" --json
/loop 30m gw cal list --days 1 --json
```

## Config

Config stored at `~/.config/google-workspace-cli/config.json`.

Credentials and tokens are stored per account:

```
~/.config/google-workspace-cli/
├── config.json
├── credentials/
│   └── user@gmail.com.json
└── tokens/
    └── user@gmail.com.json
```

## License

MIT
