#!/usr/bin/env python3
"""Append one Capable 55 training event safely and idempotently.

Usage:
  python training/tools/append_session.py event.json
  cat event.json | python training/tools/append_session.py -

The input should contain the event fields except `record_id` and `ingest.idempotency_key`,
which are generated here when absent. The tool validates the complete JSONL ledger after append.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "training" / "sessions.jsonl"
ALLOWED_INTERFACES = {"chat", "voice", "manual_import", "other"}
ALLOWED_RECORD_TYPES = {"session", "amendment"}


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def read_input(path: str) -> dict[str, Any]:
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        die(f"Invalid JSON input: {exc}")
    if not isinstance(obj, dict):
        die("Input must be one JSON object")
    return obj


def load_ledger() -> list[dict[str, Any]]:
    if not LEDGER.exists():
        return []
    records: list[dict[str, Any]] = []
    for n, line in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            die(f"Ledger contains blank line at {n}")
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            die(f"Ledger JSON error on line {n}: {exc}")
        if not isinstance(obj, dict):
            die(f"Ledger line {n} is not a JSON object")
        records.append(obj)
    ids = [r.get("record_id") for r in records]
    if len(ids) != len(set(ids)):
        die("Ledger contains duplicate record_id values")
    return records


def validate_minimal(event: dict[str, Any]) -> None:
    if event.get("schema_version") != "1.0":
        die("schema_version must be '1.0'")
    if event.get("record_type") not in ALLOWED_RECORD_TYPES:
        die("record_type must be session or amendment")
    source = event.get("source")
    if not isinstance(source, dict):
        die("source must be an object")
    for key in ("interface", "agent", "reporter", "raw_text"):
        if not source.get(key):
            die(f"source.{key} is required")
    if source.get("interface") not in ALLOWED_INTERFACES:
        die("source.interface is invalid")
    recorded_at = event.get("recorded_at")
    if not recorded_at:
        die("recorded_at with UTC offset is required")
    try:
        parsed = datetime.fromisoformat(recorded_at)
    except ValueError:
        die("recorded_at must be ISO 8601")
    if parsed.utcoffset() is None:
        die("recorded_at must include a UTC offset")
    if not event.get("timezone"):
        die("timezone is required")
    rpe = event.get("session_rpe")
    if rpe is not None and not (0 <= rpe <= 10):
        die("session_rpe must be between 0 and 10")


def stable_key(event: dict[str, Any]) -> str:
    source = event["source"]
    external = source.get("source_event_id")
    if external:
        material = f"source_event_id:{external}"
    else:
        material_obj = {
            "record_type": event.get("record_type"),
            "session_date": event.get("session_date"),
            "raw_text": source.get("raw_text"),
            "interface": source.get("interface"),
            "reporter": source.get("reporter"),
        }
        material = json.dumps(material_obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def next_record_id(event: dict[str, Any], records: list[dict[str, Any]]) -> str:
    record_type = event["record_type"]
    if record_type == "session":
        date = event.get("session_date")
        if date:
            prefix = f"session-{date}-"
        else:
            recorded_date = event["recorded_at"][:10].replace("-", "")
            prefix = f"session-unknown-{recorded_date}-"
    else:
        recorded_date = event["recorded_at"][:10]
        prefix = f"amendment-{recorded_date}-"
    nums = []
    for rec in records:
        rid = rec.get("record_id", "")
        if rid.startswith(prefix):
            try:
                nums.append(int(rid.rsplit("-", 1)[1]))
            except ValueError:
                pass
    return f"{prefix}{max(nums, default=0) + 1:02d}"


def atomic_append(event: dict[str, Any], records: list[dict[str, Any]]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    existing = LEDGER.read_text(encoding="utf-8") if LEDGER.exists() else ""
    line = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix="sessions.", suffix=".jsonl", dir=str(LEDGER.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as tmp:
            tmp.write(existing)
            tmp.write(line)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, LEDGER)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

    check = load_ledger()
    if len(check) != len(records) + 1:
        die("Post-write validation failed: unexpected ledger length")
    if check[-1].get("record_id") != event["record_id"]:
        die("Post-write validation failed: appended record not last")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="JSON file path, or - for stdin")
    args = parser.parse_args()

    event = read_input(args.input)
    validate_minimal(event)
    records = load_ledger()

    key = stable_key(event)
    for rec in records:
        if rec.get("ingest", {}).get("idempotency_key") == key:
            print(json.dumps({"status": "duplicate", "record_id": rec.get("record_id"), "idempotency_key": key}))
            return

    event.setdefault("ingest", {})
    event["ingest"]["idempotency_key"] = key
    event["ingest"].setdefault("ingested_by", "training/tools/append_session.py")
    event.setdefault("record_id", next_record_id(event, records))

    if any(r.get("record_id") == event["record_id"] for r in records):
        die(f"record_id already exists: {event['record_id']}")

    atomic_append(event, records)
    print(json.dumps({"status": "appended", "record_id": event["record_id"], "idempotency_key": key}))


if __name__ == "__main__":
    main()
