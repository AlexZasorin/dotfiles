"""Pure record-building primitives for generate-mock-sessions.

No I/O, no global state mutation. All functions are deterministic given
a seeded random state (callers can seed random/secrets as needed).
"""

from __future__ import annotations

import base64
import os
import random
import secrets
import string
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Character sets
# ---------------------------------------------------------------------------

_BASE62 = string.digits + string.ascii_letters  # 0-9 a-z A-Z (62 chars)


# ---------------------------------------------------------------------------
# ID generators
# ---------------------------------------------------------------------------


def _b62(n: int) -> str:
    """Return n random base62 characters."""
    return "".join(secrets.choice(_BASE62) for _ in range(n))


def new_uuid() -> str:
    """Generate a fresh UUID4 string.

    F1 fix: uses uuid.UUID(int=..., version=4) so the version and variant bits
    are correctly set, producing a proper v4 UUID.
    """
    import uuid as _uuid

    return str(_uuid.UUID(int=random.getrandbits(128), version=4))


def new_request_id() -> str:
    """Anthropic-style request ID: req_011<22 base62 chars> = 29 chars total."""
    return "req_011" + _b62(22)


def new_message_id() -> str:
    """Anthropic-style message ID: msg_011<22 base62 chars>."""
    return "msg_011" + _b62(22)


def new_tool_use_id() -> str:
    """Anthropic-style tool use ID: toolu_011<22 base62 chars>."""
    return "toolu_011" + _b62(22)


def new_agent_msg_id() -> str:
    """Used inside agent_progress.toolUseID: agent_msg_011<22 base62 chars>."""
    return "agent_msg_011" + _b62(22)


def new_agent_id() -> str:
    """Subagent agent IDs: a + lowercase hex.

    Real distribution: ~60% length 17 (a + 16 hex), ~40% length 7 (a + 6 hex).
    Agent IDs are lowercase hex in real data, not base62.
    """
    n = 16 if random.random() < 0.6 else 6
    # token_hex(k) returns 2k hex chars; use ceiling division then slice to n
    return "a" + secrets.token_hex((n + 1) // 2)[:n]


def new_prompt_id() -> str:
    """Prompt IDs are UUID4s in real data."""
    return new_uuid()


# ---------------------------------------------------------------------------
# Slug sampler (R1)
# ---------------------------------------------------------------------------

_SLUG_ADJ_A = (
    "brave", "calm", "eager", "happy", "jazzy", "kind", "lucky", "nervous",
    "odd", "plucky", "quick", "red", "silly", "tame", "upbeat", "valid",
    "wise", "xeno", "young", "zesty", "ancient", "bouncy", "cosmic",
    "drowsy", "echoing", "fancy", "glimmering", "heavy", "icy", "jolly",
    "keen", "lavish", "mighty", "noisy", "oblique",
)
_SLUG_ADJ_B = (
    "waddling", "whistling", "floating", "sparkling", "glowing", "racing",
    "running", "spinning", "tumbling", "vectorized", "quaking", "roaring",
    "sliding", "whirring", "yawning", "zooming", "frolicking", "skipping",
    "strolling", "wandering",
)
_SLUG_NOUN = (
    "snail", "badger", "cobra", "dolphin", "eagle", "ferret", "gecko",
    "heron", "ibex", "jaguar", "koala", "lemur", "mongoose", "newt",
    "otter", "panda", "quail", "raven", "seal", "tiger", "urchin", "vole",
    "walrus", "yak", "zebra", "fox", "wolf", "hawk", "crane", "mouse",
)


def sample_slug() -> str:
    """Real Claude slugs are <adj1>-<adj2>-<noun> like 'vectorized-whistling-snail'."""
    return f"{random.choice(_SLUG_ADJ_A)}-{random.choice(_SLUG_ADJ_B)}-{random.choice(_SLUG_NOUN)}"


# ---------------------------------------------------------------------------
# Version sampler (R5)
# ---------------------------------------------------------------------------

_REAL_VERSIONS = ("2.1.83", "2.1.91", "2.1.92", "2.1.110", "2.1.112")


def sample_version() -> str:
    return random.choice(_REAL_VERSIONS)


# ---------------------------------------------------------------------------
# TimestampSequence
# ---------------------------------------------------------------------------


class TimestampSequence:
    """Monotonically increasing timestamp generator."""

    def __init__(self, start: datetime):
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        self._cursor = start

    def next(self, min_gap_ms: int = 100, max_gap_ms: int = 5000) -> str:
        gap = random.randint(min_gap_ms, max_gap_ms)
        self._cursor = self._cursor + timedelta(milliseconds=gap)
        # millisecond precision with trailing Z
        return self._cursor.isoformat(timespec="milliseconds").replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Sampling helpers
# ---------------------------------------------------------------------------


def weighted_choice(weights: dict[str, float]) -> str:
    if not weights:
        raise ValueError("weighted_choice: weights dict is empty")
    keys = list(weights.keys())
    vals = [weights[k] for k in keys]
    return random.choices(keys, weights=vals, k=1)[0]


def sample_length(distribution: dict[str, int]) -> int:
    """Triangular distribution centered at typical."""
    return int(random.triangular(
        distribution["min_records"],
        distribution["max"],
        distribution["typical"],
    ))


# ---------------------------------------------------------------------------
# SessionContext
# ---------------------------------------------------------------------------


@dataclass
class SessionContext:
    """Per-session metadata held constant across all records in one file.

    `is_sidechain` controls whether parent-only fields (entrypoint, promptId on
    user turns, permissionMode) are emitted on this session's records — F8.
    """

    session_id: str
    project_cwd: str
    git_branch: str
    version: str
    slug: str
    user_type: str = "external"
    entrypoint: str = "cli"
    is_sidechain: bool = False  # parent session = False, subagent session = True


def _common_session_fields(context: SessionContext) -> dict:
    """Envelope fields included on every interactive record. Sidechain-aware."""
    fields: dict = {
        "userType": context.user_type,
        "cwd": context.project_cwd,
        "sessionId": context.session_id,
        "version": context.version,
        "gitBranch": context.git_branch,
        "slug": context.slug,  # R1
    }
    if not context.is_sidechain:
        fields["entrypoint"] = context.entrypoint  # F8: parent-only
    return fields


# ---------------------------------------------------------------------------
# Hook event mapping (F7)
# ---------------------------------------------------------------------------

_HOOK_SUFFIX: dict[str, tuple[str, str]] = {
    "SessionStart": ("startup", "session-start"),
    "PostToolUse": ("post-tool-use", "post-tool-use"),
    "PreToolUse": ("pre-tool-use", "pre-tool-use"),
    "UserPromptSubmit": ("user-prompt-submit", "user-prompt-submit"),
    "Stop": ("stop", "stop"),
}


def build_hook(
    event: str,
    timestamp_seq: TimestampSequence,
    context: SessionContext,
    parent_uuid: str | None = None,
) -> dict:
    """Progress/hook_progress record. Event-driven hookName + command (F7)."""
    suffix, cmd_suffix = _HOOK_SUFFIX.get(event, (event.lower(), event.lower()))
    tool_use_id = new_uuid()
    return {
        "parentUuid": parent_uuid,
        "isSidechain": context.is_sidechain,
        "type": "progress",
        "data": {
            "type": "hook_progress",
            "hookEvent": event,
            "hookName": f"{event}:{suffix}",
            "command": f'"${{CLAUDE_PLUGIN_ROOT}}/hooks/run-hook.cmd" {cmd_suffix}',
        },
        "parentToolUseID": tool_use_id,
        "toolUseID": tool_use_id,
        "timestamp": timestamp_seq.next(min_gap_ms=0, max_gap_ms=200),
        "uuid": new_uuid(),
        **_common_session_fields(context),
    }


# ---------------------------------------------------------------------------
# File snapshot
# ---------------------------------------------------------------------------


def build_file_snapshot(message_id: str, timestamp_seq: TimestampSequence) -> dict:
    ts = timestamp_seq.next(min_gap_ms=10, max_gap_ms=100)
    return {
        "type": "file-history-snapshot",
        "messageId": message_id,
        "snapshot": {
            "messageId": message_id,
            "trackedFileBackups": {},
            "timestamp": ts,
        },
        "isSnapshotUpdate": False,
    }


# ---------------------------------------------------------------------------
# User turn
# ---------------------------------------------------------------------------


def build_user_turn(
    parent_uuid: str | None,
    content,
    timestamp_seq: TimestampSequence,
    context: SessionContext,
    prompt_id: str | None = None,
    permission_mode: str = "default",
    agent_id: str | None = None,
    uuid_override: str | None = None,
) -> dict:
    """Build a user-role turn record.

    Sidechain-aware: omits promptId and permissionMode for sidechain records (F8).
    """
    record: dict = {
        "parentUuid": parent_uuid,
        "isSidechain": context.is_sidechain,
        "type": "user",
        "message": {"role": "user", "content": content},
        "uuid": uuid_override or new_uuid(),
        "timestamp": timestamp_seq.next(min_gap_ms=200, max_gap_ms=15000),
        **_common_session_fields(context),
    }
    if not context.is_sidechain:
        record["promptId"] = prompt_id or new_prompt_id()
        record["permissionMode"] = permission_mode
    if agent_id is not None:
        record["agentId"] = agent_id
    return record


# ---------------------------------------------------------------------------
# Tool result
# ---------------------------------------------------------------------------


def build_tool_result(
    parent_uuid: str,
    tool_use_id: str,
    content,
    result_kind: str,
    source_tool_assistant_uuid: str,
    timestamp_seq: TimestampSequence,
    context: SessionContext,
    is_error: bool = False,
    agent_id: str | None = None,
    tool_use_result: dict | None = None,
) -> dict:
    """Build a user record carrying a tool_result block.

    F9: no permissionMode/promptId on tool_results; is_error opt-in; toolUseResult present.
    """
    if result_kind not in ("string", "structured"):
        raise ValueError(f"unknown result_kind: {result_kind}")
    inner_block: dict = {
        "tool_use_id": tool_use_id,
        "type": "tool_result",
        "content": content,
    }
    if is_error:
        inner_block["is_error"] = True  # only emit when True (real-data realism)
    record: dict = {
        "parentUuid": parent_uuid,
        "isSidechain": context.is_sidechain,
        "type": "user",
        "message": {
            "role": "user",
            "content": [inner_block],
        },
        "uuid": new_uuid(),
        "timestamp": timestamp_seq.next(min_gap_ms=50, max_gap_ms=1500),
        "sourceToolAssistantUUID": source_tool_assistant_uuid,
        **_common_session_fields(context),
    }
    # toolUseResult is a separate top-level field carrying the rich result object
    record["toolUseResult"] = (
        tool_use_result
        if tool_use_result is not None
        else {"stdout": "", "stderr": "", "interrupted": False}
    )
    if agent_id is not None:
        record["agentId"] = agent_id
    return record


# ---------------------------------------------------------------------------
# Assistant turn
# ---------------------------------------------------------------------------


_ALLOWED_BLOCK_TYPES = {"thinking", "text", "tool_use"}


def _fake_signature() -> str:
    """R2: ~380 char base64-ish placeholder matching real thinking signature shape."""
    return base64.b64encode(os.urandom(285)).decode().rstrip("=")


def _build_block(block_spec: dict) -> tuple[dict, str | None]:
    btype = block_spec.get("type")
    if btype not in _ALLOWED_BLOCK_TYPES:
        raise ValueError(f"unknown assistant block type: {btype}")
    slot = block_spec.get("slot")
    if btype == "thinking":
        return (
            {
                "type": "thinking",
                "thinking": {"_slot": slot},
                "signature": _fake_signature(),
            },
            None,
        )
    if btype == "text":
        return ({"type": "text", "text": {"_slot": slot}}, None)
    # tool_use
    tool_name = block_spec.get("tool")
    if not isinstance(tool_name, str):
        raise ValueError("tool_use block missing 'tool' field")
    input_slot = block_spec.get("input_slot")
    tu_id = new_tool_use_id()
    return (
        {
            "type": "tool_use",
            "id": tu_id,
            "name": tool_name,
            "input": {"_slot": input_slot},
            "caller": {"type": "direct"},
        },
        tu_id,
    )


def _initial_usage(input_tokens: int) -> dict:
    """R3: full usage shape matching real assistant records."""
    return {
        "input_tokens": input_tokens,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "service_tier": "standard",
        "cache_creation": {
            "ephemeral_5m_input_tokens": 0,
            "ephemeral_1h_input_tokens": 0,
        },
        "inference_geo": "",
    }


def build_assistant_turn(
    parent_uuid: str | None,
    blocks_spec: list[dict],
    model: str,
    timestamp_seq: TimestampSequence,
    context: SessionContext,
    agent_id: str | None = None,
) -> tuple[dict, list[str]]:
    """Returns (record, list_of_tool_use_ids in template order)."""
    content_blocks: list[dict] = []
    tool_use_ids: list[str] = []
    for spec in blocks_spec:
        block, tu_id = _build_block(spec)
        content_blocks.append(block)
        if tu_id is not None:
            tool_use_ids.append(tu_id)
    has_tool_use = bool(tool_use_ids)
    input_tokens = random.randint(50, 8000)
    record: dict = {
        "parentUuid": parent_uuid,
        "isSidechain": context.is_sidechain,
        "message": {
            "model": model,
            "id": new_message_id(),
            "type": "message",
            "role": "assistant",
            "content": content_blocks,
            "stop_reason": "tool_use" if has_tool_use else "end_turn",
            "stop_sequence": None,
            "stop_details": None,  # R3: real records always include this key
            "usage": _initial_usage(input_tokens),
        },
        "requestId": new_request_id(),
        "type": "assistant",
        "uuid": new_uuid(),
        "timestamp": timestamp_seq.next(min_gap_ms=200, max_gap_ms=4000),
        **_common_session_fields(context),
    }
    if agent_id is not None:
        record["agentId"] = agent_id
    return record, tool_use_ids


# ---------------------------------------------------------------------------
# Agent progress wrapper (F5, F6)
# ---------------------------------------------------------------------------


def build_agent_progress(
    parent_uuid: str,
    agent_id: str,
    parent_tool_use_id: str,
    inner: dict,
    timestamp_seq: TimestampSequence,
    context: SessionContext,
    delegation_message_id: str | None = None,
) -> dict:
    """Wrap a subagent record as an agent_progress event in the parent file.

    F5: data.message payload is a STRIPPED projection — only {type, message,
        uuid, timestamp} for user/progress, plus requestId for assistant.
        No envelope fields inside data.message.

    F6: delegation_message_id is constant for all wrappers of one delegation.
    """
    inner_type = inner.get("type")
    stripped: dict = {
        "type": inner_type,
        "uuid": inner.get("uuid"),
        "timestamp": inner.get("timestamp"),
    }
    if inner_type in ("user", "assistant", "progress"):
        if "message" in inner:
            stripped["message"] = inner["message"]
        if "data" in inner:
            stripped["data"] = inner["data"]
        if inner_type == "assistant" and "requestId" in inner:
            stripped["requestId"] = inner["requestId"]

    return {
        "parentUuid": parent_uuid,
        "isSidechain": False,  # parent file's wrapper is never sidechain
        "type": "progress",
        "data": {
            "type": "agent_progress",
            "agentId": agent_id,
            "message": stripped,
            "prompt": "",  # caller may patch with subagent's first user prompt
        },
        "toolUseID": delegation_message_id or new_agent_msg_id(),
        "parentToolUseID": parent_tool_use_id,
        "uuid": new_uuid(),
        "timestamp": timestamp_seq.next(min_gap_ms=10, max_gap_ms=200),
        **_common_session_fields(context),
    }


# ---------------------------------------------------------------------------
# Flat meta records
# ---------------------------------------------------------------------------


def build_permission_mode(mode: str, session_id: str) -> dict:
    return {
        "type": "permission-mode",
        "permissionMode": mode,
        "sessionId": session_id,
    }


def build_system_turn_duration(
    parent_uuid: str | None,  # F10: None when no chain ancestor — NOT empty string
    duration_ms: int,
    message_count: int,
    timestamp_seq: TimestampSequence,
    context: SessionContext,
) -> dict:
    return {
        "parentUuid": parent_uuid,  # may be None
        "isSidechain": context.is_sidechain,
        "type": "system",
        "subtype": "turn_duration",
        "durationMs": duration_ms,
        "messageCount": message_count,
        "timestamp": timestamp_seq.next(min_gap_ms=10, max_gap_ms=100),
        "uuid": new_uuid(),
        "isMeta": False,
        **_common_session_fields(context),
    }


def build_attachment(
    parent_uuid: str | None,
    attachment_data: dict,
    timestamp_seq: TimestampSequence,
    context: SessionContext,
) -> dict:
    """Wrap caller-supplied attachment_data with the standard envelope."""
    return {
        "parentUuid": parent_uuid,
        "isSidechain": context.is_sidechain,
        "attachment": attachment_data,
        "type": "attachment",
        "uuid": new_uuid(),
        "timestamp": timestamp_seq.next(min_gap_ms=50, max_gap_ms=500),
        **_common_session_fields(context),
    }


def build_last_prompt(last_prompt: str, session_id: str) -> dict:
    """Flat meta record echoing the most recent user prompt."""
    return {
        "type": "last-prompt",
        "lastPrompt": last_prompt,
        "sessionId": session_id,
    }
