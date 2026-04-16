---
name: gw-setup
description: Guide users through Google Cloud Console setup for gw-cli — project creation, API enablement, OAuth consent screen, credentials, and first login. Use when the user wants to set up gw-cli for the first time or add a new Google account.
---

# gw-cli Setup Guide

Walk the user step-by-step through Google Cloud Console setup and first login.

## Prerequisites

- `gcloud` CLI installed and authenticated
- `gw-cli` installed (`pip install -e .` or `pip install git+...`)

## Step 1: Create GCP Project (or choose existing)

```bash
gcloud projects create gw-cli-$(date +%Y%m%d) --name="gw-cli"
gcloud config set project gw-cli-YYYYMMDD
```

If the project ID is taken, append a random suffix.

## Step 2: Enable APIs

```bash
gcloud services enable calendar-json.googleapis.com gmail.googleapis.com drive.googleapis.com --project=PROJECT_ID
```

## Step 3: OAuth Consent Screen

This must be done in the browser:

```
https://console.cloud.google.com/apis/credentials/consent?project=PROJECT_ID
```

Settings:
- **User Type**: External
- **App name**: `gw-cli`
- **User support email**: user's email
- **Developer contact email**: user's email
- Scopes: skip (auto-requested at login)

**IMPORTANT: Add test users**
- Go to "Test users" section
- Click "+ ADD USERS"
- Add the Gmail address that will be used with gw-cli
- Without this, login will fail with `Error 403: access_denied`

## Step 4: Create OAuth Client ID

Browser:
```
https://console.cloud.google.com/apis/credentials/oauthclient?project=PROJECT_ID
```

Settings:
- **Application type**: Desktop app
- **Name**: `gw-cli`

After creation, download the JSON file.

## Step 5: Save Credentials

Recommend saving to `~/.config/gw-cli/ACCOUNT_NAME.json` for organization.

## Step 6: Login

```bash
gw auth login --credentials PATH_TO_CREDENTIALS_JSON
```

### WSL2 / Remote Environment

If the local server callback fails (localhost connection refused), gw-cli automatically falls back to manual mode:
1. Open the displayed URL in your browser
2. Authorize the app
3. Copy the full URL from the browser address bar (the localhost page that fails to load)
4. Paste it into the terminal

## Step 7: Verify

```bash
gw auth status
gw cal list --days 3
gw mail list --query "is:unread" --limit 5
```

## Adding More Accounts

Each Google account needs its own credentials.json from its own GCP project (or the same project if the admin allows it).

```bash
gw auth login --credentials ~/.config/gw-cli/work-account.json
gw auth list
gw auth switch work@company.com
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Error 403: access_denied` | Add your email to OAuth consent screen test users |
| `ERR_CONNECTION_REFUSED` on callback | WSL2 issue — gw-cli auto-falls back to manual URL paste |
| `HttpError 401` on login | Enable the required APIs (Step 2) |
| `Token has been expired or revoked` | Run `gw auth login --credentials <path>` again |
