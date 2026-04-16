# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in gw-cli, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email: fumikazu.kiyota@gmail.com
3. Include a description of the vulnerability and steps to reproduce

You should receive a response within 48 hours.

## Security Design

### Credential Storage

- OAuth tokens and credentials are stored at `~/.config/google-workspace-cli/`
- All sensitive files (tokens, credentials, config) are set to `chmod 600` (owner-only read/write)
- Credentials and tokens are never included in CLI output or `--json` output

### OAuth Scopes

gw-cli requests the following OAuth scopes:

| Scope | Purpose |
|---|---|
| `calendar` | Read/write calendar events |
| `gmail.modify` | Read, label, and mark emails |
| `gmail.send` | Send and reply to emails |
| `drive` | Read/write Drive files and permissions |

### .gitignore

The following are excluded from version control:
- `credentials/` — OAuth client credentials
- `tokens/` — OAuth access/refresh tokens
- `.env` / `.env.*` — Environment variables
- `*.json` (except plugin config files)

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |
