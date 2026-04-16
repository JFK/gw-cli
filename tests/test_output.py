import json

from gw.output import format_output


def test_format_output_json() -> None:
    data = [{"id": "1", "summary": "Meeting"}]
    result = format_output(data, output_json=True, account="test@gmail.com")
    parsed = json.loads(result)
    assert parsed == data


def test_format_output_json_single_item() -> None:
    data = {"id": "1", "summary": "Meeting"}
    result = format_output(data, output_json=True, account="test@gmail.com")
    parsed = json.loads(result)
    assert parsed == data


def test_format_output_human_list() -> None:
    data = [{"id": "1", "summary": "Meeting"}]
    result = format_output(data, output_json=False, account="test@gmail.com")
    assert "[test@gmail.com]" in result
    assert "Meeting" in result


def test_format_output_human_dict() -> None:
    data = {"id": "1", "summary": "Meeting", "start": "10:00"}
    result = format_output(data, output_json=False, account="test@gmail.com")
    assert "[test@gmail.com]" in result
    assert "Meeting" in result


def test_format_output_human_empty_list() -> None:
    result = format_output([], output_json=False, account="test@gmail.com")
    assert "[test@gmail.com]" in result
    assert "No results" in result


def test_format_output_message() -> None:
    result = format_output("Event created successfully.", output_json=False, account="test@gmail.com")
    assert "[test@gmail.com]" in result
    assert "Event created successfully." in result
