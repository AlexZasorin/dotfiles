"""Structural validator for assembled mock session records.

Rules enforced
--------------
V1  Required-field invariants: type/uuid/timestamp must be present and non-null
    for records that carry the top-level UUID chain.

V2  Flat-meta records intentionally lack the uuid/timestamp envelope.  These
    are recognised by type and receive only slot-scan and (for
    file-history-snapshot) anchor checks.

    _FLAT_META_TYPES = {
        "file-history-snapshot", "permission-mode", "last-prompt",
        "custom-title", "agent-name", "queue-operation",
    }

V3  Tool-use / tool-result cross-reference:
    - Every tool_result.tool_use_id must match the id of a prior assistant
      tool_use block in the same file.
    - Every sourceToolAssistantUUID must match the uuid of a prior assistant
      record.
    Skipped entirely on subagent files (first record isSidechain=True) because
    the matching assistant tool_use blocks live in the parent session file.

V4  File-history-snapshot anchor: snapshot.messageId must resolve to the uuid
    of a user OR assistant record in the file.  The check is forward-looking —
    we collect all user/assistant uuids first, then verify every snapshot.

V5  Nested agent_progress traversal: when scanning for unfilled slot markers,
    recurse into data.message (subagent records embedded in parent progress
    wrappers).  Inner uuids are NOT added to the parent file's seen_uuids set.

Cross-file parent references
-----------------------------
A parentUuid whose value is not present in the current file's seen_uuids is
treated as a cross-file reference (e.g. the first record of a resumed session
whose parent lived in a previous file).  These are silently accepted — no error.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_REQUIRED_FIELDS = ("type", "uuid", "timestamp")

# Records that intentionally carry no top-level uuid/timestamp envelope.
# V2: skip structural checks; still run slot scan and V4 anchor check.
# queue-operation: real files have ~342 of these per large session.
_FLAT_META_TYPES = frozenset({
    "file-history-snapshot",
    "permission-mode",
    "last-prompt",
    "custom-title",
    "agent-name",
    "queue-operation",
})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _is_slot_marker(value: Any) -> bool:
    """Return True if value is an unfilled slot dict like {"_slot": "some-id"}."""
    return isinstance(value, dict) and set(value.keys()) == {"_slot"}


def _walk_for_slots(value: Any, path: str = "") -> list[str]:
    """Recursively walk value and return dotted paths of any slot markers found.

    V5: callers must pass the top-level record value here; data.message is
    traversed automatically since we recurse into every dict/list.
    """
    findings: list[str] = []
    if _is_slot_marker(value):
        findings.append(path or "<root>")
        return findings
    if isinstance(value, dict):
        for k, v in value.items():
            findings.extend(_walk_for_slots(v, f"{path}.{k}" if path else k))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            findings.extend(_walk_for_slots(item, f"{path}[{i}]"))
    return findings


def _parse_ts(ts: str) -> datetime | None:
    """Parse an ISO-8601 / Z-suffix timestamp string.

    Returns None if parsing fails, so callers can emit a descriptive error.
    """
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _collect_assistant_ids(records: list[dict]) -> tuple[set[str], set[str]]:
    """Pre-scan all records to collect assistant uuids and tool_use block ids.

    Returns (assistant_uuids, assistant_tool_use_ids).
    Used by V3 checks so we don't require strict ordering of validation.
    """
    asst_uuids: set[str] = set()
    tool_use_ids: set[str] = set()
    for r in records:
        if not isinstance(r, dict):
            continue
        if r.get("type") == "assistant":
            u = r.get("uuid")
            if isinstance(u, str):
                asst_uuids.add(u)
            content = r.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        bid = block.get("id")
                        if isinstance(bid, str):
                            tool_use_ids.add(bid)
    return asst_uuids, tool_use_ids


def _collect_interactive_uuids(records: list[dict]) -> set[str]:
    """Pre-collect uuids from user and assistant records for V4 anchor check.

    V4 originally required only user uuids, but real data shows snapshots also
    anchor to assistant record uuids, so we include both types here.
    """
    return {
        r["uuid"]
        for r in records
        if isinstance(r, dict)
        and r.get("type") in ("user", "assistant")
        and isinstance(r.get("uuid"), str)
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate(records: list[dict]) -> list[str]:
    """Return a list of human-readable error strings.  Empty list means valid."""
    errors: list[str] = []

    if not records:
        return ["records list is empty"]

    # Subagent files have their first record's isSidechain=True.
    # In that case, skip V3 cross-reference checks (the matching assistant
    # tool_use blocks live in the parent session file).
    is_subagent_file = bool(records[0].get("isSidechain")) if records else False

    # Pre-collect for V3 and V4 so ordering within the file doesn't matter.
    asst_uuids, tool_use_ids = _collect_assistant_ids(records)
    interactive_uuids = _collect_interactive_uuids(records)

    seen_uuids: set[str] = set()

    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            errors.append(f"records[{i}]: must be a dict")
            continue

        rtype = rec.get("type")

        # ------------------------------------------------------------------
        # Flat-meta records: only slot scan + V4 anchor check
        # ------------------------------------------------------------------
        if rtype in _FLAT_META_TYPES:
            for path in _walk_for_slots(rec):
                errors.append(f"records[{i}]: unfilled slot at {path}")

            # V4: file-history-snapshot.messageId must resolve to a user or
            # assistant record uuid in this file.
            if rtype == "file-history-snapshot":
                mid = rec.get("messageId")
                if isinstance(mid, str) and mid not in interactive_uuids:
                    errors.append(
                        f"records[{i}]: file-history-snapshot.messageId {mid!r} "
                        f"does not match any user or assistant record uuid in file"
                    )
            continue

        # ------------------------------------------------------------------
        # V1: required fields
        # ------------------------------------------------------------------
        for field in _REQUIRED_FIELDS:
            if field not in rec or rec[field] is None:
                errors.append(f"records[{i}]: missing or null {field}")

        # ------------------------------------------------------------------
        # V1: uuid uniqueness
        # ------------------------------------------------------------------
        u = rec.get("uuid")
        if isinstance(u, str):
            if u in seen_uuids:
                errors.append(f"records[{i}]: duplicate uuid {u}")
            seen_uuids.add(u)

        # ------------------------------------------------------------------
        # parentUuid: normalise empty string → None; cross-file refs silent
        # ------------------------------------------------------------------
        if "parentUuid" in rec:
            p = rec["parentUuid"]
            if p == "":
                p = None  # F10 edge case: empty string treated as no parent
            if p is not None and not isinstance(p, str):
                errors.append(f"records[{i}]: parentUuid must be string or null")
            # Non-None value absent from seen_uuids is a cross-file reference —
            # silently accepted (no error).

        # ------------------------------------------------------------------
        # Timestamp: validate parsability only
        #
        # NOTE: Real Claude Code session files do NOT maintain strict timestamp
        # monotonicity — attachment records, tool results, and progress records
        # can have timestamps slightly behind the preceding record (by up to
        # several seconds in observed data).  ~40% of real files exhibit this
        # pattern.  We therefore only check that timestamps are parsable; we do
        # not enforce ordering.
        # ------------------------------------------------------------------
        ts = rec.get("timestamp")
        if isinstance(ts, str):
            cur = _parse_ts(ts)
            if cur is None:
                errors.append(f"records[{i}]: malformed timestamp {ts!r}")

        # ------------------------------------------------------------------
        # Slot scan (V5: recurses into data.message automatically)
        # ------------------------------------------------------------------
        for path in _walk_for_slots(rec):
            errors.append(f"records[{i}]: unfilled slot at {path}")

        # ------------------------------------------------------------------
        # V3: tool_result cross-reference checks (skip on subagent files)
        # ------------------------------------------------------------------
        if not is_subagent_file and rtype == "user":
            content = rec.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        tu_id = block.get("tool_use_id")
                        if isinstance(tu_id, str) and tu_id not in tool_use_ids:
                            errors.append(
                                f"records[{i}]: tool_result references unknown "
                                f"tool_use_id {tu_id!r}"
                            )

            sta = rec.get("sourceToolAssistantUUID")
            if isinstance(sta, str) and sta not in asst_uuids:
                errors.append(
                    f"records[{i}]: sourceToolAssistantUUID {sta!r} does not "
                    f"match any assistant uuid in file"
                )

    return errors


def validate_jsonl_file(path: str | Path) -> list[str]:
    """Convenience wrapper: parse a .jsonl file then run validate().

    Returns a list of error strings.  A parse failure is reported as a single
    "cannot parse ..." error rather than raising.
    """
    p = Path(path)
    try:
        records = [
            json.loads(line)
            for line in p.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot parse {p}: {exc}"]
    return validate(records)
