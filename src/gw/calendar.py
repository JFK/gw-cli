from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import click

from gw.auth import build_service
from gw.config import DEFAULT_CONFIG_DIR, GwConfig
from gw.output import format_output


@click.group()
@click.pass_context
def cal(ctx: click.Context) -> None:
    """Google Calendar operations."""
    pass


@cal.command("list")
@click.option("--days", default=None, type=int, help="Number of days to show")
@click.pass_context
def list_events(ctx: click.Context, days: int | None) -> None:
    """List upcoming events."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    if days is None:
        default_days = cfg.get_default("calendar", "days")
        days = int(default_days) if default_days is not None else 7

    service = build_service(cfg, account, "calendar", "v3")
    tz = cfg.get_default("calendar", "timezone") or "Asia/Tokyo"

    now = datetime.now(timezone.utc).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
            timeZone=tz,
        )
        .execute()
    )

    events = []
    for item in result.get("items", []):
        start = item.get("start", {}).get("dateTime", item.get("start", {}).get("date", ""))
        end_time = item.get("end", {}).get("dateTime", item.get("end", {}).get("date", ""))
        events.append(
            {
                "id": item["id"],
                "summary": item.get("summary", "(No title)"),
                "start": start,
                "end": end_time,
                "meet": item.get("hangoutLink", ""),
            }
        )

    click.echo(format_output(events, output_json=output_json, account=account))


@cal.command()
@click.argument("event_id")
@click.pass_context
def get(ctx: click.Context, event_id: str) -> None:
    """Get event details."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "calendar", "v3")
    item = service.events().get(calendarId="primary", eventId=event_id).execute()

    data = {
        "id": item["id"],
        "summary": item.get("summary", "(No title)"),
        "start": item.get("start", {}).get("dateTime", ""),
        "end": item.get("end", {}).get("dateTime", ""),
        "location": item.get("location", ""),
        "description": item.get("description", ""),
        "meet": item.get("hangoutLink", ""),
        "attendees": [a.get("email", "") for a in item.get("attendees", [])],
    }
    click.echo(format_output(data, output_json=output_json, account=account))


@cal.command()
@click.option("--title", required=True)
@click.option("--start", required=True, help="Start time: YYYY-MM-DD HH:MM")
@click.option("--end", required=True, help="End time: YYYY-MM-DD HH:MM")
@click.option("--meet", is_flag=True, help="Add Google Meet link")
@click.option("--attendee", multiple=True, help="Attendee email (repeatable)")
@click.pass_context
def create(ctx: click.Context, title: str, start: str, end: str, meet: bool, attendee: tuple[str, ...]) -> None:
    """Create a new event."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)
    tz = cfg.get_default("calendar", "timezone") or "Asia/Tokyo"

    body: dict = {
        "summary": title,
        "start": {"dateTime": _parse_datetime(start, tz), "timeZone": tz},
        "end": {"dateTime": _parse_datetime(end, tz), "timeZone": tz},
    }

    if attendee:
        body["attendees"] = [{"email": e} for e in attendee]

    if meet:
        body["conferenceData"] = {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        }

    service = build_service(cfg, account, "calendar", "v3")
    conference_version = 1 if meet else 0
    result = (
        service.events()
        .insert(
            calendarId="primary",
            body=body,
            conferenceDataVersion=conference_version,
        )
        .execute()
    )

    data = {
        "id": result["id"],
        "summary": result.get("summary", ""),
        "link": result.get("htmlLink", ""),
        "meet": result.get("hangoutLink", ""),
    }
    click.echo(format_output(data, output_json=output_json, account=account))


@cal.command()
@click.argument("event_id")
@click.option("--title", default=None)
@click.option("--start", default=None, help="New start time: YYYY-MM-DD HH:MM")
@click.option("--end", default=None, help="New end time: YYYY-MM-DD HH:MM")
@click.pass_context
def update(ctx: click.Context, event_id: str, title: str | None, start: str | None, end: str | None) -> None:
    """Update an event."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)
    tz = cfg.get_default("calendar", "timezone") or "Asia/Tokyo"

    service = build_service(cfg, account, "calendar", "v3")
    event = service.events().get(calendarId="primary", eventId=event_id).execute()

    if title:
        event["summary"] = title
    if start:
        event["start"] = {"dateTime": _parse_datetime(start, tz), "timeZone": tz}
    if end:
        event["end"] = {"dateTime": _parse_datetime(end, tz), "timeZone": tz}

    result = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
    click.echo(format_output(f"Updated: {result.get('summary', '')}", output_json=output_json, account=account))


@cal.command()
@click.argument("event_id")
@click.pass_context
def delete(ctx: click.Context, event_id: str) -> None:
    """Delete an event."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    account = cfg.resolve_account(ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)

    service = build_service(cfg, account, "calendar", "v3")
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    click.echo(format_output("Deleted event.", output_json=output_json, account=account))


@cal.command()
@click.option("--date", required=True, help="Date to check: YYYY-MM-DD")
@click.option("--account", "account_override", default=None, help="Account email to check")
@click.pass_context
def free(ctx: click.Context, date: str, account_override: str | None) -> None:
    """Check free/busy status."""
    config_dir = ctx.obj.get("config_dir", DEFAULT_CONFIG_DIR)
    cfg = GwConfig(config_dir)
    # Use the --account option passed to this subcommand, or fall back to ctx.obj
    account = cfg.resolve_account(account_override or ctx.obj.get("account"))
    output_json = ctx.obj.get("json", False)
    tz = cfg.get_default("calendar", "timezone") or "Asia/Tokyo"

    try:
        next_day = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    except ValueError as exc:
        raise click.BadParameter(f"Invalid date {date!r}; expected format 'YYYY-MM-DD'.") from exc

    service = build_service(cfg, account, "calendar", "v3")
    body = {
        "timeMin": _parse_datetime(f"{date} 00:00", tz),
        "timeMax": _parse_datetime(f"{next_day} 00:00", tz),
        "timeZone": tz,
        "items": [{"id": account}],
    }
    result = service.freebusy().query(body=body).execute()

    busy_times = []
    for cal_id, cal_data in result.get("calendars", {}).items():
        for busy in cal_data.get("busy", []):
            busy_times.append({"account": cal_id, "start": busy["start"], "end": busy["end"]})

    if busy_times:
        click.echo(format_output(busy_times, output_json=output_json, account=account))
    else:
        click.echo(format_output(f"No busy times on {date}.", output_json=output_json, account=account))


def _parse_datetime(dt_str: str, tz_name: str) -> str:
    """Parse 'YYYY-MM-DD HH:MM' into RFC3339 with timezone offset."""
    from zoneinfo import ZoneInfo

    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise click.BadParameter(f"Invalid datetime {dt_str!r}; expected format 'YYYY-MM-DD HH:MM'.") from exc
    dt = dt.replace(tzinfo=ZoneInfo(tz_name))
    return dt.isoformat()
