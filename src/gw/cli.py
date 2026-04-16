import click


@click.group()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--account", default=None, help="Google account email to use")
@click.pass_context
def main(ctx: click.Context, output_json: bool, account: str | None) -> None:
    """gw - Google Workspace CLI for Claude Code."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = output_json
    ctx.obj["account"] = account


if __name__ == "__main__":
    main()
