import json as json_module
import sys

import click

from gw.auth import auth
from gw.calendar import cal
from gw.config import DEFAULT_CONFIG_DIR, GwConfig
from gw.drive import drive
from gw.gmail import mail


@click.group()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--account", default=None, help="Google account email to use")
@click.option(
    "--config-dir",
    type=click.Path(),
    default=None,
    hidden=True,
    help="Config directory override (for testing)",
)
@click.pass_context
def main(ctx: click.Context, output_json: bool, account: str | None, config_dir: str | None) -> None:
    """gw - Google Workspace CLI for Claude Code."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = output_json
    ctx.obj["account"] = account
    if config_dir:
        from pathlib import Path
        ctx.obj["config_dir"] = Path(config_dir)


main.add_command(auth)
main.add_command(cal)
main.add_command(drive)
main.add_command(mail)


@click.group("config")
@click.pass_context
def config_group(ctx: click.Context) -> None:
    """Manage gw-cli configuration."""
    pass


@config_group.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Show current configuration."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    data = {
        "active_account": cfg.active_account,
        "accounts": [a["email"] for a in cfg.accounts],
        "defaults": cfg.defaults,
        "loop": cfg.loop,
    }
    click.echo(json_module.dumps(data, indent=2, ensure_ascii=False))


@config_group.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_config(ctx: click.Context, key: str, value: str) -> None:
    """Set a config value (e.g. defaults.calendar.days 14)."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)

    parts = key.split(".")
    if len(parts) == 3 and parts[0] == "defaults":
        converted: object = value
        try:
            converted = int(value)
        except ValueError:
            try:
                converted = float(value)
            except ValueError:
                if value.lower() in ("true", "false"):
                    converted = value.lower() == "true"
                elif value.lower() == "null":
                    converted = None

        cfg.set_default(parts[1], parts[2], converted)
        cfg.save()
        click.echo(f"Set {key} = {converted}")
    else:
        click.echo(f"Unknown config key: {key}", err=True)
        raise SystemExit(1)


main.add_command(config_group)


def cli() -> None:
    """Console-script entry point with friendly top-level error handling.

    Click only renders ClickException subclasses nicely; uncaught RuntimeError
    or ValueError (raised by build_service, resolve_account, config loading,
    etc.) would otherwise surface as a raw Python traceback. Catch those here
    and report a one-line error with a non-zero exit code.
    """
    try:
        main(standalone_mode=False)
    except click.ClickException as exc:
        exc.show()
        sys.exit(exc.exit_code)
    except click.exceptions.Abort:
        click.echo("Aborted.", err=True)
        sys.exit(1)
    except (RuntimeError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
