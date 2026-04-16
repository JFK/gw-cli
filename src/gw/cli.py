import click

from gw.auth import auth
from gw.calendar import cal
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
main.add_command(mail)


if __name__ == "__main__":
    main()
