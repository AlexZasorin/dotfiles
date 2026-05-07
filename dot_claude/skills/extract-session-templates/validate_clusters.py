"""
validate_clusters.py — Validate a clusters.json file against the expected schema.

Usage: python3 validate_clusters.py <clusters.json>
Exit 0 if valid, 1 on schema errors, 2 on usage error.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _check_archetype(archetype: object, idx: int, list_name: str) -> list[str]:
    """Validate a single archetype entry. Returns list of error strings."""
    errors: list[str] = []
    prefix = f"{list_name}[{idx}]"

    if not isinstance(archetype, dict):
        errors.append(f"{prefix}: must be an object, got {type(archetype).__name__}")
        return errors  # can't check fields if not a dict

    required_fields = {"name", "description", "member_files", "representative_files"}
    for field in required_fields:
        if field not in archetype:
            errors.append(f"{prefix}: missing required field '{field}'")

    # Validate name
    name = archetype.get("name")
    if "name" in archetype:
        if not isinstance(name, str):
            errors.append(f"{prefix}: name must be a string, got {type(name).__name__}")
        elif not _KEBAB_RE.match(name):
            errors.append(f"{prefix}: name '{name}' is not kebab-case")

    # Validate member_files type
    member_files = archetype.get("member_files")
    if "member_files" in archetype:
        if not isinstance(member_files, list):
            errors.append(
                f"{prefix}: member_files must be a list, got {type(member_files).__name__}"
            )

    # Validate representative_files type and membership
    representative_files = archetype.get("representative_files")
    if "representative_files" in archetype:
        if not isinstance(representative_files, list):
            errors.append(
                f"{prefix}: representative_files must be a list,"
                f" got {type(representative_files).__name__}"
            )
        elif isinstance(member_files, list):
            # Check every representative_files entry is in member_files
            member_set = set(member_files)
            for rep in representative_files:
                if rep not in member_set:
                    errors.append(
                        f"{prefix}: representative_file '{rep}' is not in member_files"
                    )

    return errors


def validate(path: Path) -> list[str]:
    """
    Validate a clusters.json file. Returns list of error strings (empty if valid).
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

    # Check top-level keys
    for key in ("main_archetypes", "subagent_archetypes"):
        if key not in data:
            errors.append(f"Missing top-level key '{key}'")

    # Validate main_archetypes
    main = data.get("main_archetypes")
    if main is not None:
        if not isinstance(main, list):
            errors.append(
                f"main_archetypes must be a list, got {type(main).__name__}"
            )
        else:
            for idx, archetype in enumerate(main):
                errors.extend(_check_archetype(archetype, idx, "main_archetypes"))
    elif "main_archetypes" in data:
        errors.append("main_archetypes must be a list, got NoneType")

    # Validate subagent_archetypes
    subagent = data.get("subagent_archetypes")
    if subagent is not None:
        if not isinstance(subagent, list):
            errors.append(
                f"subagent_archetypes must be a list, got {type(subagent).__name__}"
            )
        else:
            for idx, archetype in enumerate(subagent):
                errors.extend(_check_archetype(archetype, idx, "subagent_archetypes"))
    elif "subagent_archetypes" in data:
        errors.append("subagent_archetypes must be a list, got NoneType")

    # Check for duplicate names across both lists
    if errors:
        # Proceed with name dedup check only if we have valid list structures
        pass

    names_seen: dict[str, str] = {}  # name -> where it was first seen
    for list_name, lst in [
        ("main_archetypes", main),
        ("subagent_archetypes", subagent),
    ]:
        if not isinstance(lst, list):
            continue
        for idx, archetype in enumerate(lst):
            if not isinstance(archetype, dict):
                continue
            name = archetype.get("name")
            if not isinstance(name, str):
                continue
            key = name
            if key in names_seen:
                errors.append(
                    f"Duplicate archetype name '{name}' (first in"
                    f" {names_seen[key]}, also in {list_name}[{idx}])"
                )
            else:
                names_seen[key] = f"{list_name}[{idx}]"

    return errors


def _main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <clusters.json>", file=sys.stderr)
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
