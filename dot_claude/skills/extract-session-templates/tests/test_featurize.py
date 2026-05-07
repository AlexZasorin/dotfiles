"""
Tests for featurize.py
"""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import featurize  # type: ignore[import-not-found]

from tests.fixtures import (  # type: ignore[import-not-found]
    ASSISTANT_TURN_AGENT_DELEGATION,
    ASSISTANT_TURN_TEXT,
    ASSISTANT_TURN_THINKING,
    ASSISTANT_TURN_TOOL_USE,
    FILE_HISTORY_SNAPSHOT,
    HOOK_PROGRESS_SESSION_START,
    SUBAGENT_USER_TURN,
    USER_TURN_STRING,
    USER_TURN_TOOL_RESULT,
    minimal_session,
    session_with_delegation,
    subagent_session,
)


class TestDeriveProjectSlug(unittest.TestCase):
    def test_first_path_component(self):
        root = Path("/home/user/.claude/projects")
        path = Path("/home/user/.claude/projects/my-project/session.jsonl")
        slug = featurize._derive_project_slug(root, path)
        self.assertEqual(slug, "my-project")

    def test_nested_subagent_path(self):
        root = Path("/home/user/.claude/projects")
        path = Path(
            "/home/user/.claude/projects/my-project/abc123/subagents/agent-xyz.jsonl"
        )
        slug = featurize._derive_project_slug(root, path)
        self.assertEqual(slug, "my-project")

    def test_path_not_under_root(self):
        root = Path("/home/user/.claude/projects")
        path = Path("/tmp/some.jsonl")
        slug = featurize._derive_project_slug(root, path)
        self.assertEqual(slug, "")


class TestDeriveIsSubagent(unittest.TestCase):
    def test_subagent_in_path(self):
        path = Path("/projects/my-proj/abc123/subagents/agent-xyz.jsonl")
        self.assertTrue(featurize._derive_is_subagent(path))

    def test_regular_session(self):
        path = Path("/projects/my-proj/session-id.jsonl")
        self.assertFalse(featurize._derive_is_subagent(path))


class TestExtractToolSequence(unittest.TestCase):
    def test_extracts_tool_names_in_order(self):
        records = session_with_delegation()
        seq = featurize.extract_tool_sequence(records)
        self.assertIn("Agent", seq)
        self.assertIn("Grep", seq)
        self.assertEqual(seq.index("Agent"), 0)

    def test_skips_non_dict_blocks(self):
        records = [
            {
                "type": "assistant",
                "message": {
                    "content": [
                        "not a dict",
                        {"type": "tool_use", "name": "Read"},
                    ]
                },
            }
        ]
        seq = featurize.extract_tool_sequence(records)
        self.assertEqual(seq, ["Read"])

    def test_empty_records(self):
        self.assertEqual(featurize.extract_tool_sequence([]), [])

    def test_no_tool_use_blocks(self):
        records = minimal_session()
        seq = featurize.extract_tool_sequence(records)
        self.assertEqual(seq, [])

    def test_agent_not_task(self):
        """Delegation uses 'Agent' tool name, not 'Task' — ensure we track 'Agent'."""
        records = session_with_delegation()
        seq = featurize.extract_tool_sequence(records)
        self.assertIn("Agent", seq)
        self.assertNotIn("Task", seq)


class TestSessionLength(unittest.TestCase):
    def test_minimal_session(self):
        records = minimal_session()
        self.assertEqual(featurize.session_length(records), 3)

    def test_empty(self):
        self.assertEqual(featurize.session_length([]), 0)


class TestSessionDurationSeconds(unittest.TestCase):
    def test_duration_from_top_level_timestamps(self):
        records = minimal_session()
        # FILE_HISTORY_SNAPSHOT has no top-level timestamp, uses snapshot.timestamp
        # USER_TURN_STRING: 10:00:10, ASSISTANT_TURN_TEXT: 10:00:45
        # snapshot timestamp: 10:00:05
        # Expect: 10:00:45 - 10:00:05 = 40 seconds
        duration = featurize.session_duration_seconds(records)
        self.assertAlmostEqual(duration, 40.0, places=1)

    def test_snapshot_timestamp_fallback(self):
        """FILE_HISTORY_SNAPSHOT has no top-level timestamp — uses snapshot.timestamp."""
        records = [FILE_HISTORY_SNAPSHOT]
        # Only one timestamp source → returns 0.0 (need at least 2)
        # But paired with another:
        records_pair = [FILE_HISTORY_SNAPSHOT, USER_TURN_STRING]
        # snapshot: 10:00:05, user: 10:00:10 → 5 seconds
        duration = featurize.session_duration_seconds(records_pair)
        self.assertAlmostEqual(duration, 5.0, places=1)

    def test_single_timestamp_returns_zero(self):
        records = [USER_TURN_STRING]
        self.assertEqual(featurize.session_duration_seconds(records), 0.0)

    def test_no_timestamps_returns_zero(self):
        # Remove timestamp from records
        record = {"type": "user", "message": {"content": "hello"}}
        self.assertEqual(featurize.session_duration_seconds([record]), 0.0)

    def test_duration_with_delegation_session(self):
        records = session_with_delegation()
        duration = featurize.session_duration_seconds(records)
        self.assertGreater(duration, 0.0)


class TestSubagentDelegationCount(unittest.TestCase):
    def test_counts_agent_tool_use(self):
        records = session_with_delegation()
        count = featurize.subagent_delegation_count(records)
        self.assertEqual(count, 1)

    def test_zero_for_no_delegation(self):
        records = minimal_session()
        self.assertEqual(featurize.subagent_delegation_count(records), 0)

    def test_task_tool_not_counted(self):
        """'Task' tool should NOT be counted — only 'Agent'."""
        records = [
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Task",
                            "id": "toolu_task_001",
                        }
                    ]
                },
            }
        ]
        self.assertEqual(featurize.subagent_delegation_count(records), 0)

    def test_multiple_delegations(self):
        # Two Agent delegations
        records = [ASSISTANT_TURN_AGENT_DELEGATION, ASSISTANT_TURN_AGENT_DELEGATION]
        self.assertEqual(featurize.subagent_delegation_count(records), 2)


class TestModelMix(unittest.TestCase):
    def test_model_from_assistant_records(self):
        records = minimal_session()
        mix = featurize.model_mix(records)
        self.assertIn("claude-opus-4-7", mix)
        self.assertEqual(mix["claude-opus-4-7"], 1)

    def test_multiple_models(self):
        assistant1 = dict(ASSISTANT_TURN_TEXT)
        assistant1["message"] = dict(assistant1["message"])
        assistant1["message"]["model"] = "claude-haiku-4-5"
        records = [ASSISTANT_TURN_TEXT, assistant1]
        mix = featurize.model_mix(records)
        self.assertEqual(mix.get("claude-opus-4-7", 0), 1)
        self.assertEqual(mix.get("claude-haiku-4-5", 0), 1)

    def test_empty_if_no_assistant_records(self):
        records = [USER_TURN_STRING]
        mix = featurize.model_mix(records)
        self.assertEqual(mix, {})


class TestUsesPlanMode(unittest.TestCase):
    def test_false_for_default_mode(self):
        records = minimal_session()
        self.assertFalse(featurize.uses_plan_mode(records))

    def test_true_for_plan_mode(self):
        plan_user = dict(USER_TURN_STRING)
        plan_user = {**USER_TURN_STRING, "permissionMode": "plan"}
        records = [plan_user]
        self.assertTrue(featurize.uses_plan_mode(records))

    def test_false_for_empty(self):
        self.assertFalse(featurize.uses_plan_mode([]))


class TestTopicFingerprint(unittest.TestCase):
    def test_extracts_tokens_from_first_user_turn(self):
        records = minimal_session()
        fp = featurize.topic_fingerprint(records)
        # "fix the bug in parser.ts" → stopwords removed: "fix", "bug", "parser"
        self.assertIn("fix", fp)
        self.assertIn("bug", fp)
        self.assertIn("parser", fp)
        # "the", "in" should be filtered out
        self.assertNotIn("the", fp)
        self.assertNotIn("in", fp)

    def test_skips_sidechain_turns(self):
        """Sidechain user turns should be skipped; use first non-sidechain turn."""
        records = [SUBAGENT_USER_TURN, USER_TURN_STRING]
        fp = featurize.topic_fingerprint(records)
        # Should fingerprint USER_TURN_STRING ("fix the bug..."), not SUBAGENT
        self.assertIn("fix", fp)
        # "search", "codebase", "typescript", "parsers" from subagent should NOT dominate
        # but they may not appear as first non-sidechain turn content
        self.assertNotIn("search", fp)

    def test_skips_tool_result_content(self):
        """First non-sidechain user turn with list content (tool result) should be skipped."""
        records = [USER_TURN_TOOL_RESULT, USER_TURN_STRING]
        fp = featurize.topic_fingerprint(records)
        # USER_TURN_TOOL_RESULT has list content, not string → skipped
        # USER_TURN_STRING has "fix the bug in parser.ts"
        self.assertIn("fix", fp)

    def test_returns_empty_set_for_no_user_turns(self):
        fp = featurize.topic_fingerprint([ASSISTANT_TURN_TEXT])
        self.assertEqual(fp, set())

    def test_filters_short_tokens(self):
        record = {
            **USER_TURN_STRING,
            "message": {"role": "user", "content": "do it now ab cd xyz"},
        }
        fp = featurize.topic_fingerprint([record])
        self.assertNotIn("do", fp)
        self.assertNotIn("it", fp)
        self.assertNotIn("ab", fp)
        self.assertNotIn("cd", fp)
        self.assertIn("xyz", fp)


class TestStopwords(unittest.TestCase):
    def test_is_frozenset(self):
        self.assertIsInstance(featurize._STOPWORDS, frozenset)

    def test_contains_common_words(self):
        for word in ["the", "and", "not", "use", "what", "when"]:
            self.assertIn(word, featurize._STOPWORDS)


class TestCSVWriteIntegration(unittest.TestCase):
    def test_write_csv_integration(self):
        """Integration test: write a real .jsonl file and verify CSV output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            project_dir = root / "my-project"
            project_dir.mkdir()

            session_id = "abc123-def456"
            session_file = project_dir / f"{session_id}.jsonl"

            records = minimal_session()
            with session_file.open("w") as fh:
                for r in records:
                    fh.write(json.dumps(r) + "\n")

            out_csv = root / "features.csv"
            count = featurize.write_csv(root, out_csv)

            self.assertEqual(count, 1)
            self.assertTrue(out_csv.exists())

            with out_csv.open() as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)

            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["project_slug"], "my-project")
            self.assertEqual(row["session_id"], session_id)
            self.assertEqual(row["is_subagent"], "False")
            self.assertEqual(row["length"], "3")
            self.assertIn("fix", row["topic_fingerprint"])

    def test_write_csv_with_subagent(self):
        """Subagent files in 'subagents/' subdirectory are tracked as is_subagent=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            project_dir = root / "my-project" / "session-parent" / "subagents"
            project_dir.mkdir(parents=True)

            agent_file = project_dir / "agent-abc123.jsonl"
            records = subagent_session()
            with agent_file.open("w") as fh:
                for r in records:
                    fh.write(json.dumps(r) + "\n")

            out_csv = root / "features.csv"
            featurize.write_csv(root, out_csv)

            with out_csv.open() as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["is_subagent"], "True")
            self.assertEqual(rows[0]["project_slug"], "my-project")


if __name__ == "__main__":
    unittest.main()
