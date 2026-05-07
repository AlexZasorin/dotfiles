"""Tests for validate.py — structural validator for assembled session records."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Allow running from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))
import validate  # type: ignore[import-not-found]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_uuid(n: int) -> str:
    """Stable deterministic uuid for tests."""
    return f"00000000-0000-4000-8000-{n:012d}"


def _make_ts(n: int) -> str:
    """Monotonically increasing timestamps by second offset."""
    return f"2026-01-01T00:00:{n:02d}.000Z"


def _minimal_user(i: int, parent: int | None = None) -> dict:
    return {
        "type": "user",
        "uuid": _make_uuid(i),
        "timestamp": _make_ts(i),
        "parentUuid": _make_uuid(parent) if parent is not None else None,
        "isSidechain": False,
        "message": {"role": "user", "content": "hello"},
    }


def _minimal_assistant(i: int, parent: int) -> dict:
    return {
        "type": "assistant",
        "uuid": _make_uuid(i),
        "timestamp": _make_ts(i),
        "parentUuid": _make_uuid(parent),
        "isSidechain": False,
        "message": {"role": "assistant", "content": [], "model": "claude-opus"},
    }


def _minimal_hook(i: int) -> dict:
    return {
        "type": "progress",
        "uuid": _make_uuid(i),
        "timestamp": _make_ts(i),
        "parentUuid": None,
        "isSidechain": False,
        "data": {"type": "hook_progress", "hookEvent": "SessionStart"},
    }


# ---------------------------------------------------------------------------
# TestStructuralRules
# ---------------------------------------------------------------------------


class TestStructuralRules(unittest.TestCase):
    def test_empty_records_returns_error(self):
        errors = validate.validate([])
        self.assertEqual(errors, ["records list is empty"])

    def test_valid_minimal_session_passes(self):
        """A hook + user + assistant chain should produce no errors."""
        records = [
            _minimal_hook(0),
            _minimal_user(1),
            _minimal_assistant(2, parent=1),
        ]
        errors = validate.validate(records)
        self.assertEqual(errors, [], f"Expected no errors, got: {errors}")

    def test_missing_uuid_flagged(self):
        """Record without uuid field → missing or null uuid."""
        rec = _minimal_user(1)
        del rec["uuid"]
        errors = validate.validate([rec])
        self.assertTrue(
            any("missing or null uuid" in e for e in errors),
            f"Expected uuid error, got: {errors}",
        )

    def test_null_uuid_flagged(self):
        """uuid=None is treated as missing (V1)."""
        rec = _minimal_user(1)
        rec["uuid"] = None
        errors = validate.validate([rec])
        self.assertTrue(
            any("missing or null uuid" in e for e in errors),
            f"Expected uuid null error, got: {errors}",
        )

    def test_null_timestamp_flagged(self):
        """timestamp=None is treated as missing (V1)."""
        rec = _minimal_user(1)
        rec["timestamp"] = None
        errors = validate.validate([rec])
        self.assertTrue(
            any("missing or null timestamp" in e for e in errors),
            f"Expected timestamp null error, got: {errors}",
        )

    def test_duplicate_uuid_detected(self):
        """Two records with same uuid → duplicate uuid error."""
        same_uuid = _make_uuid(5)
        rec1 = _minimal_user(1)
        rec1["uuid"] = same_uuid
        rec2 = _minimal_assistant(2, parent=1)
        rec2["uuid"] = same_uuid
        errors = validate.validate([rec1, rec2])
        self.assertTrue(
            any("duplicate uuid" in e for e in errors),
            f"Expected duplicate uuid error, got: {errors}",
        )

    def test_dangling_parent_uuid_silent_for_cross_file(self):
        """A parentUuid that doesn't appear in this file is silently accepted.

        This covers cross-file references — e.g. a subagent file where the
        first record's parentUuid refers to a record in the parent session file.
        """
        rec = _minimal_user(1)
        rec["parentUuid"] = "deadbeef-dead-beef-dead-beefdeadbeef"  # not in this file
        errors = validate.validate([rec])
        self.assertEqual(
            errors,
            [],
            f"Cross-file parentUuid should not error, got: {errors}",
        )

    def test_empty_string_parent_uuid_accepted(self):
        """parentUuid='' is normalized to None and accepted (F10 edge case)."""
        rec = _minimal_user(1)
        rec["parentUuid"] = ""
        errors = validate.validate([rec])
        self.assertEqual(
            errors,
            [],
            f"Empty-string parentUuid should be accepted, got: {errors}",
        )

    def test_non_monotonic_timestamps_accepted(self):
        """Non-monotonic timestamps are accepted — real files violate ordering frequently.

        ~40% of real Claude Code session files have non-monotonic timestamps
        (attachment and tool-result records can arrive slightly before the
        record that logically precedes them).  We only validate parsability.
        """
        rec1 = _minimal_user(1)
        rec1["timestamp"] = "2026-01-01T00:00:10.000Z"
        rec2 = _minimal_assistant(2, parent=1)
        rec2["timestamp"] = "2026-01-01T00:00:05.000Z"  # goes backwards
        errors = validate.validate([rec1, rec2])
        self.assertFalse(
            any("non-monotonic" in e for e in errors),
            f"Non-monotonic timestamps should not error, got: {errors}",
        )

    def test_equal_timestamps_allowed(self):
        """Two records with identical timestamps must NOT produce an error.

        Real files have many equal timestamps (1ms granularity).
        """
        ts = "2026-01-01T00:00:10.000Z"
        rec1 = _minimal_user(1)
        rec1["timestamp"] = ts
        rec2 = _minimal_assistant(2, parent=1)
        rec2["timestamp"] = ts
        errors = validate.validate([rec1, rec2])
        self.assertEqual(
            errors,
            [],
            f"Equal timestamps should be allowed, got: {errors}",
        )

    def test_malformed_timestamp_flagged(self):
        """A timestamp that cannot be parsed → error."""
        rec = _minimal_user(1)
        rec["timestamp"] = "not-a-timestamp"
        errors = validate.validate([rec])
        self.assertTrue(
            any("malformed timestamp" in e for e in errors),
            f"Expected malformed timestamp error, got: {errors}",
        )


# ---------------------------------------------------------------------------
# TestFlatMetaTypes
# ---------------------------------------------------------------------------


class TestFlatMetaTypes(unittest.TestCase):
    def _make_base_session(self):
        """Returns a minimal [hook, user] session for attaching meta records to."""
        return [_minimal_hook(0), _minimal_user(1)]

    def test_queue_operation_passes(self):
        """queue-operation records (no uuid/timestamp) must pass without errors (V2)."""
        records = [
            {
                "type": "queue-operation",
                "operation": "enqueue",
                "timestamp": "2026-01-01T00:00:00.159Z",
                "sessionId": "some-session-id",
                "content": "do something",
            },
            _minimal_user(1),
            _minimal_assistant(2, parent=1),
        ]
        errors = validate.validate(records)
        self.assertEqual(errors, [], f"Expected no errors, got: {errors}")

    def test_permission_mode_passes(self):
        """permission-mode flat-meta records (no uuid/timestamp) must pass."""
        records = [
            {
                "type": "permission-mode",
                "permissionMode": "default",
                "sessionId": "some-session-id",
            },
            _minimal_user(1),
            _minimal_assistant(2, parent=1),
        ]
        errors = validate.validate(records)
        self.assertEqual(errors, [], f"Expected no errors, got: {errors}")

    def test_file_history_snapshot_with_matching_anchor_passes(self):
        """Snapshot whose messageId resolves to a record uuid → no V4 error."""
        user_uuid = _make_uuid(1)
        user_rec = _minimal_user(1)
        user_rec["uuid"] = user_uuid
        snapshot = {
            "type": "file-history-snapshot",
            "messageId": user_uuid,
            "snapshot": {"messageId": user_uuid, "trackedFileBackups": {}, "timestamp": "2026-01-01T00:00:02.000Z"},
            "isSnapshotUpdate": False,
        }
        records = [_minimal_hook(0), user_rec, snapshot]
        errors = validate.validate(records)
        self.assertEqual(errors, [], f"Expected no errors, got: {errors}")

    def test_file_history_snapshot_with_dangling_anchor_flagged(self):
        """Snapshot whose messageId doesn't match any record uuid → V4 error."""
        snapshot = {
            "type": "file-history-snapshot",
            "messageId": "nonexistent-uuid-0000-0000-000000000000",
            "snapshot": {
                "messageId": "nonexistent-uuid-0000-0000-000000000000",
                "trackedFileBackups": {},
                "timestamp": "2026-01-01T00:00:01.000Z",
            },
            "isSnapshotUpdate": False,
        }
        records = [_minimal_user(1), snapshot]
        errors = validate.validate(records)
        self.assertTrue(
            any("file-history-snapshot" in e for e in errors),
            f"Expected V4 snapshot anchor error, got: {errors}",
        )


# ---------------------------------------------------------------------------
# TestSlotScan
# ---------------------------------------------------------------------------


class TestSlotScan(unittest.TestCase):
    def test_unfilled_slot_in_user_content_flagged(self):
        """A {_slot: ...} marker nested in a record's message.content → error."""
        rec = _minimal_user(1)
        rec["message"]["content"] = {"_slot": "u"}
        errors = validate.validate([rec])
        self.assertTrue(
            any("unfilled slot" in e for e in errors),
            f"Expected slot error, got: {errors}",
        )

    def test_unfilled_slot_in_nested_progress_flagged(self):
        """Slot marker inside data.message.message.content is detected (V5).

        data.message represents a subagent record. The validator must recurse
        into it but should NOT add the inner uuid to the parent's seen_uuids.
        """
        inner_record = {
            "type": "assistant",
            "uuid": _make_uuid(99),
            "timestamp": _make_ts(2),
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": {"_slot": "inner_text"}}],
            },
        }
        progress_rec = {
            "type": "progress",
            "uuid": _make_uuid(2),
            "timestamp": _make_ts(2),
            "parentUuid": _make_uuid(1),
            "isSidechain": False,
            "data": {
                "type": "agent_progress",
                "agentId": "a1234567",
                "message": inner_record,
            },
        }
        records = [_minimal_user(1), progress_rec]
        errors = validate.validate(records)
        self.assertTrue(
            any("unfilled slot" in e for e in errors),
            f"Expected nested slot error, got: {errors}",
        )

    def test_clean_record_has_no_slot_error(self):
        """Records without slot markers must not trigger slot errors."""
        records = [_minimal_user(1), _minimal_assistant(2, parent=1)]
        errors = validate.validate(records)
        self.assertFalse(
            any("unfilled slot" in e for e in errors),
            f"Unexpected slot error in clean records: {errors}",
        )


# ---------------------------------------------------------------------------
# TestPairingChecks
# ---------------------------------------------------------------------------


def _make_tool_use_id(n: int) -> str:
    return f"toolu_011{'a' * 18}{n:04d}"


class TestPairingChecks(unittest.TestCase):
    def _make_assistant_with_tool_use(self, i: int, parent: int, tu_id: str) -> dict:
        rec = _minimal_assistant(i, parent)
        rec["message"]["content"] = [
            {"type": "tool_use", "id": tu_id, "name": "Bash", "input": {"cmd": "ls"}}
        ]
        return rec

    def _make_tool_result_user(self, i: int, parent: int, tu_id: str, asst_uuid: str) -> dict:
        rec = {
            "type": "user",
            "uuid": _make_uuid(i),
            "timestamp": _make_ts(i),
            "parentUuid": _make_uuid(parent),
            "isSidechain": False,
            "sourceToolAssistantUUID": asst_uuid,
            "message": {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": tu_id, "content": "output"}
                ],
            },
        }
        return rec

    def test_orphan_tool_result_flagged(self):
        """tool_result with a tool_use_id not emitted by any assistant → V3 error."""
        fake_tu_id = "toolu_011nonexistentXXXXXXXXXXXXXXXXXXXX"
        user_rec = _minimal_user(1)
        # Build a tool-result user record that references an unknown tool_use_id
        tool_result_rec = {
            "type": "user",
            "uuid": _make_uuid(2),
            "timestamp": _make_ts(2),
            "parentUuid": _make_uuid(1),
            "isSidechain": False,
            "sourceToolAssistantUUID": _make_uuid(99),  # also unknown
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": fake_tu_id,
                        "content": "some output",
                    }
                ],
            },
        }
        records = [user_rec, tool_result_rec]
        errors = validate.validate(records)
        self.assertTrue(
            any("tool_result references unknown tool_use_id" in e for e in errors),
            f"Expected tool_result pairing error, got: {errors}",
        )

    def test_paired_tool_result_passes(self):
        """tool_result paired with a prior assistant tool_use → no V3 error."""
        tu_id = _make_tool_use_id(1)
        user1 = _minimal_user(1)
        asst = self._make_assistant_with_tool_use(2, parent=1, tu_id=tu_id)
        tr_user = self._make_tool_result_user(3, parent=2, tu_id=tu_id, asst_uuid=_make_uuid(2))
        records = [user1, asst, tr_user]
        errors = validate.validate(records)
        self.assertEqual(errors, [], f"Expected no errors for paired tool_result, got: {errors}")

    def test_unknown_source_tool_assistant_uuid_flagged(self):
        """sourceToolAssistantUUID not matching any assistant uuid → V3 error."""
        tu_id = _make_tool_use_id(1)
        user1 = _minimal_user(1)
        asst = self._make_assistant_with_tool_use(2, parent=1, tu_id=tu_id)
        tr_user = self._make_tool_result_user(
            3, parent=2, tu_id=tu_id,
            asst_uuid="deadbeef-dead-beef-dead-000000000000"  # unknown
        )
        records = [user1, asst, tr_user]
        errors = validate.validate(records)
        self.assertTrue(
            any("sourceToolAssistantUUID" in e for e in errors),
            f"Expected sourceToolAssistantUUID error, got: {errors}",
        )

    def test_subagent_file_skips_pairing_checks(self):
        """Subagent files (first record isSidechain=True) skip V3 cross-reference checks.

        In subagent files, the assistant tool_use blocks live in the parent session
        file. The orphan tool_results here are expected — not errors.
        """
        fake_tu_id = "toolu_011orphanXXXXXXXXXXXXXXXXXXXXXX"
        # First record has isSidechain=True — marks this as a subagent file
        first_user = _minimal_user(1)
        first_user["isSidechain"] = True
        # A tool_result with an "orphan" tool_use_id (tool_use is in parent file)
        tool_result_rec = {
            "type": "user",
            "uuid": _make_uuid(2),
            "timestamp": _make_ts(2),
            "parentUuid": _make_uuid(1),
            "isSidechain": True,
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": fake_tu_id,
                        "content": "output from parent tool_use",
                    }
                ],
            },
        }
        records = [first_user, tool_result_rec]
        errors = validate.validate(records)
        self.assertFalse(
            any("tool_result references unknown tool_use_id" in e for e in errors),
            f"Subagent file should skip pairing checks, got: {errors}",
        )


# ---------------------------------------------------------------------------
# TestRealFileRoundtrip (T1 — CRITICAL)
# ---------------------------------------------------------------------------


class TestRealFileRoundtrip(unittest.TestCase):
    """Validate 5 random real session files from ~/.claude/projects.

    This is the spec's 'validate against all real files before first use' test,
    sampled to 5 random files to keep the suite fast.
    """

    def test_real_files_validate_clean(self):
        import glob
        import random

        pattern = str(Path.home() / ".claude" / "projects" / "**" / "*.jsonl")
        all_files = glob.glob(pattern, recursive=True)
        if not all_files:
            self.skipTest("No real session files found at ~/.claude/projects")

        random.seed(42)  # deterministic sample
        sample = random.sample(all_files, min(5, len(all_files)))

        failed = []
        for path in sample:
            errors = validate.validate_jsonl_file(path)
            if errors:
                failed.append((path, errors[:3]))

        if failed:
            msgs = []
            for path, errs in failed:
                msgs.append(f"\n  {path}:\n    " + "\n    ".join(errs))
            self.fail("Real files failed validation:" + "".join(msgs))


# ---------------------------------------------------------------------------
# TestValidateJsonlFile
# ---------------------------------------------------------------------------


class TestValidateJsonlFile(unittest.TestCase):
    def test_writes_then_validates(self):
        """Writing valid records to a .jsonl file and calling validate_jsonl_file returns []."""
        records = [
            _minimal_user(1),
            _minimal_assistant(2, parent=1),
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")
            tmp_path = f.name
        errors = validate.validate_jsonl_file(tmp_path)
        self.assertEqual(errors, [], f"Expected no errors, got: {errors}")

    def test_malformed_json_returns_parse_error(self):
        """A file containing invalid JSON returns a parse error (not a crash)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("{not valid json\n")
            tmp_path = f.name
        errors = validate.validate_jsonl_file(tmp_path)
        self.assertTrue(
            errors and "cannot parse" in errors[0],
            f"Expected parse error, got: {errors}",
        )


if __name__ == "__main__":
    unittest.main()
