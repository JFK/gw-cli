from __future__ import annotations

import mimetypes
from pathlib import Path

import click

from gw.auth import build_service
from gw.config import DEFAULT_CONFIG_DIR, GwConfig
from gw.output import format_output

GOOGLE_DOC_TYPES = {
    "doc": "application/vnd.google-apps.document",
    "sheet": "application/vnd.google-apps.spreadsheet",
    "slide": "application/vnd.google-apps.presentation",
    "form": "application/vnd.google-apps.form",
}


@click.group()
@click.pass_context
def drive(ctx: click.Context) -> None:
    """Google Drive operations."""
    pass


@drive.command("list")
@click.option("--folder", default=None, help="Folder ID to list")
@click.option("--query", default=None, help="Drive search query")
@click.pass_context
def list_files(ctx: click.Context, folder: str | None, query: str | None) -> None:
    """List files in Drive."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "drive", "v3")

    q_parts = []
    if folder:
        q_parts.append(f"'{folder}' in parents")
    if query:
        q_parts.append(query)
    q_parts.append("trashed = false")
    q = " and ".join(q_parts)

    result = service.files().list(
        q=q, fields="files(id,name,mimeType,modifiedTime,size,webViewLink)",
        orderBy="modifiedTime desc", pageSize=50,
    ).execute()

    files = []
    for f in result.get("files", []):
        files.append({
            "id": f["id"], "name": f["name"], "type": f["mimeType"],
            "modified": f.get("modifiedTime", ""), "size": f.get("size", ""),
            "link": f.get("webViewLink", ""),
        })

    click.echo(format_output(files, output_json=output_json, account=account))


@drive.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--folder", default=None, help="Destination folder ID")
@click.pass_context
def upload(ctx: click.Context, file_path: str, folder: str | None) -> None:
    """Upload a file to Drive."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    from googleapiclient.http import MediaFileUpload

    service = build_service(cfg, account, "drive", "v3")
    path = Path(file_path)
    mime_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"

    file_metadata: dict = {"name": path.name}
    if folder:
        file_metadata["parents"] = [folder]

    media = MediaFileUpload(str(path), mimetype=mime_type)
    result = service.files().create(
        body=file_metadata, media_body=media, fields="id,name,webViewLink"
    ).execute()

    click.echo(format_output({
        "id": result["id"], "name": result["name"], "link": result.get("webViewLink", ""),
    }, output_json=output_json, account=account))


@drive.command()
@click.option("--type", "doc_type", required=True, type=click.Choice(list(GOOGLE_DOC_TYPES.keys())))
@click.option("--title", required=True)
@click.option("--folder", default=None, help="Destination folder ID")
@click.pass_context
def create(ctx: click.Context, doc_type: str, title: str, folder: str | None) -> None:
    """Create a new Google Doc/Sheet/Slide."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "drive", "v3")
    file_metadata: dict = {"name": title, "mimeType": GOOGLE_DOC_TYPES[doc_type]}
    if folder:
        file_metadata["parents"] = [folder]

    result = service.files().create(body=file_metadata, fields="id,name,webViewLink").execute()

    click.echo(format_output({
        "id": result["id"], "name": result["name"], "link": result.get("webViewLink", ""),
    }, output_json=output_json, account=account))


@drive.command()
@click.argument("file_id")
@click.option("--email", required=True, help="Email to share with")
@click.option("--role", required=True, type=click.Choice(["reader", "writer", "commenter"]))
@click.pass_context
def share(ctx: click.Context, file_id: str, email: str, role: str) -> None:
    """Share a file."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "drive", "v3")
    service.permissions().create(
        fileId=file_id, body={"type": "user", "role": role, "emailAddress": email},
    ).execute()
    click.echo(format_output(f"Shared {file_id} with {email} as {role}.", output_json=output_json, account=account))


@drive.command()
@click.argument("file_id")
@click.option("--email", required=True, help="Email to remove sharing")
@click.pass_context
def unshare(ctx: click.Context, file_id: str, email: str) -> None:
    """Remove sharing from a file."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "drive", "v3")
    perms = service.permissions().list(
        fileId=file_id, fields="permissions(id,emailAddress,role)"
    ).execute()

    perm_id = None
    for p in perms.get("permissions", []):
        if p.get("emailAddress", "").lower() == email.lower():
            perm_id = p["id"]
            break

    if perm_id is None:
        click.echo(format_output(f"No permission found for {email}.", output_json=output_json, account=account))
        return

    service.permissions().delete(fileId=file_id, permissionId=perm_id).execute()
    click.echo(format_output(f"Removed {email} from {file_id}.", output_json=output_json, account=account))
