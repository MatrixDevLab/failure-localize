#!/usr/bin/env python3
"""Deterministic first-failure localization for normalized tool traces."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class InputError(ValueError):
    """Raised when a trace cannot be safely classified."""


FAILURE_STATUSES = {"error", "failed", "failure"}
TRUNCATION_REASONS = {"length", "max_tokens", "MALFORMED_FUNCTION_CALL"}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{label} must be an object")
    return value


def load_trace(path: Path) -> list[dict[str, Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read JSON trace: {exc}") from exc

    root = _mapping(raw, "trace")
    events = root.get("events")
    if not isinstance(events, list):
        raise InputError("trace.events must be an array")

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_seq: set[int] = set()
    for index, raw_event in enumerate(events):
        event = _mapping(raw_event, f"trace.events[{index}]")
        event_id = event.get("id")
        seq = event.get("seq")
        kind = event.get("kind")
        if not isinstance(event_id, str) or not event_id:
            raise InputError(f"trace.events[{index}].id must be a non-empty string")
        if event_id in seen_ids:
            raise InputError(f"duplicate event id: {event_id}")
        if isinstance(seq, bool) or not isinstance(seq, int) or seq < 0:
            raise InputError(f"trace.events[{index}].seq must be a non-negative integer")
        if seq in seen_seq:
            raise InputError(f"duplicate event seq: {seq}")
        if not isinstance(kind, str) or not kind:
            raise InputError(f"trace.events[{index}].kind must be a non-empty string")
        seen_ids.add(event_id)
        seen_seq.add(seq)
        normalized.append(event)

    return sorted(normalized, key=lambda event: event["seq"])


def classify(event: dict[str, Any]) -> tuple[str, str] | None:
    if event.get("finish_reason") in TRUNCATION_REASONS:
        return "truncated_tool_call", "explicit finish reason"
    if event.get("tool_found") is False:
        return "unknown_tool", "explicit tool lookup miss"
    if event.get("arguments_valid") is False or event.get("validation_error") is True:
        return "invalid_arguments", "explicit argument validation failure"
    if event.get("status") in FAILURE_STATUSES or bool(event.get("error")):
        kind = event.get("kind")
        category = "execution_failure" if kind == "tool_result" else "workflow_failure"
        return category, "explicit failure status or error"
    return None


def linked_to(event: dict[str, Any], first: dict[str, Any]) -> bool:
    first_id = first["id"]
    if event.get("cause_id") == first_id:
        return True
    depends_on = event.get("depends_on", [])
    if isinstance(depends_on, list) and first_id in depends_on:
        return True
    first_call = first.get("call_id")
    return bool(first_call and event.get("call_id") == first_call and event["seq"] > first["seq"])


def localize(events: list[dict[str, Any]]) -> dict[str, Any]:
    ordered_events = sorted(events, key=lambda event: event["seq"])
    candidates: list[tuple[dict[str, Any], str, str]] = []
    for event in ordered_events:
        result = classify(event)
        if result:
            category, reason = result
            candidates.append((event, category, reason))

    if not candidates:
        return {
            "schema": 1,
            "state": "insufficient",
            "first_failure": None,
            "cascades": [],
            "note": "no explicit failure signal was present",
        }

    first, category, reason = candidates[0]
    cascades = [
        {
            "id": event["id"],
            "seq": event["seq"],
            "kind": event["kind"],
            "category": next_category,
        }
        for event, next_category, _ in candidates[1:]
        if linked_to(event, first)
    ]
    return {
        "schema": 1,
        "state": "localized",
        "first_failure": {
            "id": first["id"],
            "seq": first["seq"],
            "kind": first["kind"],
            "category": category,
            "basis": reason,
        },
        "cascades": cascades,
        "note": "classification is limited to explicit fields and links",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    args = parser.parse_args(argv)
    try:
        result = localize(load_trace(args.trace))
    except InputError as exc:
        print(json.dumps({"schema": 1, "state": "invalid", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
