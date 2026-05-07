"""
Tests for validate_template.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import validate_template  # type: ignore[import-not-found]


def _write_json(data: object) -> Path:
    """Write data to a temp file and return its Path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(data, tmp)
    tmp.flush()
    tmp.close()
    return Path(tmp.name)


def _valid_template() -> dict:
    return {
        "archetype": "typescript-bug-fix",
        "authoring_note": "Derived from 12 representative sessions",
        "length_distribution": {
            "min_records": 10,
            "typical": 50,
            "max": 200,
        },
        "model_weights": {
            "claude-opus-4-7": 0.7,
            "claude-haiku-4-5": 0.3,
        },
        "subagent_probability": 0.2,
        "events": [
            {"kind": "user_turn", "content_slot": "initial-prompt"},
            {
                "kind": "assistant_turn",
                "blocks": [{"type": "text", "slot": "response-text"}],
            },
        ],
    }


class TestValidateTemplate(unittest.TestCase):
    def test_valid_passes(self):
        path = _write_json(_valid_template())
        errors = validate_template.validate(path)
        self.assertEqual(errors, [])

    def test_missing_archetype(self):
        data = _valid_template()
        del data["archetype"]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("archetype" in e for e in errors))

    def test_archetype_not_kebab_case(self):
        data = _valid_template()
        data["archetype"] = "TypeScript Bug Fix"
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("kebab" in e.lower() for e in errors))

    def test_model_weights_dont_sum_to_one(self):
        data = _valid_template()
        data["model_weights"] = {"claude-opus-4-7": 0.5, "claude-haiku-4-5": 0.4}
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("model_weights" in e and "sum" in e for e in errors))

    def test_model_weights_null(self):
        data = _valid_template()
        data["model_weights"] = None
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("model_weights" in e and "NoneType" in e for e in errors))

    def test_model_weights_empty(self):
        data = _valid_template()
        data["model_weights"] = {}
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("model_weights" in e and "empty" in e for e in errors))

    def test_subagent_probability_out_of_range_high(self):
        data = _valid_template()
        data["subagent_probability"] = 1.5
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("subagent_probability" in e for e in errors))

    def test_subagent_probability_out_of_range_low(self):
        data = _valid_template()
        data["subagent_probability"] = -0.1
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("subagent_probability" in e for e in errors))

    def test_subagent_probability_zero_valid(self):
        data = _valid_template()
        data["subagent_probability"] = 0
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertEqual(errors, [])

    def test_subagent_probability_one_valid(self):
        data = _valid_template()
        data["subagent_probability"] = 1.0
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertEqual(errors, [])

    def test_duplicate_slot_id(self):
        data = _valid_template()
        data["events"] = [
            {"kind": "user_turn", "content_slot": "slot-a"},
            {"kind": "user_turn", "content_slot": "slot-a"},  # duplicate
        ]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("Duplicate" in e and "slot-a" in e for e in errors))

    def test_duplicate_slot_across_blocks(self):
        data = _valid_template()
        data["events"] = [
            {
                "kind": "assistant_turn",
                "blocks": [
                    {"type": "text", "slot": "shared-slot"},
                    {"type": "text", "slot": "shared-slot"},
                ],
            }
        ]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("Duplicate" in e and "shared-slot" in e for e in errors))

    def test_unknown_event_kind(self):
        data = _valid_template()
        data["events"] = [{"kind": "unknown_event_type"}]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("unknown" in e.lower() and "unknown_event_type" in e for e in errors))

    def test_unknown_block_type(self):
        data = _valid_template()
        data["events"] = [
            {
                "kind": "assistant_turn",
                "blocks": [{"type": "invalid_block_type"}],
            }
        ]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(
            any("invalid_block_type" in e for e in errors)
        )

    def test_length_distribution_ordering(self):
        data = _valid_template()
        data["length_distribution"] = {"min_records": 100, "typical": 50, "max": 200}
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("ordering" in e or "min_records" in e for e in errors))

    def test_length_distribution_null(self):
        data = _valid_template()
        data["length_distribution"] = None
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("length_distribution" in e and "NoneType" in e for e in errors))

    def test_blocks_wrong_type(self):
        data = _valid_template()
        data["events"] = [
            {
                "kind": "assistant_turn",
                "blocks": "not-a-list",
            }
        ]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("blocks" in e and ("list" in e or "str" in e) for e in errors))

    def test_permission_mode_event_accepted(self):
        """permission_mode is a valid event kind — must not produce errors."""
        data = _valid_template()
        data["events"] = [{"kind": "permission_mode", "mode": "plan"}]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertEqual(errors, [])

    def test_system_turn_duration_event_accepted(self):
        """system_turn_duration is a valid event kind — must not produce errors."""
        data = _valid_template()
        data["events"] = [
            {"kind": "system_turn_duration", "duration_ms": 1500, "message_count": 3}
        ]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertEqual(errors, [])

    def test_all_valid_event_kinds_accepted(self):
        """All 8 event kinds must be accepted without errors."""
        data = _valid_template()
        data["events"] = [
            {"kind": "hook"},
            {"kind": "file_snapshot"},
            {"kind": "user_turn"},
            {"kind": "assistant_turn", "blocks": [{"type": "text"}]},
            {"kind": "tool_result", "result_kind": "string"},
            {"kind": "subagent", "template": "explore-codebase"},
            {"kind": "permission_mode", "mode": "auto"},
            {"kind": "system_turn_duration", "duration_ms": 100, "message_count": 1},
        ]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertEqual(errors, [])

    def test_subagent_event_missing_template(self):
        data = _valid_template()
        data["events"] = [{"kind": "subagent", "template": ""}]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("subagent" in e and "template" in e for e in errors))

    def test_tool_result_unknown_result_kind(self):
        data = _valid_template()
        data["events"] = [{"kind": "tool_result", "result_kind": "binary"}]
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("result_kind" in e for e in errors))

    def test_events_empty_list(self):
        data = _valid_template()
        data["events"] = []
        path = _write_json(data)
        errors = validate_template.validate(path)
        self.assertTrue(any("events" in e and "empty" in e for e in errors))

    def test_missing_multiple_fields_all_reported(self):
        """All missing required fields should be reported, not just the first."""
        data = {}
        path = _write_json(data)
        errors = validate_template.validate(path)
        required = {"archetype", "authoring_note", "length_distribution",
                    "model_weights", "subagent_probability", "events"}
        for field in required:
            self.assertTrue(
                any(field in e for e in errors),
                f"Expected error about missing '{field}' but got: {errors}",
            )


class TestValidateTemplateMain(unittest.TestCase):
    def test_main_valid_returns_zero(self):
        path = _write_json(_valid_template())
        result = validate_template._main(["prog", str(path)])
        self.assertEqual(result, 0)

    def test_main_invalid_returns_one(self):
        data = _valid_template()
        data["subagent_probability"] = 5.0
        path = _write_json(data)
        result = validate_template._main(["prog", str(path)])
        self.assertEqual(result, 1)

    def test_main_usage_error_returns_two(self):
        result = validate_template._main(["prog"])
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
