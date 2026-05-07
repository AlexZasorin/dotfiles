"""
Synthetic record dicts for testing featurize.py.
All fixture variables use SCREAMING_SNAKE_CASE.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Individual record fixtures
# ---------------------------------------------------------------------------

HOOK_PROGRESS_SESSION_START: dict = {
    "type": "progress",
    "uuid": "hook-uuid-001",
    "parentUuid": None,
    "timestamp": "2026-01-01T10:00:00.000Z",
    "sessionId": "test-session-001",
    "cwd": "/Users/test/project",
    "data": {
        "type": "hook_progress",
        "hookEvent": "SessionStart",
        "message": "Starting session",
    },
}

FILE_HISTORY_SNAPSHOT: dict = {
    "type": "file-history-snapshot",
    "messageId": "u-user-1",
    "isSnapshotUpdate": False,
    "snapshot": {
        "messageId": "u-user-1",
        "trackedFileBackups": {},
        "timestamp": "2026-01-01T10:00:05.000Z",
    },
    # NOTE: no top-level uuid/timestamp/parentUuid on this record type
}

USER_TURN_STRING: dict = {
    "parentUuid": None,
    "isSidechain": False,
    "promptId": "prompt-001",
    "type": "user",
    "message": {
        "role": "user",
        "content": "fix the bug in parser.ts",
    },
    "uuid": "u-user-1",
    "timestamp": "2026-01-01T10:00:10.000Z",
    "permissionMode": "default",
    "userType": "external",
    "entrypoint": "cli",
    "cwd": "/Users/test/project",
    "sessionId": "test-session-001",
    "version": "2.1.0",
    "gitBranch": "main",
}

USER_TURN_TOOL_RESULT: dict = {
    "parentUuid": "a-assistant-1",
    "isSidechain": False,
    "sourceToolAssistantUUID": "a-assistant-1",
    # No promptId on tool result turns
    "type": "user",
    "message": {
        "role": "user",
        "content": [
            {
                "tool_use_id": "toolu_001",
                "type": "tool_result",
                "content": "Result content here",
                "is_error": False,
            }
        ],
    },
    "uuid": "u-tool-result-1",
    "timestamp": "2026-01-01T10:00:30.000Z",
    "permissionMode": "default",
    "userType": "external",
    "entrypoint": "cli",
    "cwd": "/Users/test/project",
    "sessionId": "test-session-001",
    "version": "2.1.0",
    "gitBranch": "main",
}

ASSISTANT_TURN_THINKING: dict = {
    "parentUuid": "u-user-1",
    "isSidechain": False,
    "type": "assistant",
    "message": {
        "model": "claude-opus-4-7",
        "id": "msg_thinking_001",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "thinking",
                "thinking": "Let me think about this bug...",
                "signature": "ErwEClkIDBgCKkDsomesignaturehere==",
            }
        ],
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 100, "output_tokens": 50},
    },
    "uuid": "a-assistant-thinking-1",
    "timestamp": "2026-01-01T10:00:20.000Z",
    "userType": "external",
    "entrypoint": "cli",
    "cwd": "/Users/test/project",
    "sessionId": "test-session-001",
    "version": "2.1.0",
}

ASSISTANT_TURN_TOOL_USE: dict = {
    "parentUuid": "a-assistant-thinking-1",
    "isSidechain": False,
    "type": "assistant",
    "message": {
        "model": "claude-opus-4-7",
        "id": "msg_tool_use_001",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_001",
                "name": "Grep",
                "input": {"pattern": "parseBug", "path": "src/"},
                "caller": {"type": "direct"},
            }
        ],
        "stop_reason": "tool_use",
        "usage": {"input_tokens": 150, "output_tokens": 30},
    },
    "uuid": "a-assistant-1",
    "timestamp": "2026-01-01T10:00:25.000Z",
    "userType": "external",
    "entrypoint": "cli",
    "cwd": "/Users/test/project",
    "sessionId": "test-session-001",
    "version": "2.1.0",
}

ASSISTANT_TURN_TEXT: dict = {
    "parentUuid": "u-tool-result-1",
    "isSidechain": False,
    "type": "assistant",
    "message": {
        "model": "claude-opus-4-7",
        "id": "msg_text_001",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "I found the bug. Here is the fix...",
            }
        ],
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 200, "output_tokens": 80},
    },
    "uuid": "a-assistant-text-1",
    "timestamp": "2026-01-01T10:00:45.000Z",
    "userType": "external",
    "entrypoint": "cli",
    "cwd": "/Users/test/project",
    "sessionId": "test-session-001",
    "version": "2.1.0",
}

ASSISTANT_TURN_AGENT_DELEGATION: dict = {
    "parentUuid": "u-user-1",
    "isSidechain": False,
    "type": "assistant",
    "message": {
        "model": "claude-opus-4-7",
        "id": "msg_agent_001",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_agent_001",
                "name": "Agent",
                "input": {
                    "description": "Explore the codebase for relevant files",
                    "subagent_type": "Explore",
                    "prompt": "Find all TypeScript files related to parsing",
                },
                "caller": {"type": "direct"},
            }
        ],
        "stop_reason": "tool_use",
        "usage": {"input_tokens": 300, "output_tokens": 100},
    },
    "uuid": "a-agent-delegation-1",
    "timestamp": "2026-01-01T10:01:00.000Z",
    "userType": "external",
    "entrypoint": "cli",
    "cwd": "/Users/test/project",
    "sessionId": "test-session-001",
    "version": "2.1.0",
}

SUBAGENT_USER_TURN: dict = {
    "parentUuid": None,
    "isSidechain": True,
    "agentId": "agent-xyz",
    # No promptId on subagent turns
    "type": "user",
    "message": {
        "role": "user",
        "content": "Search this codebase for any TypeScript parsers",
    },
    "uuid": "subagent-u-1",
    "timestamp": "2026-01-01T10:01:05.000Z",
    "userType": "external",
    "cwd": "/Users/test/project",
    "sessionId": "test-session-001",
    "version": "2.1.0",
}

# ---------------------------------------------------------------------------
# Composite session helpers
# ---------------------------------------------------------------------------


def minimal_session() -> list[dict]:
    """A minimal session: snapshot, user turn, assistant text reply."""
    return [
        FILE_HISTORY_SNAPSHOT,
        USER_TURN_STRING,
        ASSISTANT_TURN_TEXT,
    ]


def session_with_delegation() -> list[dict]:
    """A session containing an Agent delegation and a Grep tool use."""
    return [
        FILE_HISTORY_SNAPSHOT,
        USER_TURN_STRING,
        ASSISTANT_TURN_AGENT_DELEGATION,
        USER_TURN_TOOL_RESULT,
        ASSISTANT_TURN_THINKING,
        ASSISTANT_TURN_TOOL_USE,
        USER_TURN_TOOL_RESULT,
        ASSISTANT_TURN_TEXT,
    ]


def subagent_session() -> list[dict]:
    """A subagent session (all records have isSidechain=True, no promptId)."""
    return [
        SUBAGENT_USER_TURN,
        ASSISTANT_TURN_THINKING,
        ASSISTANT_TURN_TOOL_USE,
        USER_TURN_TOOL_RESULT,
        ASSISTANT_TURN_TEXT,
    ]
