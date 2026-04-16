---
name: gw-calendar
description: Google Calendar operations — list events, create/update/delete events, set up Google Meet, check free/busy. Use when the user asks about calendar, meetings, schedules, or availability.
---

# Google Calendar Operations

Use the `gw cal` CLI for calendar operations. Always use `--json` for parsing results.

## Commands

- `gw cal list [--account EMAIL] [--days N] --json` — List upcoming events
- `gw cal get EVENT_ID [--account EMAIL] --json` — Get event details
- `gw cal create --title "..." --start "YYYY-MM-DD HH:MM" --end "YYYY-MM-DD HH:MM" [--meet] [--attendee EMAIL] [--account EMAIL] --json` — Create event
- `gw cal update EVENT_ID [--title "..."] [--start "..."] [--end "..."] [--account EMAIL] --json` — Update event
- `gw cal delete EVENT_ID [--account EMAIL]` — Delete event
- `gw cal free --date YYYY-MM-DD [--account EMAIL] --json` — Check free/busy

## Guidelines

- Always confirm with the user before creating, updating, or deleting events
- When creating events with Meet, use the `--meet` flag
- Date/time format: "YYYY-MM-DD HH:MM" (24-hour, JST assumed)
- For free/busy across accounts, run the command for each account separately
- Present results in a readable format: date, time, title, Meet link if present
