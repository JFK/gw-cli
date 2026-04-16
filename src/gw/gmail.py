from __future__ import annotations

import base64
from email.mime.text import MIMEText

import click

from gw.auth import build_service
from gw.config import DEFAULT_CONFIG_DIR, GwConfig
from gw.output import format_output


def _get_header(headers: list[dict], name: str) -> str:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _decode_body(payload: dict) -> str:
    """Extract plain text body from message payload."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        text = _decode_body(part)
        if text:
            return text
    return ""


@click.group()
@click.pass_context
def mail(ctx: click.Context) -> None:
    """Gmail operations."""
    pass


@mail.command("list")
@click.option("--query", default=None, help="Gmail search query")
@click.option("--limit", default=None, type=int, help="Max messages to show")
@click.option("--since", default=None, help="Only show messages after this datetime (ISO format)")
@click.pass_context
def list_messages(ctx: click.Context, query: str | None, limit: int | None, since: str | None) -> None:
    """List messages."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    if limit is None:
        limit = cfg.get_default("mail", "limit") or 20

    search_query = query or cfg.get_default("mail", "check_query") or ""
    if since:
        search_query += f" after:{since}"

    service = build_service(cfg, account, "gmail", "v1")
    result = service.users().messages().list(userId="me", q=search_query, maxResults=limit).execute()

    messages = []
    for msg_meta in result.get("messages", []):
        msg = service.users().messages().get(
            userId="me", id=msg_meta["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()
        headers = msg.get("payload", {}).get("headers", [])
        messages.append({
            "id": msg["id"],
            "subject": _get_header(headers, "Subject"),
            "from": _get_header(headers, "From"),
            "date": _get_header(headers, "Date"),
            "unread": "UNREAD" in msg.get("labelIds", []),
        })

    click.echo(format_output(messages, output_json=output_json, account=account))


@mail.command()
@click.argument("message_id")
@click.pass_context
def read(ctx: click.Context, message_id: str) -> None:
    """Read a message (does NOT mark as read)."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "gmail", "v1")
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = msg.get("payload", {}).get("headers", [])
    body = _decode_body(msg.get("payload", {}))

    data = {
        "id": msg["id"],
        "subject": _get_header(headers, "Subject"),
        "from": _get_header(headers, "From"),
        "date": _get_header(headers, "Date"),
        "body": body,
    }
    click.echo(format_output(data, output_json=output_json, account=account))


@mail.command()
@click.option("--to", required=True, help="Recipient email")
@click.option("--subject", required=True)
@click.option("--body", required=True)
@click.pass_context
def send(ctx: click.Context, to: str, subject: str, body: str) -> None:
    """Send a message."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service = build_service(cfg, account, "gmail", "v1")
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    click.echo(format_output(f"Sent message (id: {result['id']})", output_json=output_json, account=account))


@mail.command()
@click.argument("message_id")
@click.option("--body", required=True)
@click.pass_context
def reply(ctx: click.Context, message_id: str, body: str) -> None:
    """Reply to a message."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "gmail", "v1")
    original = service.users().messages().get(userId="me", id=message_id, format="metadata",
                                               metadataHeaders=["Subject", "From", "Message-ID"]).execute()
    headers = original.get("payload", {}).get("headers", [])
    subject = _get_header(headers, "Subject")
    sender = _get_header(headers, "From")
    msg_id_header = _get_header(headers, "Message-ID")

    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    message = MIMEText(body)
    message["to"] = sender
    message["subject"] = subject
    message["In-Reply-To"] = msg_id_header
    message["References"] = msg_id_header
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    result = service.users().messages().send(
        userId="me", body={"raw": raw, "threadId": original["threadId"]},
    ).execute()
    click.echo(format_output(f"Replied (id: {result['id']})", output_json=output_json, account=account))


@mail.command("labels")
@click.pass_context
def list_labels(ctx: click.Context) -> None:
    """List Gmail labels."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "gmail", "v1")
    result = service.users().labels().list(userId="me").execute()
    labels = [{"id": l["id"], "name": l["name"]} for l in result.get("labels", [])]
    click.echo(format_output(labels, output_json=output_json, account=account))


@mail.command("label")
@click.argument("message_id")
@click.option("--add", "add_labels", multiple=True, help="Labels to add")
@click.option("--remove", "remove_labels", multiple=True, help="Labels to remove")
@click.pass_context
def modify_labels(ctx: click.Context, message_id: str, add_labels: tuple, remove_labels: tuple) -> None:
    """Add or remove labels from a message."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "gmail", "v1")
    service.users().messages().modify(
        userId="me", id=message_id,
        body={"addLabelIds": list(add_labels), "removeLabelIds": list(remove_labels)},
    ).execute()
    click.echo(format_output("Labels updated.", output_json=output_json, account=account))


@mail.command()
@click.argument("message_id")
@click.option("--read", "mark_read", is_flag=True, help="Mark as read")
@click.option("--unread", "mark_unread", is_flag=True, help="Mark as unread")
@click.pass_context
def mark(ctx: click.Context, message_id: str, mark_read: bool, mark_unread: bool) -> None:
    """Mark a message as read or unread."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    body: dict = {"addLabelIds": [], "removeLabelIds": []}
    if mark_read:
        body["removeLabelIds"].append("UNREAD")
    if mark_unread:
        body["addLabelIds"].append("UNREAD")

    service = build_service(cfg, account, "gmail", "v1")
    service.users().messages().modify(userId="me", id=message_id, body=body).execute()

    status = "read" if mark_read else "unread"
    click.echo(format_output(f"Marked as {status}.", output_json=output_json, account=account))


@mail.command()
@click.argument("message_id")
@click.pass_context
def attachments(ctx: click.Context, message_id: str) -> None:
    """List attachments of a message."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "gmail", "v1")
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()

    atts = []
    for part in msg.get("payload", {}).get("parts", []):
        if part.get("filename"):
            atts.append({
                "attachment_id": part["body"].get("attachmentId", ""),
                "filename": part["filename"],
                "mime_type": part.get("mimeType", ""),
                "size": part["body"].get("size", 0),
            })

    click.echo(format_output(atts, output_json=output_json, account=account))


@mail.command()
@click.argument("message_id")
@click.option("--attachment-id", required=True)
@click.option("--out", required=True, type=click.Path(), help="Output file path")
@click.pass_context
def download(ctx: click.Context, message_id: str, attachment_id: str, out: str) -> None:
    """Download an attachment."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "gmail", "v1")
    att = service.users().messages().attachments().get(
        userId="me", messageId=message_id, id=attachment_id
    ).execute()

    data = base64.urlsafe_b64decode(att["data"])
    from pathlib import Path
    Path(out).write_bytes(data)
    click.echo(format_output(f"Downloaded to {out}", output_json=output_json, account=account))


@mail.command("to-drive")
@click.argument("message_id")
@click.option("--attachment-id", required=True)
@click.option("--folder", default=None, help="Drive folder ID")
@click.pass_context
def to_drive(ctx: click.Context, message_id: str, attachment_id: str, folder: str | None) -> None:
    """Save an attachment to Google Drive."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    gmail_service = build_service(cfg, account, "gmail", "v1")
    msg = gmail_service.users().messages().get(userId="me", id=message_id, format="full").execute()
    filename = ""
    mime_type = "application/octet-stream"
    for part in msg.get("payload", {}).get("parts", []):
        if part.get("body", {}).get("attachmentId") == attachment_id:
            filename = part.get("filename", "attachment")
            mime_type = part.get("mimeType", mime_type)
            break

    att = gmail_service.users().messages().attachments().get(
        userId="me", messageId=message_id, id=attachment_id
    ).execute()
    data = base64.urlsafe_b64decode(att["data"])

    from googleapiclient.http import MediaInMemoryUpload
    drive_service = build_service(cfg, account, "drive", "v3")
    file_metadata: dict = {"name": filename}
    if folder:
        file_metadata["parents"] = [folder]

    media = MediaInMemoryUpload(data, mimetype=mime_type)
    result = drive_service.files().create(
        body=file_metadata, media_body=media, fields="id,name,webViewLink"
    ).execute()

    click.echo(format_output({
        "id": result["id"],
        "name": result["name"],
        "link": result.get("webViewLink", ""),
    }, output_json=output_json, account=account))
