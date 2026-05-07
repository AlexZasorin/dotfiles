"""
validate_template.py — Validate a session template JSON file against the expected schema.

Usage: python3 validate_template.py <template.json>
Exit 0 if valid, 1 on schema errors, 2 on usage error.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

_ALLOWED_EVENT_KINDS: frozenset[str] = frozenset(
    {
        "hook",
        "file_snapshot",
        "user_turn",
        "assistant_turn",
        "tool_result",
        "subagent",
        "permission_mode",
        "system_turn_duration",
    }
)

_ALLOWED_BLOCK_TYPES: frozenset[str] = frozenset({"thinking", "text", "tool_use"})
_ALLOWED_RESULT_KINDS: frozenset[str] = frozenset({"string", "structured"})

_REQUIRED_TOP_LEVEL = {
    "archetype",
    "authoring_note",
    "length_distribution",
    "model_weights",
    "subagent_probability",
    "events",
}


def _check_event(event: object, idx: int) -> list[str]:
    """Validate a single event entry. Returns list of error strings."""
    errors: list[str] = []
    prefix = f"events[{idx}]"

    if not isinstance(event, dict):
        errors.append(f"{prefix}: must be an object, got {type(event).__name__}")
        return errors

    kind = event.get("kind")
    if kind is None:
        errors.append(f"{prefix}: missing required field 'kind'")
        return errors

    if not isinstance(kind, str):
        errors.append(f"{prefix}: kind must be a string, got {type(kind).__name__}")
        return errors

    if kind not in _ALLOWED_EVENT_KINDS:
        errors.append(
            f"{prefix}: unknown event kind '{kind}'."
            f" Allowed: {sorted(_ALLOWED_EVENT_KINDS)}"
        )
        return errors  # no point checking kind-specific fields for unknown kinds

    if kind == "assistant_turn":
        blocks = event.get("blocks")
        if blocks is not None:
            if not isinstance(blocks, list):
                errors.append(
                    f"{prefix}: blocks must be a list,"
                    f" got {type(blocks).__name__}"
                )
            else:
                for bidx, block in enumerate(blocks):
                    if not isinstance(block, dict):
                        errors.append(
                            f"{prefix}.blocks[{bidx}]: must be an object,"
                            f" got {type(block).__name__}"
                        )
                        continue
                    btype = block.get("type")
                    if btype not in _ALLOWED_BLOCK_TYPES:
                        errors.append(
                            f"{prefix}.blocks[{bidx}]: unknown block type '{btype}'."
                            f" Allowed: {sorted(_ALLOWED_BLOCK_TYPES)}"
                        )

    elif kind == "tool_result":
        result_kind = event.get("result_kind")
        if result_kind is not None and result_kind not in _ALLOWED_RESULT_KINDS:
            errors.append(
                f"{prefix}: unknown result_kind '{result_kind}'."
                f" Allowed: {sorted(_ALLOWED_RESULT_KINDS)}"
            )

    elif kind == "subagent":
        template = event.get("template")
        if not isinstance(template, str) or not template.strip():
            errors.append(
                f"{prefix}: subagent event must have a non-empty 'template' string"
            )

    return errors


def _collect_slot_ids(template_data: dict) -> list[str]:
    """Collect all slot ID values from the template for uniqueness checking."""
    slot_ids: list[str] = []

    events = template_data.get("events", [])
    if not isinstance(events, list):
        return slot_ids

    for event in events:
        if not isinstance(event, dict):
            continue

        # Top-level content_slot and input_slot on events
        for field in ("content_slot", "input_slot"):
            val = event.get(field)
            if isinstance(val, str):
                slot_ids.append(val)

        # Block-level slot / input_slot
        blocks = event.get("blocks")
        if isinstance(blocks, list):
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                for field in ("slot", "input_slot"):
                    val = block.get(field)
                    if isinstance(val, str):
                        slot_ids.append(val)

    return slot_ids


def validate(path: Path) -> list[str]:
    """
    Validate a template JSON file. Returns list of error strings (empty if valid).
    Collects all errors — does not fail-fast.
    """
    errors: list[str] = []

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        return [f"JSON parse error: {exc}"]
    except OSError as exc:
        return [f"File read error: {exc}"]

    if not isinstance(data, dict):
        return [f"Root must be an object, got {type(data).__name__}"]

    # Check required top-level fields
    for field in sorted(_REQUIRED_TOP_LEVEL):
        if field not in data:
            errors.append(f"Missing required field '{field}'")

    # Validate archetype (kebab-case)
    archetype = data.get("archetype")
    if archetype is not None:
        if not isinstance(archetype, str):
            errors.append(
                f"archetype must be a string, got {type(archetype).__name__}"
            )
        elif not _KEBAB_RE.match(archetype):
            errors.append(f"archetype '{archetype}' is not kebab-case")

    # Validate length_distribution
    ld = data.get("length_distribution")
    if "length_distribution" in data:
        if ld is None:
            errors.append("length_distribution must be an object, got NoneType")
        elif not isinstance(ld, dict):
            errors.append(
                f"length_distribution must be an object, got {type(ld).__name__}"
            )
        else:
            min_r = ld.get("min_records")
            typical = ld.get("typical")
            max_r = ld.get("max")
            for fname, val in [
                ("min_records", min_r),
                ("typical", typical),
                ("max", max_r),
            ]:
                if val is None:
                    errors.append(
                        f"length_distribution.{fname} is required"
                    )
                elif not isinstance(val, (int, float)):
                    errors.append(
                        f"length_distribution.{fname} must be a number,"
                        f" got {type(val).__name__}"
                    )
            # Check ordering only if all three are present and numeric
            if (
                isinstance(min_r, (int, float))
                and isinstance(typical, (int, float))
                and isinstance(max_r, (int, float))
            ):
                if not (min_r <= typical <= max_r):
                    errors.append(
                        f"length_distribution ordering violated:"
                        f" min_records={min_r} <= typical={typical} <= max={max_r}"
                        f" must hold"
                    )

    # Validate model_weights
    mw = data.get("model_weights")
    if "model_weights" in data:
        if mw is None:
            errors.append("model_weights must be a non-empty dict, got NoneType")
        elif not isinstance(mw, dict):
            errors.append(
                f"model_weights must be a non-empty dict, got {type(mw).__name__}"
            )
        elif len(mw) == 0:
            errors.append("model_weights must not be empty")
        else:
            total = sum(mw.values())
            if abs(total - 1.0) > 1e-6:
                errors.append(
                    f"model_weights values must sum to 1.0, got {total}"
                )

    # Validate subagent_probability
    sp = data.get("subagent_probability")
    if "subagent_probability" in data:
        if not isinstance(sp, (int, float)):
            errors.append(
                f"subagent_probability must be a number, got {type(sp).__name__}"
            )
        elif not (0 <= sp <= 1):
            errors.append(
                f"subagent_probability must be in [0, 1], got {sp}"
            )

    # Validate events
    events = data.get("events")
    if "events" in data:
        if not isinstance(events, list):
            errors.append(
                f"events must be a list, got {type(events).__name__}"
            )
        elif len(events) == 0:
            errors.append("events must not be empty")
        else:
            for idx, event in enumerate(events):
                errors.extend(_check_event(event, idx))

    # Check slot ID uniqueness
    slot_ids = _collect_slot_ids(data)
    seen: dict[str, int] = {}
    for sid in slot_ids:
        seen[sid] = seen.get(sid, 0) + 1
    for sid, count in seen.items():
        if count > 1:
            errors.append(f"Duplicate slot id '{sid}' appears {count} times")

    return errors


def _main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <template.json>", file=sys.stderr)
        return 2

    path = Path(argv[1]).expanduser().resolve()
    errors = validate(path)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"{path.name} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
