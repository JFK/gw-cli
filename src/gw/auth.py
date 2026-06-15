from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import click
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from gw.config import DEFAULT_CONFIG_DIR, GwConfig

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive",
]


def _can_auto_open_browser() -> bool:
    """Whether auto-opening a browser is likely to reach the user.

    On WSL2 and headless hosts the OS default URL handler is usually wrong (e.g. a
    file manager) or absent, so an auto-opened consent page never appears. In those
    cases the caller should skip the auto-open and let the operator open the printed
    URL in any browser that can reach this host's localhost (a Windows browser
    reaches WSL2 localhost). On native desktops (macOS / Windows / Linux with a
    display) auto-open is the convenient one-step path.
    """
    if os.environ.get("WSL_DISTRO_NAME"):
        return False
    try:
        with open("/proc/version", encoding="utf-8") as fh:
            if "microsoft" in fh.read().lower():
                return False
    except OSError:
        pass
    if sys.platform.startswith("linux") and not (
        os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    ):
        return False
    return True


def _get_user_email(credentials) -> str:
    """Fetch the authenticated user's email via Gmail API."""
    service = build("gmail", "v1", credentials=credentials)
    profile = service.users().getProfile(userId="me").execute()
    return profile["emailAddress"]


def _resolve_config_dir(ctx: click.Context, config_dir: Path | None) -> Path:
    """Resolve config_dir from subcommand option, parent context, or default."""
    if config_dir is not None:
        return config_dir
    return ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)


_config_dir_option = click.option(
    "--config-dir",
    type=click.Path(path_type=Path),
    default=None,
    hidden=True,
    help="Config directory (default: ~/.config/google-workspace-cli)",
)


@click.group()
@click.pass_context
def auth(ctx: click.Context) -> None:
    """Manage Google accounts."""
    ctx.ensure_object(dict)


@auth.command()
@click.option("--credentials", required=True, type=click.Path(exists=True, path_type=Path))
@_config_dir_option
@click.pass_context
def login(ctx: click.Context, credentials: Path, config_dir: Path | None) -> None:
    """Add a Google account via OAuth login."""
    resolved_dir = _resolve_config_dir(ctx, config_dir)
    cfg = GwConfig(resolved_dir)

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials), SCOPES)

    try:
        # Loopback flow. Always print the consent URL explicitly (don't rely on
        # the library's default prompt message) and keep the local server
        # listening long enough for the operator to authorize. Only auto-open a
        # browser where one is likely to reach the user: on WSL2/headless the OS
        # default URL handler is often wrong (e.g. a file manager), so we skip the
        # auto-open and let the operator open the printed URL in any browser that
        # can reach this host's localhost (a Windows browser reaches WSL2 localhost).
        flow.run_local_server(
            port=0,
            open_browser=_can_auto_open_browser(),
            authorization_prompt_message=(
                "\nOpen this URL in your browser to authorize:\n\n{url}\n"
            ),
            timeout_seconds=300,
        )
    except Exception:
        # Last-resort manual paste (requires an interactive terminal for the prompt).
        auth_url, _ = flow.authorization_url(prompt="consent")
        click.echo(f"\nOpen this URL in your browser:\n\n{auth_url}\n")
        click.echo("After authorizing, you will be redirected to a localhost URL.")
        click.echo("Copy the FULL URL from the browser address bar and paste it here:\n")
        redirect_url = click.prompt("Redirect URL")
        flow.fetch_token(authorization_response=redirect_url)

    creds = flow.credentials
    email = _get_user_email(creds)

    dest_creds = cfg.credentials_dir / f"{email}.json"
    cfg.credentials_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(credentials, dest_creds)
    os.chmod(dest_creds, 0o600)

    cfg.tokens_dir.mkdir(parents=True, exist_ok=True)
    token_path = cfg.tokens_dir / f"{email}.json"
    token_path.write_text(creds.to_json())
    os.chmod(token_path, 0o600)

    cfg.add_account(email, f"credentials/{email}.json")
    click.echo(f"Logged in as {email}")


@auth.command("list")
@_config_dir_option
@click.pass_context
def list_accounts(ctx: click.Context, config_dir: Path | None) -> None:
    """List registered accounts."""
    resolved_dir = _resolve_config_dir(ctx, config_dir)
    cfg = GwConfig(resolved_dir)
    if not cfg.accounts:
        click.echo("No accounts registered. Run 'gw auth login' to add one.")
        return
    for acct in cfg.accounts:
        marker = " *" if acct["email"] == cfg.active_account else ""
        click.echo(f"  {acct['email']}{marker}")


@auth.command()
@_config_dir_option
@click.pass_context
def status(ctx: click.Context, config_dir: Path | None) -> None:
    """Show the active account."""
    resolved_dir = _resolve_config_dir(ctx, config_dir)
    cfg = GwConfig(resolved_dir)
    if cfg.active_account:
        click.echo(f"Active account: {cfg.active_account}")
    else:
        click.echo("No active account. Run 'gw auth login' to add one.")


@auth.command()
@click.argument("email")
@_config_dir_option
@click.pass_context
def switch(ctx: click.Context, email: str, config_dir: Path | None) -> None:
    """Switch the active account."""
    resolved_dir = _resolve_config_dir(ctx, config_dir)
    cfg = GwConfig(resolved_dir)
    cfg.switch_account(email)
    click.echo(f"Switched to {email}")


@auth.command()
@click.argument("email")
@_config_dir_option
@click.pass_context
def remove(ctx: click.Context, email: str, config_dir: Path | None) -> None:
    """Remove a registered account."""
    resolved_dir = _resolve_config_dir(ctx, config_dir)
    cfg = GwConfig(resolved_dir)
    cfg.remove_account(email)
    click.echo(f"Removed {email}")


def build_service(cfg: GwConfig, email: str, api_name: str, api_version: str):
    """Build an authenticated Google API service for the given account."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    token_path = cfg.get_token_path(email)
    if not token_path.exists():
        raise RuntimeError(
            f"No token found for {email}. Run 'gw auth login --credentials <path>' first."
        )

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
            os.chmod(token_path, 0o600)
        except Exception as exc:
            raise RuntimeError(
                f"Token refresh failed for {email}. "
                "Run 'gw auth login --credentials <path>' to re-authenticate."
            ) from exc

    return build(api_name, api_version, credentials=creds)
