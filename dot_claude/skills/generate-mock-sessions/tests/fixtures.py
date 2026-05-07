"""Test fixtures for test_records.py."""

SAMPLE_BLOCKS_SPEC_TEXT = [{"type": "text", "slot": "asst_text"}]

SAMPLE_BLOCKS_SPEC_THINKING_TOOL = [
    {"type": "thinking", "slot": "th"},
    {"type": "tool_use", "tool": "Grep", "input_slot": "gi"},
]

SAMPLE_TOOL_USE_RESULT = {"stdout": "match found", "stderr": "", "interrupted": False}

# ---------------------------------------------------------------------------
# Scaffolder template fixtures
# ---------------------------------------------------------------------------

MINIMAL_TEMPLATE = {
    "archetype": "minimal-test",
    "authoring_note": "small Q+A",
    "length_distribution": {"min_records": 3, "typical": 5, "max": 10},
    "model_weights": {"claude-opus-4-7": 1.0},
    "subagent_probability": 0.0,
    "events": [
        {"kind": "hook", "event": "SessionStart"},
        {"kind": "user_turn", "content_slot": "user_q"},
        {"kind": "assistant_turn", "blocks": [{"type": "text", "slot": "asst_a"}]},
    ],
}

DELEGATION_TEMPLATE = {
    "archetype": "delegation-test",
    "authoring_note": "user asks, assistant delegates to one subagent",
    "length_distribution": {"min_records": 5, "typical": 10, "max": 20},
    "model_weights": {"claude-opus-4-7": 1.0},
    "subagent_probability": 1.0,
    "events": [
        {"kind": "user_turn", "content_slot": "user_q"},
        {"kind": "assistant_turn", "blocks": [
            {"type": "tool_use", "tool": "Agent", "input_slot": "agent_input"},
        ]},
        {"kind": "subagent", "template": "subagent-test"},
        {"kind": "tool_result", "content_slot": "agent_finding", "result_kind": "string"},
        {"kind": "assistant_turn", "blocks": [{"type": "text", "slot": "synthesis"}]},
    ],
}

SUBAGENT_TEMPLATE = {  # paired with DELEGATION_TEMPLATE
    "archetype": "subagent-test",
    "authoring_note": "Glob then text reply",
    "length_distribution": {"min_records": 3, "typical": 4, "max": 8},
    "model_weights": {"claude-haiku-4-5-20251001": 1.0},
    "subagent_probability": 0.0,
    "events": [
        {"kind": "user_turn", "content_slot": "sub_user"},
        {"kind": "assistant_turn", "blocks": [
            {"type": "tool_use", "tool": "Glob", "input_slot": "glob_in"},
        ]},
        {"kind": "tool_result", "content_slot": "glob_out", "result_kind": "string"},
        {"kind": "assistant_turn", "blocks": [{"type": "text", "slot": "sub_reply"}]},
    ],
}

MULTI_TOOL_TEMPLATE = {
    "archetype": "multi-tool",
    "authoring_note": "two tool_use in one turn",
    "length_distribution": {"min_records": 4, "typical": 4, "max": 4},
    "model_weights": {"claude-opus-4-7": 1.0},
    "subagent_probability": 0.0,
    "events": [
        {"kind": "user_turn", "content_slot": "u"},
        {"kind": "assistant_turn", "blocks": [
            {"type": "tool_use", "tool": "Grep", "input_slot": "grep_in"},
            {"type": "tool_use", "tool": "Read", "input_slot": "read_in"},
        ]},
        {"kind": "tool_result", "content_slot": "grep_out", "result_kind": "string"},
        {"kind": "tool_result", "content_slot": "read_out", "result_kind": "string"},
    ],
}

FILE_SNAPSHOT_TEMPLATE = {
    "archetype": "file-snap",
    "authoring_note": "file snapshot before user turn",
    "length_distribution": {"min_records": 3, "typical": 3, "max": 3},
    "model_weights": {"claude-opus-4-7": 1.0},
    "subagent_probability": 0.0,
    "events": [
        {"kind": "permission_mode", "mode": "default"},
        {"kind": "hook", "event": "SessionStart"},
        {"kind": "file_snapshot"},
        {"kind": "user_turn", "content_slot": "u"},
    ],
}
