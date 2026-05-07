"""CLI + skeleton/assemble/checkpoint orchestration for generate-mock-sessions.

Public API
----------
build_skeleton(template_path, template_dir, seed=0) -> dict
assemble(skeleton, filled_slots, out_root) -> dict
load_checkpoint(run_id, checkpoint_dir=None) -> dict
mark_checkpoint(run_id, index, total, checkpoint_dir=None) -> None
_main(argv) -> int
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Sibling-module imports
# ---------------------------------------------------------------------------
# Allow running from the skill directory directly.
_SKILL_DIR = Path(__file__).parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

import records
from validate import _is_slot_marker, validate

# ---------------------------------------------------------------------------
# Constants / defaults
# ---------------------------------------------------------------------------

_DEFAULT_PROJECTS = [
    ("-Users-azasorin--local-share-chezmoi", "/Users/azasorin/.local/share/chezmoi", "main"),
    ("-Users-azasorin-Repos-assignment", "/Users/azasorin/Repos/assignment", "trunk"),
    ("-Users-azasorin-Repos-outcome", "/Users/azasorin/Repos/outcome", "main"),
    ("-Users-azasorin-Repos-forms", "/Users/azasorin/Repos/forms", "main"),
    ("-Users-azasorin-Repos-platform-agent", "/Users/azasorin/Repos/platform-agent", "main"),
]

_DEFAULT_CHECKPOINT_DIR = Path.home() / ".local" / "share" / "generate-mock-sessions" / "checkpoints"

# Validation regexes for path-traversal guards (F12)
_VALID_RUN_ID = re.compile(r"^[A-Za-z0-9_-]+$")
_VALID_TEMPLATE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")  # kebab-case


# ---------------------------------------------------------------------------
# Session context sampling
# ---------------------------------------------------------------------------


def _sample_session_context(
    template: dict, is_sidechain: bool = False
) -> tuple[records.SessionContext, str, str]:
    """Return (SessionContext, session_id, project_slug)."""
    import random

    slug_tuple = random.choice(_DEFAULT_PROJECTS)
    project_slug, project_cwd, git_branch = slug_tuple

    session_id = records.new_uuid()
    version = records.sample_version()
    slug = records.sample_slug()
    model_weights = template.get("model_weights", {"claude-opus-4-7": 1.0})
    _ = records.weighted_choice(model_weights)  # consume a random draw for determinism

    ctx = records.SessionContext(
        session_id=session_id,
        project_cwd=project_cwd,
        git_branch=git_branch,
        version=version,
        slug=slug,
        user_type="external",
        entrypoint="cli",
        is_sidechain=is_sidechain,
    )
    return ctx, session_id, project_slug


# ---------------------------------------------------------------------------
# Event dispatcher
# ---------------------------------------------------------------------------


def _emit_event(
    event: dict,
    parent_uuid: str | None,
    timestamp_seq: records.TimestampSequence,
    context: records.SessionContext,
    model: str,
    state: dict,
    template_dir: Path,
    agent_id: str | None = None,
) -> tuple[list[dict], str | None]:
    """Dispatch a single template event and return (new_records, new_chain_uuid).

    State keys:
      pending_tool_use_ids   : list[str]  — FIFO queue (F3)
      preallocated_user_uuids: list[str]  — pre-allocated UUIDs for upcoming user_turns (F2)
      last_user_uuid         : str | None
      last_assistant_uuid    : str | None
      current_prompt_id      : str | None
      slots                  : list[dict] — accumulated slot manifest entries
    """
    kind = event.get("kind")

    # ------------------------------------------------------------------
    # hook — F11: root record, does NOT advance the chain
    # ------------------------------------------------------------------
    if kind == "hook":
        rec = records.build_hook(
            event["event"], timestamp_seq, context, parent_uuid=None
        )
        return [rec], parent_uuid  # chain unchanged

    # ------------------------------------------------------------------
    # permission_mode — flat meta, no chain change
    # ------------------------------------------------------------------
    if kind == "permission_mode":
        rec = records.build_permission_mode(event["mode"], context.session_id)
        return [rec], parent_uuid

    # ------------------------------------------------------------------
    # system_turn_duration
    # ------------------------------------------------------------------
    if kind == "system_turn_duration":
        rec = records.build_system_turn_duration(
            parent_uuid,
            event["duration_ms"],
            event["message_count"],
            timestamp_seq,
            context,
        )
        return [rec], rec["uuid"]

    # ------------------------------------------------------------------
    # file_snapshot — F2: anchor to pre-allocated NEXT user uuid
    # ------------------------------------------------------------------
    if kind == "file_snapshot":
        if state["preallocated_user_uuids"]:
            anchor = state["preallocated_user_uuids"][0]
        else:
            anchor = records.new_uuid()
        rec = records.build_file_snapshot(anchor, timestamp_seq)
        return [rec], parent_uuid  # snapshot doesn't advance chain

    # ------------------------------------------------------------------
    # user_turn — F11: first user always has parentUuid=None
    # ------------------------------------------------------------------
    if kind == "user_turn":
        u_uuid = (
            state["preallocated_user_uuids"].pop(0)
            if state["preallocated_user_uuids"]
            else None
        )
        prompt_id = records.new_prompt_id()
        state["current_prompt_id"] = prompt_id
        slot_id = event.get("content_slot")
        content: Any = {"_slot": slot_id} if slot_id else ""
        rec = records.build_user_turn(
            parent_uuid=parent_uuid,
            content=content,
            timestamp_seq=timestamp_seq,
            context=context,
            prompt_id=prompt_id,
            agent_id=agent_id,
            uuid_override=u_uuid,
        )
        if slot_id:
            state["slots"].append({"id": slot_id, "kind": "user_prompt", "context": ""})
        state["last_user_uuid"] = rec["uuid"]
        return [rec], rec["uuid"]

    # ------------------------------------------------------------------
    # assistant_turn
    # ------------------------------------------------------------------
    if kind == "assistant_turn":
        rec, tu_ids = records.build_assistant_turn(
            parent_uuid=parent_uuid,
            blocks_spec=event.get("blocks", []),
            model=model,
            timestamp_seq=timestamp_seq,
            context=context,
            agent_id=agent_id,
        )
        # F3: append ALL tool_use ids to FIFO queue
        state["pending_tool_use_ids"].extend(tu_ids)
        state["last_assistant_uuid"] = rec["uuid"]
        for block in event.get("blocks", []):
            btype = block.get("type", "")
            if "slot" in block:
                state["slots"].append({"id": block["slot"], "kind": btype, "context": ""})
            if "input_slot" in block:
                state["slots"].append(
                    {"id": block["input_slot"], "kind": "tool_input", "context": block.get("tool", "")}
                )
        return [rec], rec["uuid"]

    # ------------------------------------------------------------------
    # tool_result — F3: pop FIFO front
    # ------------------------------------------------------------------
    if kind == "tool_result":
        if not state["pending_tool_use_ids"]:
            raise ValueError("tool_result event with no pending tool_use in queue")
        tu_id = state["pending_tool_use_ids"].pop(0)
        slot_id = event.get("content_slot")
        content = {"_slot": slot_id} if slot_id else ""
        rec = records.build_tool_result(
            parent_uuid=parent_uuid,
            tool_use_id=tu_id,
            content=content,
            result_kind=event.get("result_kind", "string"),
            source_tool_assistant_uuid=state.get("last_assistant_uuid") or (parent_uuid or ""),
            timestamp_seq=timestamp_seq,
            context=context,
            agent_id=agent_id,
            tool_use_result={"stdout": "", "stderr": "", "interrupted": False},
        )
        if slot_id:
            state["slots"].append({"id": slot_id, "kind": "tool_result", "context": ""})
        return [rec], rec["uuid"]

    raise ValueError(f"unknown event kind: {kind!r}")


# ---------------------------------------------------------------------------
# Subagent expansion (F6, F8, F12c)
# ---------------------------------------------------------------------------


def _expand_subagent_event(
    event: dict,
    parent_uuid: str | None,
    parent_state: dict,
    timestamp_seq: records.TimestampSequence,
    parent_context: records.SessionContext,
    template_dir: Path,
    project_slug: str,
) -> tuple[dict, list[dict]]:
    """Build a subagent skeleton, wrap each record as agent_progress in the parent.

    Returns (sub_skeleton, parent_progress_records).

    F6: ONE delegation_msg_id shared across ALL wrappers for this delegation.
    F12c: template name must be kebab-case and file must exist.
    """
    name = event.get("template", "")
    if not _VALID_TEMPLATE_NAME.match(name):
        raise ValueError(f"invalid subagent template name: {name!r}")
    sub_path = template_dir / f"{name}.json"
    if not sub_path.exists():
        raise ValueError(f"subagent template '{name}' not found in {template_dir}")

    sub_template = json.loads(sub_path.read_text())

    agent_id = records.new_agent_id()
    delegation_msg_id = records.new_agent_msg_id()  # F6: stable across all wrappers

    # F8: subagent context is_sidechain=True
    sub_context = records.SessionContext(
        session_id=parent_context.session_id,
        project_cwd=parent_context.project_cwd,
        git_branch=parent_context.git_branch,
        version=parent_context.version,
        slug=parent_context.slug,
        user_type=parent_context.user_type,
        entrypoint=parent_context.entrypoint,
        is_sidechain=True,
    )
    sub_model = records.weighted_choice(
        sub_template.get("model_weights", {"claude-haiku-4-5-20251001": 1.0})
    )

    # Pass 1: pre-allocate user UUIDs for F2 in sub-events
    sub_events = sub_template.get("events", [])
    sub_preallocated = [
        records.new_uuid()
        for evt in sub_events
        if evt.get("kind") == "user_turn"
    ]

    sub_state: dict = {
        "pending_tool_use_ids": [],
        "preallocated_user_uuids": list(sub_preallocated),
        "last_user_uuid": None,
        "last_assistant_uuid": None,
        "current_prompt_id": None,
        "slots": [],
    }

    sub_records: list[dict] = []
    sub_parent_uuid: str | None = None
    for evt in sub_events:
        recs, sub_parent_uuid = _emit_event(
            evt, sub_parent_uuid, timestamp_seq, sub_context, sub_model, sub_state, template_dir, agent_id=agent_id
        )
        sub_records.extend(recs)

    # Merge sub slot manifest into parent's
    parent_state["slots"].extend(sub_state["slots"])

    # Peek at the parent's pending tool_use id (DO NOT pop — the subsequent
    # tool_result event in the parent template will pop it via FIFO).
    # The agent_progress wrappers reference this id as parentToolUseID.
    parent_tool_use_id = (
        parent_state["pending_tool_use_ids"][0]
        if parent_state["pending_tool_use_ids"]
        else "toolu_unknown"
    )

    # Build agent_progress wrappers in parent — F6: use delegation_msg_id for ALL
    _FLAT_META = {"file-history-snapshot", "permission-mode", "last-prompt"}
    parent_progress_records: list[dict] = []
    for sub_rec in sub_records:
        if sub_rec.get("type") in _FLAT_META:
            continue  # don't mirror flat meta into parent
        prog = records.build_agent_progress(
            parent_uuid=parent_uuid,
            agent_id=agent_id,
            parent_tool_use_id=parent_tool_use_id,
            inner=sub_rec,
            timestamp_seq=timestamp_seq,
            context=parent_context,
            delegation_message_id=delegation_msg_id,  # F6
        )
        parent_progress_records.append(prog)

    sub_output_path = (
        f"{project_slug}/{parent_context.session_id}/subagents/agent-{agent_id}.jsonl"
    )
    sub_skeleton = {
        "records": sub_records,
        "agent_id": agent_id,
        "output_path": sub_output_path,
    }
    return sub_skeleton, parent_progress_records


# ---------------------------------------------------------------------------
# build_skeleton — two-pass for F2
# ---------------------------------------------------------------------------


def build_skeleton(template_path: str | Path, template_dir: str | Path, seed: int = 0) -> dict:
    """Build a session skeleton from a template file.

    Two-pass approach (F2):
      Pass 1: count user_turn events and pre-allocate their UUIDs.
      Pass 2: emit records; file_snapshot references the pre-allocated UUID.
    """
    import random

    random.seed(seed)

    template_dir = Path(template_dir)
    template = json.loads(Path(template_path).read_text())

    context, session_id, project_slug = _sample_session_context(template, is_sidechain=False)
    model = records.weighted_choice(template.get("model_weights", {"claude-opus-4-7": 1.0}))
    timestamp_seq = records.TimestampSequence(
        start=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    events = template.get("events", [])

    # Pass 1: pre-allocate UUIDs for every user_turn (F2)
    preallocated_user_uuids = [
        records.new_uuid()
        for evt in events
        if evt.get("kind") == "user_turn"
    ]

    state: dict = {
        "pending_tool_use_ids": [],
        "preallocated_user_uuids": list(preallocated_user_uuids),
        "last_user_uuid": None,
        "last_assistant_uuid": None,
        "current_prompt_id": None,
        "slots": [],
    }

    out_records: list[dict] = []
    subagent_skeletons: list[dict] = []
    parent_uuid: str | None = None

    for evt in events:
        if evt.get("kind") == "subagent":
            # Validate template name eagerly (F12c)
            name = evt.get("template", "")
            if not _VALID_TEMPLATE_NAME.match(name):
                raise ValueError(f"invalid subagent template name: {name!r}")
            sub_path = template_dir / f"{name}.json"
            if not sub_path.exists():
                raise ValueError(f"subagent template '{name}' not found in {template_dir}")

            sub_skel, progress_records = _expand_subagent_event(
                evt, parent_uuid, state, timestamp_seq, context, template_dir, project_slug
            )
            out_records.extend(progress_records)
            subagent_skeletons.append(sub_skel)
            # subagent expansion does NOT advance the chain
            continue

        recs, parent_uuid = _emit_event(
            evt, parent_uuid, timestamp_seq, context, model, state, template_dir
        )
        out_records.extend(recs)

    return {
        "records": out_records,
        "slot_manifest": state["slots"],
        "session_id": session_id,
        "project_slug": project_slug,
        "output_path": f"{project_slug}/{session_id}.jsonl",
        "subagent_skeletons": subagent_skeletons,
    }


# ---------------------------------------------------------------------------
# Slot substitution
# ---------------------------------------------------------------------------


def _substitute_slots(value: Any, filled: dict) -> Any:
    """Recursively substitute {_slot: id} markers with their filled values."""
    if _is_slot_marker(value):
        return filled.get(value["_slot"], value)  # leave marker if missing → validator catches it
    if isinstance(value, dict):
        return {k: _substitute_slots(v, filled) for k, v in value.items()}
    if isinstance(value, list):
        return [_substitute_slots(item, filled) for item in value]
    return value


# ---------------------------------------------------------------------------
# Usage recompute — F4
# ---------------------------------------------------------------------------


def _recompute_usage(record: dict) -> None:
    """F4: recompute output_tokens from filled content size.

    Recurses into agent_progress.data.message for nested assistant records.
    """
    if record.get("type") == "assistant":
        msg = record.get("message", {})
        usage = msg.setdefault("usage", {})
        size = len(json.dumps(msg.get("content", [])))
        usage["output_tokens"] = max(1, size // 4)
    elif (
        record.get("type") == "progress"
        and record.get("data", {}).get("type") == "agent_progress"
    ):
        # F4: recurse into the inner message record
        inner = record.get("data", {}).get("message")
        if isinstance(inner, dict):
            _recompute_usage(inner)


# ---------------------------------------------------------------------------
# Path traversal check helper
# ---------------------------------------------------------------------------


def _path_within(child: Path, parent: Path) -> bool:
    """Return True if child is inside parent (after resolution)."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# assemble — F4 recompute + F12b traversal check
# ---------------------------------------------------------------------------


def assemble(skeleton: dict, filled_slots: dict, out_root: str | Path) -> dict:
    """Substitute slots, validate, and write JSONL files.

    Returns {"output_file": Path|None, "subagent_files": [Path,...], "errors": [str,...]}.
    """
    out_root = Path(out_root).resolve()

    # Substitute slots
    parent_records = [_substitute_slots(r, filled_slots) for r in skeleton["records"]]
    sub_assemblies: list[tuple[dict, list[dict]]] = []
    for sub_skel in skeleton.get("subagent_skeletons", []):
        sub_records = [_substitute_slots(r, filled_slots) for r in sub_skel["records"]]
        sub_assemblies.append((sub_skel, sub_records))

    # F4: recompute usage
    for r in parent_records:
        _recompute_usage(r)
    for _sub_skel, sub_recs in sub_assemblies:
        for r in sub_recs:
            _recompute_usage(r)

    # Validate
    errors: list[str] = []
    errors.extend(validate(parent_records))
    for _sub_skel, sub_recs in sub_assemblies:
        errors.extend(validate(sub_recs))
    if errors:
        return {"output_file": None, "subagent_files": [], "errors": errors}

    # F12b: path traversal check on parent output
    out_file = out_root / skeleton["output_path"]
    if not _path_within(out_file, out_root):
        return {
            "output_file": None,
            "subagent_files": [],
            "errors": ["output_path escapes out_root"],
        }
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        "\n".join(json.dumps(r) for r in parent_records) + "\n"
    )

    sub_files: list[Path] = []
    for sub_skel, sub_recs in sub_assemblies:
        sf = out_root / sub_skel["output_path"]
        if not _path_within(sf, out_root):
            return {
                "output_file": None,
                "subagent_files": [],
                "errors": ["subagent output_path escapes out_root"],
            }
        sf.parent.mkdir(parents=True, exist_ok=True)
        sf.write_text("\n".join(json.dumps(r) for r in sub_recs) + "\n")
        sub_files.append(sf)

    return {"output_file": out_file, "subagent_files": sub_files, "errors": []}


# ---------------------------------------------------------------------------
# Checkpoint — F12a + F13
# ---------------------------------------------------------------------------


def _checkpoint_path(run_id: str, checkpoint_dir: str | Path | None) -> Path:
    if not _VALID_RUN_ID.match(run_id):
        raise ValueError(f"invalid run_id: {run_id!r}")
    base = Path(checkpoint_dir) if checkpoint_dir else _DEFAULT_CHECKPOINT_DIR
    return base / f"{run_id}.json"


def mark_checkpoint(
    run_id: str,
    index: int,
    total: int,
    checkpoint_dir: str | Path | None = None,
) -> None:
    """Record that index has been completed.  F12a + F13 atomic write."""
    path = _checkpoint_path(run_id, checkpoint_dir)  # raises ValueError if bad run_id
    path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing or start fresh (F13 corrupt-file recovery)
    try:
        state = json.loads(path.read_text()) if path.exists() else {"completed": [], "remaining": total}
    except (OSError, json.JSONDecodeError):
        state = {"completed": [], "remaining": total}

    state.setdefault("completed", [])
    state.setdefault("remaining", total)
    if index not in state["completed"]:
        state["completed"].append(index)

    # F13: atomic write via rename
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, path)  # atomic on POSIX


def load_checkpoint(
    run_id: str,
    checkpoint_dir: str | Path | None = None,
) -> dict:
    """Load checkpoint state. F12a validates run_id. F13 recovers corrupt files."""
    path = _checkpoint_path(run_id, checkpoint_dir)  # raises ValueError if bad run_id
    if not path.exists():
        return {"completed": [], "remaining": None}
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        # F13: corrupt or partial — start fresh
        return {"completed": [], "remaining": None}


# ---------------------------------------------------------------------------
# CLI — _main
# ---------------------------------------------------------------------------


def _main(argv: list[str]) -> int:
    """CLI dispatcher. Returns exit code 0/1/2."""
    parser = argparse.ArgumentParser(
        prog="scaffolder.py",
        description="Generate mock Claude session JSONL files.",
    )
    sub = parser.add_subparsers(dest="command")

    # skeleton subcommand
    p_skel = sub.add_parser("skeleton", help="Build a session skeleton from a template.")
    p_skel.add_argument("template_path", help="Path to the template JSON file.")
    p_skel.add_argument("--template-dir", default=None, help="Directory for subagent templates.")
    p_skel.add_argument("--seed", type=int, default=0, help="Random seed (default: 0).")

    # assemble subcommand
    p_asm = sub.add_parser("assemble", help="Fill slots and write JSONL files.")
    p_asm.add_argument("skeleton_path", help="Path to a skeleton JSON file.")
    p_asm.add_argument("slots_path", help="Path to a filled-slots JSON file.")
    p_asm.add_argument("out_root", help="Output root directory.")

    # checkpoint-mark subcommand
    p_mark = sub.add_parser("checkpoint-mark", help="Mark an index as completed.")
    p_mark.add_argument("run_id", help="Run identifier (alphanumeric, hyphens, underscores).")
    p_mark.add_argument("index", type=int, help="Index to mark completed.")
    p_mark.add_argument("total", type=int, help="Total number of items.")
    p_mark.add_argument("--checkpoint-dir", default=None, help="Checkpoint directory.")

    # checkpoint-load subcommand
    p_load = sub.add_parser("checkpoint-load", help="Load checkpoint state.")
    p_load.add_argument("run_id", help="Run identifier.")
    p_load.add_argument("--checkpoint-dir", default=None, help="Checkpoint directory.")

    args = parser.parse_args(argv[1:])

    if args.command == "skeleton":
        tpl_path = Path(args.template_path)
        tpl_dir = Path(args.template_dir) if args.template_dir else tpl_path.parent
        try:
            skel = build_skeleton(tpl_path, tpl_dir, seed=args.seed)
        except Exception as exc:
            print(json.dumps({"error": str(exc)}))
            return 1
        print(json.dumps(skel, default=str))
        return 0

    if args.command == "assemble":
        skeleton = json.loads(Path(args.skeleton_path).read_text())
        filled_slots = json.loads(Path(args.slots_path).read_text())
        result = assemble(skeleton, filled_slots, args.out_root)
        out = {
            "output_file": str(result["output_file"]) if result["output_file"] else None,
            "subagent_files": [str(p) for p in result["subagent_files"]],
            "errors": result["errors"],
        }
        print(json.dumps(out))
        return 0 if not result["errors"] else 1

    if args.command == "checkpoint-mark":
        try:
            mark_checkpoint(
                args.run_id,
                args.index,
                args.total,
                checkpoint_dir=args.checkpoint_dir,
            )
        except ValueError as exc:
            print(json.dumps({"error": str(exc)}))
            return 1
        print(json.dumps({"ok": True}))
        return 0

    if args.command == "checkpoint-load":
        try:
            state = load_checkpoint(args.run_id, checkpoint_dir=args.checkpoint_dir)
        except ValueError as exc:
            print(json.dumps({"error": str(exc)}))
            return 1
        print(json.dumps(state))
        return 0

    # Unknown subcommand
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
