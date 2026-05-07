"""Test fixtures for test_records.py."""

SAMPLE_BLOCKS_SPEC_TEXT = [{"type": "text", "slot": "asst_text"}]

SAMPLE_BLOCKS_SPEC_THINKING_TOOL = [
    {"type": "thinking", "slot": "th"},
    {"type": "tool_use", "tool": "Grep", "input_slot": "gi"},
]

SAMPLE_TOOL_USE_RESULT = {"stdout": "match found", "stderr": "", "interrupted": False}
