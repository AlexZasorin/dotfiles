"""
featurize.py — Walk a directory of Claude Code session .jsonl files and produce
a CSV of structural features per file.

Usage: python3 featurize.py <input-dir> <output-csv>
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from typing import Iterator

_STOPWORDS: frozenset[str] = frozenset(
    {
        # Standard English
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "to", "of", "in", "on", "at", "for", "and", "or", "but",
        "with", "as", "by", "from", "it", "its", "this", "that",
        "these", "those", "i", "you", "he", "she", "we", "they",
        "my", "your", "our", "can", "could", "should", "would",
        "do", "does", "did", "has", "have", "had", "will", "just",
        # Noisy / common in session data
        "not", "any", "all", "them", "use", "please", "only", "also",
        "even", "still", "now", "then", "than", "like", "want", "need",
        "make", "made", "get", "got", "see", "look", "find", "found",
        "let", "way", "following", "running", "message", "messages",
        "command", "commands", "read", "reads", "while", "name",
        "response", "responses", "generated", "context",
        "what", "when", "where", "why", "how", "who", "which",
        "there", "here", "into", "over", "under", "out", "up", "down",
        "about", "after", "before", "between", "some", "more", "most",
        "much", "many", "few", "other", "another", "same", "next",
        "last", "first", "if", "so", "no", "yes",
    }
)

_CSV_COLUMNS = [
    "path",
    "project_slug",
    "is_subagent",
    "session_id",
    "length",
    "duration_seconds",
    "tool_sequence",
    "subagent_delegation_count",
    "uses_plan_mode",
    "model_mix",
    "topic_fingerprint",
]


def load_session(path: Path) -> list[dict]:
    """Parse a .jsonl file; skip blank lines. Returns list of record dicts."""
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def extract_tool_sequence(records: list[dict]) -> list[str]:
    """Return assistant tool_use names in order. Non-dict blocks are skipped."""
    names: list[str] = []
    for record in records:
        if record.get("type") != "assistant":
            continue
        content = record.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                tool_name = block.get("name")
                if tool_name:
                    names.append(tool_name)
    return names


def session_length(records: list[dict]) -> int:
    """Return total number of records."""
    return len(records)


def session_duration_seconds(records: list[dict]) -> float:
    """
    Return duration from first to last record that has a timestamp.
    Checks top-level `timestamp` field first, then `snapshot.timestamp`
    for file-history-snapshot records. Returns 0.0 if fewer than 2 timestamps found.
    """
    from datetime import datetime

    timestamps: list[datetime] = []

    for record in records:
        ts_str: str | None = None
        # Top-level timestamp
        if "timestamp" in record and record["timestamp"]:
            ts_str = record["timestamp"]
        # Fallback: file-history-snapshot records embed timestamp inside snapshot
        elif record.get("type") == "file-history-snapshot":
            snapshot = record.get("snapshot", {})
            if isinstance(snapshot, dict) and snapshot.get("timestamp"):
                ts_str = snapshot["timestamp"]

        if ts_str:
            try:
                # Handle both Z suffix and +00:00 suffix
                ts_str_clean = ts_str.replace("Z", "+00:00")
                dt = datetime.fromisoformat(ts_str_clean)
                timestamps.append(dt)
            except (ValueError, TypeError):
                pass

    if len(timestamps) < 2:
        return 0.0

    return (max(timestamps) - min(timestamps)).total_seconds()


def subagent_delegation_count(records: list[dict]) -> int:
    """Count assistant tool_use blocks whose name is 'Agent'."""
    count = 0
    for record in records:
        if record.get("type") != "assistant":
            continue
        content = record.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                if block.get("name") == "Agent":
                    count += 1
    return count


def model_mix(records: list[dict]) -> dict[str, int]:
    """Return mapping of model name -> count of assistant records using that model."""
    mix: dict[str, int] = {}
    for record in records:
        if record.get("type") != "assistant":
            continue
        model = record.get("message", {}).get("model")
        if model:
            mix[model] = mix.get(model, 0) + 1
    return mix


def uses_plan_mode(records: list[dict]) -> bool:
    """Return True if any user record has permissionMode == 'plan'."""
    for record in records:
        if record.get("type") == "user":
            if record.get("permissionMode") == "plan":
                return True
    return False


def topic_fingerprint(records: list[dict]) -> set[str]:
    """
    Return token set from the FIRST non-sidechain user turn with string content.
    Tokens are alpha-numeric sequences > 2 chars, lowercased, not in _STOPWORDS.
    Sidechain records (isSidechain == True) are skipped.
    """
    for record in records:
        if record.get("type") != "user":
            continue
        if record.get("isSidechain"):
            continue
        content = record.get("message", {}).get("content")
        if not isinstance(content, str):
            continue
        if not content.strip():
            continue
        tokens = re.findall(r"[a-zA-Z0-9]+", content.lower())
        return {t for t in tokens if len(t) > 2 and t not in _STOPWORDS}
    return set()


def _derive_project_slug(root: Path, file_path: Path) -> str:
    """Return the first path component of file_path relative to root."""
    try:
        rel = file_path.relative_to(root)
        return rel.parts[0] if rel.parts else ""
    except ValueError:
        return ""


def _derive_is_subagent(file_path: Path) -> bool:
    """Return True if 'subagents' appears in the file path parts."""
    return "subagents" in file_path.parts


def _derive_session_id(file_path: Path) -> str:
    """Extract session ID from filename stem."""
    return file_path.stem


def featurize_file(root: Path, path: Path) -> dict:
    """Load a session file and return a feature dict (one CSV row)."""
    records = load_session(path)

    tool_seq = extract_tool_sequence(records)
    mix = model_mix(records)
    fingerprint = topic_fingerprint(records)

    return {
        "path": str(path),
        "project_slug": _derive_project_slug(root, path),
        "is_subagent": _derive_is_subagent(path),
        "session_id": _derive_session_id(path),
        "length": session_length(records),
        "duration_seconds": round(session_duration_seconds(records), 3),
        "tool_sequence": json.dumps(tool_seq),
        "subagent_delegation_count": subagent_delegation_count(records),
        "uses_plan_mode": uses_plan_mode(records),
        "model_mix": json.dumps(mix),
        "topic_fingerprint": json.dumps(sorted(fingerprint)),
    }


def featurize_directory(root: Path) -> Iterator[dict]:
    """
    Walk root recursively for *.jsonl files and yield one feature dict per file.
    Files that fail to parse emit a stderr warning and are skipped.
    """
    for path in sorted(root.rglob("*.jsonl")):
        try:
            yield featurize_file(root, path)
        except Exception as exc:
            print(f"WARNING: skipping {path}: {exc}", file=sys.stderr)


def write_csv(root: Path, out_path: Path) -> int:
    """Write features CSV to out_path. Returns number of rows written."""
    rows = list(featurize_directory(root))
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"Usage: {argv[0]} <input-dir> <output-csv>", file=sys.stderr)
        return 2

    root = Path(argv[1]).expanduser().resolve()
    out_path = Path(argv[2]).expanduser().resolve()

    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        return 1

    count = write_csv(root, out_path)
    print(f"Wrote {count} rows to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
