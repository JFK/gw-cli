from __future__ import annotations

import json


def format_output(
    data: list | dict | str,
    *,
    output_json: bool,
    account: str,
) -> str:
    if output_json:
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)

    prefix = f"[{account}]"

    if isinstance(data, str):
        return f"{prefix} {data}"

    if isinstance(data, list):
        if not data:
            return f"{prefix} No results."
        lines = [prefix]
        for item in data:
            parts = [str(v) for v in item.values()]
            lines.append("  " + " | ".join(parts))
        return "\n".join(lines)

    if isinstance(data, dict):
        lines = [prefix]
        for key, value in data.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)

    return f"{prefix} {data}"
