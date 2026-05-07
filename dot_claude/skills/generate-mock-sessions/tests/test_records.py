"""Tests for records.py — pure record-building primitives."""
import re
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

# Make records importable from the skill directory
sys.path.insert(0, str(Path(__file__).parent.parent))
import records  # type: ignore[import-not-found]

from tests.fixtures import (  # type: ignore[import-not-found]
    SAMPLE_BLOCKS_SPEC_TEXT,
    SAMPLE_BLOCKS_SPEC_THINKING_TOOL,
    SAMPLE_TOOL_USE_RESULT,
)

_UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


def _make_context(is_sidechain: bool = False) -> records.SessionContext:
    return records.SessionContext(
        session_id="test-session-id",
        project_cwd="/home/user/project",
        git_branch="main",
        version="2.1.91",
        slug="brave-waddling-snail",
        user_type="external",
        entrypoint="cli",
        is_sidechain=is_sidechain,
    )


def _make_ts() -> records.TimestampSequence:
    return records.TimestampSequence(datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc))


# ---------------------------------------------------------------------------
# TestIDGenerators
# ---------------------------------------------------------------------------


class TestIDGenerators(unittest.TestCase):
    def test_new_uuid_matches_v4_regex(self):
        """new_uuid() must produce valid UUID4 strings (F1 fix)."""
        for _ in range(100):
            uid = records.new_uuid()
            self.assertRegex(uid, _UUID4_RE, f"Not a valid v4 UUID: {uid}")

    def test_new_uuid_unique_across_100(self):
        ids = [records.new_uuid() for _ in range(100)]
        self.assertEqual(len(set(ids)), 100)

    def test_new_request_id_prefix_and_length(self):
        rid = records.new_request_id()
        self.assertTrue(rid.startswith("req_011"), f"Bad prefix: {rid}")
        self.assertEqual(len(rid), 29, f"Wrong length: {rid}")

    def test_new_message_id_prefix(self):
        mid = records.new_message_id()
        self.assertTrue(mid.startswith("msg_011"), f"Bad prefix: {mid}")

    def test_new_tool_use_id_prefix(self):
        tid = records.new_tool_use_id()
        self.assertTrue(tid.startswith("toolu_011"), f"Bad prefix: {tid}")

    def test_new_agent_msg_id_prefix(self):
        amid = records.new_agent_msg_id()
        self.assertTrue(amid.startswith("agent_msg_011"), f"Bad prefix: {amid}")

    def test_new_agent_id_prefix_and_lengths(self):
        """new_agent_id() starts with 'a' and is either 7 or 17 chars. Both lengths appear in 200 generations."""
        lengths = set()
        for _ in range(200):
            aid = records.new_agent_id()
            self.assertTrue(aid.startswith("a"), f"Bad prefix: {aid}")
            self.assertIn(len(aid), (7, 17), f"Unexpected length {len(aid)}: {aid}")
            lengths.add(len(aid))
        self.assertIn(7, lengths, "Length-7 agent IDs never appeared in 200 generations")
        self.assertIn(17, lengths, "Length-17 agent IDs never appeared in 200 generations")

    def test_base62_ids_contain_uppercase(self):
        """ID character set includes UPPERCASE letters (verifies base62, not lowercase hex)."""
        combined = "".join(records.new_request_id() for _ in range(50))
        has_upper = any(c.isupper() for c in combined)
        self.assertTrue(has_upper, "No uppercase letters found in 50 request IDs — base62 not used")

    def test_message_ids_contain_uppercase(self):
        combined = "".join(records.new_message_id() for _ in range(50))
        has_upper = any(c.isupper() for c in combined)
        self.assertTrue(has_upper, "No uppercase letters found in 50 message IDs — base62 not used")


# ---------------------------------------------------------------------------
# TestSlugSampler
# ---------------------------------------------------------------------------


class TestSlugSampler(unittest.TestCase):
    def test_slug_shape(self):
        """sample_slug() returns <a>-<b>-<c> shape (3 hyphen-separated parts)."""
        for _ in range(10):
            slug = records.sample_slug()
            parts = slug.split("-")
            self.assertGreaterEqual(
                len(parts), 3,
                f"Slug does not have 3+ parts: {slug}",
            )

    def test_slug_uniqueness(self):
        """100 calls produce >= 50 unique values."""
        slugs = [records.sample_slug() for _ in range(100)]
        self.assertGreaterEqual(len(set(slugs)), 50)


# ---------------------------------------------------------------------------
# TestTimestampSequence
# ---------------------------------------------------------------------------


class TestTimestampSequence(unittest.TestCase):
    def test_progressively_increases(self):
        ts = _make_ts()
        prev = ts.next()
        for _ in range(10):
            curr = ts.next()
            self.assertGreater(curr, prev, "Timestamps not strictly increasing")
            prev = curr

    def test_timestamp_format(self):
        ts = _make_ts()
        for _ in range(10):
            t = ts.next()
            self.assertRegex(t, _TS_RE, f"Bad timestamp format: {t}")

    def test_gap_respects_bounds(self):
        """Timestamps respect min/max gap bounds."""
        from datetime import datetime as dt
        ts = _make_ts()
        # Use tight bounds so we can verify
        t1 = ts.next(min_gap_ms=1000, max_gap_ms=1001)
        t2 = ts.next(min_gap_ms=1000, max_gap_ms=1001)
        d1 = dt.fromisoformat(t1.replace("Z", "+00:00"))
        d2 = dt.fromisoformat(t2.replace("Z", "+00:00"))
        diff_ms = (d2 - d1).total_seconds() * 1000
        self.assertGreaterEqual(diff_ms, 1000)
        self.assertLessEqual(diff_ms, 1001)


# ---------------------------------------------------------------------------
# TestSampling
# ---------------------------------------------------------------------------


class TestSampling(unittest.TestCase):
    def test_weighted_choice_returns_known_key(self):
        weights = {"a": 1.0, "b": 2.0, "c": 0.5}
        for _ in range(100):
            result = records.weighted_choice(weights)
            self.assertIn(result, weights)

    def test_weighted_choice_empty_raises(self):
        with self.assertRaises(ValueError):
            records.weighted_choice({})

    def test_sample_length_within_bounds(self):
        dist = {"min_records": 5, "max": 20, "typical": 10}
        for _ in range(100):
            n = records.sample_length(dist)
            self.assertGreaterEqual(n, 5)
            self.assertLessEqual(n, 20)


# ---------------------------------------------------------------------------
# TestSessionContext
# ---------------------------------------------------------------------------


class TestSessionContext(unittest.TestCase):
    def test_parent_context_includes_entrypoint(self):
        ctx = _make_context(is_sidechain=False)
        fields = records._common_session_fields(ctx)
        self.assertIn("entrypoint", fields)

    def test_sidechain_context_omits_entrypoint(self):
        ctx = _make_context(is_sidechain=True)
        fields = records._common_session_fields(ctx)
        self.assertNotIn("entrypoint", fields)

    def test_both_contexts_include_slug(self):
        for is_sc in (False, True):
            ctx = _make_context(is_sidechain=is_sc)
            fields = records._common_session_fields(ctx)
            self.assertIn("slug", fields, f"slug missing for is_sidechain={is_sc}")


# ---------------------------------------------------------------------------
# TestBuildHook
# ---------------------------------------------------------------------------


class TestBuildHook(unittest.TestCase):
    def test_session_start_hookname_and_command(self):
        ctx = _make_context()
        ts = _make_ts()
        hook = records.build_hook("SessionStart", ts, ctx)
        self.assertEqual(hook["data"]["hookName"], "SessionStart:startup")
        self.assertIn("session-start", hook["data"]["command"])

    def test_post_tool_use_hookname_and_command(self):
        ctx = _make_context()
        ts = _make_ts()
        hook = records.build_hook("PostToolUse", ts, ctx)
        self.assertEqual(hook["data"]["hookName"], "PostToolUse:post-tool-use")
        self.assertIn("post-tool-use", hook["data"]["command"])

    def test_hook_sidechain_aware(self):
        ctx_sc = _make_context(is_sidechain=True)
        ts = _make_ts()
        hook = records.build_hook("SessionStart", ts, ctx_sc)
        self.assertTrue(hook["isSidechain"])

    def test_hook_parent_not_sidechain(self):
        ctx = _make_context(is_sidechain=False)
        ts = _make_ts()
        hook = records.build_hook("SessionStart", ts, ctx)
        self.assertFalse(hook["isSidechain"])


# ---------------------------------------------------------------------------
# TestBuildUserTurn
# ---------------------------------------------------------------------------


class TestBuildUserTurn(unittest.TestCase):
    def test_parent_context_has_prompt_id_and_permission_mode(self):
        ctx = _make_context(is_sidechain=False)
        ts = _make_ts()
        record = records.build_user_turn(None, "hello", ts, ctx)
        self.assertIn("promptId", record)
        self.assertIn("permissionMode", record)
        self.assertIn("entrypoint", record)

    def test_sidechain_context_omits_prompt_id_and_permission_mode(self):
        ctx = _make_context(is_sidechain=True)
        ts = _make_ts()
        record = records.build_user_turn(None, "hello", ts, ctx)
        self.assertNotIn("promptId", record)
        self.assertNotIn("permissionMode", record)
        self.assertNotIn("entrypoint", record)

    def test_reuses_provided_prompt_id(self):
        ctx = _make_context(is_sidechain=False)
        ts = _make_ts()
        pid = "my-prompt-id-123"
        record = records.build_user_turn(None, "hello", ts, ctx, prompt_id=pid)
        self.assertEqual(record["promptId"], pid)

    def test_generates_prompt_id_when_not_provided(self):
        ctx = _make_context(is_sidechain=False)
        ts = _make_ts()
        record = records.build_user_turn(None, "hello", ts, ctx)
        self.assertTrue(record["promptId"])


# ---------------------------------------------------------------------------
# TestBuildToolResult
# ---------------------------------------------------------------------------


class TestBuildToolResult(unittest.TestCase):
    def _build(self, is_error: bool = False, tool_use_result=None, result_kind="string"):
        ctx = _make_context()
        ts = _make_ts()
        return records.build_tool_result(
            parent_uuid="parent-uuid",
            tool_use_id="toolu_abc",
            content="tool output",
            result_kind=result_kind,
            source_tool_assistant_uuid="asst-uuid",
            timestamp_seq=ts,
            context=ctx,
            is_error=is_error,
            tool_use_result=tool_use_result,
        )

    def test_default_no_is_error_key(self):
        """is_error=False → is_error key NOT present in inner block (F9)."""
        record = self._build(is_error=False)
        inner = record["message"]["content"][0]
        self.assertNotIn("is_error", inner)

    def test_explicit_is_error_true_present(self):
        record = self._build(is_error=True)
        inner = record["message"]["content"][0]
        self.assertIn("is_error", inner)
        self.assertTrue(inner["is_error"])

    def test_tool_use_result_present_at_top_level(self):
        record = self._build(tool_use_result=SAMPLE_TOOL_USE_RESULT)
        self.assertIn("toolUseResult", record)
        self.assertEqual(record["toolUseResult"]["stdout"], "match found")

    def test_default_tool_use_result(self):
        record = self._build()
        self.assertIn("toolUseResult", record)
        self.assertIn("stdout", record["toolUseResult"])

    def test_no_permission_mode_or_prompt_id(self):
        record = self._build()
        self.assertNotIn("permissionMode", record)
        self.assertNotIn("promptId", record)

    def test_unknown_result_kind_raises(self):
        with self.assertRaises(ValueError):
            self._build(result_kind="unknown_kind")


# ---------------------------------------------------------------------------
# TestBuildAssistantTurn
# ---------------------------------------------------------------------------


class TestBuildAssistantTurn(unittest.TestCase):
    def _build_text(self):
        ctx = _make_context()
        ts = _make_ts()
        return records.build_assistant_turn(
            parent_uuid=None,
            blocks_spec=SAMPLE_BLOCKS_SPEC_TEXT,
            model="claude-opus-4-5",
            timestamp_seq=ts,
            context=ctx,
        )

    def _build_thinking_tool(self):
        ctx = _make_context()
        ts = _make_ts()
        return records.build_assistant_turn(
            parent_uuid=None,
            blocks_spec=SAMPLE_BLOCKS_SPEC_THINKING_TOOL,
            model="claude-opus-4-5",
            timestamp_seq=ts,
            context=ctx,
        )

    def test_returns_tuple(self):
        result = self._build_text()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_thinking_block_has_signature(self):
        """Thinking block must have non-empty signature >= 100 chars (R2)."""
        record, _ = self._build_thinking_tool()
        content = record["message"]["content"]
        thinking_blocks = [b for b in content if b["type"] == "thinking"]
        self.assertGreater(len(thinking_blocks), 0)
        sig = thinking_blocks[0]["signature"]
        self.assertGreaterEqual(len(sig), 100, f"Signature too short: {len(sig)} chars")

    def test_usage_dict_has_required_keys(self):
        """Usage dict has 7 keys including nested cache_creation and inference_geo (R3)."""
        record, _ = self._build_text()
        usage = record["message"]["usage"]
        self.assertIn("input_tokens", usage)
        self.assertGreater(usage["input_tokens"], 0)
        self.assertIn("output_tokens", usage)
        self.assertIn("cache_creation_input_tokens", usage)
        self.assertIn("cache_read_input_tokens", usage)
        self.assertIn("service_tier", usage)
        self.assertIn("cache_creation", usage)
        cc = usage["cache_creation"]
        self.assertIn("ephemeral_5m_input_tokens", cc)
        self.assertIn("ephemeral_1h_input_tokens", cc)
        self.assertIn("inference_geo", usage)

    def test_stop_details_none_present(self):
        """Message must have stop_details: None (not absent) (R3)."""
        record, _ = self._build_text()
        msg = record["message"]
        self.assertIn("stop_details", msg)
        self.assertIsNone(msg["stop_details"])

    def test_stop_reason_tool_use_when_has_tool(self):
        record, tool_ids = self._build_thinking_tool()
        self.assertEqual(record["message"]["stop_reason"], "tool_use")
        self.assertGreater(len(tool_ids), 0)

    def test_stop_reason_end_turn_when_no_tool(self):
        record, tool_ids = self._build_text()
        self.assertEqual(record["message"]["stop_reason"], "end_turn")
        self.assertEqual(tool_ids, [])

    def test_tool_use_ids_returned(self):
        record, tool_ids = self._build_thinking_tool()
        self.assertEqual(len(tool_ids), 1)
        content = record["message"]["content"]
        tu_blocks = [b for b in content if b["type"] == "tool_use"]
        self.assertEqual(tu_blocks[0]["id"], tool_ids[0])

    def test_unknown_block_type_raises(self):
        ctx = _make_context()
        ts = _make_ts()
        with self.assertRaises(ValueError):
            records.build_assistant_turn(
                parent_uuid=None,
                blocks_spec=[{"type": "unknown_block"}],
                model="claude-opus-4-5",
                timestamp_seq=ts,
                context=ctx,
            )


# ---------------------------------------------------------------------------
# TestBuildAgentProgress
# ---------------------------------------------------------------------------


class TestBuildAgentProgress(unittest.TestCase):
    def _make_inner_user(self):
        ctx = _make_context(is_sidechain=True)
        ts = _make_ts()
        return records.build_user_turn(None, "subagent prompt", ts, ctx)

    def _make_inner_assistant(self):
        ctx = _make_context(is_sidechain=True)
        ts = _make_ts()
        record, _ = records.build_assistant_turn(
            parent_uuid=None,
            blocks_spec=SAMPLE_BLOCKS_SPEC_TEXT,
            model="claude-opus-4-5",
            timestamp_seq=ts,
            context=ctx,
        )
        return record

    def test_stripped_user_message_keys(self):
        """data.message is stripped: only type, message, uuid, timestamp for user (F5)."""
        inner = self._make_inner_user()
        ctx = _make_context(is_sidechain=False)
        ts = _make_ts()
        wrapper = records.build_agent_progress(
            parent_uuid="parent-uuid",
            agent_id="a1234567",
            parent_tool_use_id="toolu_abc",
            inner=inner,
            timestamp_seq=ts,
            context=ctx,
        )
        stripped = wrapper["data"]["message"]
        allowed_keys = {"type", "message", "uuid", "timestamp", "data", "requestId"}
        for key in stripped:
            self.assertIn(key, allowed_keys, f"Unexpected key in stripped message: {key}")
        # Must NOT contain envelope fields
        forbidden = {"parentUuid", "isSidechain", "cwd", "sessionId", "version", "gitBranch", "agentId", "slug", "entrypoint", "userType"}
        for key in forbidden:
            self.assertNotIn(key, stripped, f"Forbidden key found in stripped message: {key}")

    def test_stripped_assistant_message_has_request_id(self):
        """data.message includes requestId for assistant inner (F5)."""
        inner = self._make_inner_assistant()
        ctx = _make_context(is_sidechain=False)
        ts = _make_ts()
        wrapper = records.build_agent_progress(
            parent_uuid="parent-uuid",
            agent_id="a1234567",
            parent_tool_use_id="toolu_abc",
            inner=inner,
            timestamp_seq=ts,
            context=ctx,
        )
        stripped = wrapper["data"]["message"]
        self.assertIn("requestId", stripped)

    def test_delegation_message_id_reused(self):
        """Two wrappers with same delegation_message_id end up with same toolUseID (F6)."""
        inner1 = self._make_inner_user()
        inner2 = self._make_inner_assistant()
        ctx = _make_context(is_sidechain=False)
        ts = _make_ts()
        dm_id = records.new_agent_msg_id()
        w1 = records.build_agent_progress(
            parent_uuid="parent-uuid",
            agent_id="a1234567",
            parent_tool_use_id="toolu_abc",
            inner=inner1,
            timestamp_seq=ts,
            context=ctx,
            delegation_message_id=dm_id,
        )
        w2 = records.build_agent_progress(
            parent_uuid="parent-uuid",
            agent_id="a1234567",
            parent_tool_use_id="toolu_abc",
            inner=inner2,
            timestamp_seq=ts,
            context=ctx,
            delegation_message_id=dm_id,
        )
        self.assertEqual(w1["toolUseID"], w2["toolUseID"])
        self.assertEqual(w1["toolUseID"], dm_id)

    def test_data_agent_id_matches(self):
        inner = self._make_inner_user()
        ctx = _make_context(is_sidechain=False)
        ts = _make_ts()
        agent_id = "a1234567"
        wrapper = records.build_agent_progress(
            parent_uuid="parent-uuid",
            agent_id=agent_id,
            parent_tool_use_id="toolu_abc",
            inner=inner,
            timestamp_seq=ts,
            context=ctx,
        )
        self.assertEqual(wrapper["data"]["agentId"], agent_id)


# ---------------------------------------------------------------------------
# TestMetaRecords
# ---------------------------------------------------------------------------


class TestMetaRecords(unittest.TestCase):
    def test_build_permission_mode_shape(self):
        pm = records.build_permission_mode("default", "session-123")
        self.assertEqual(len(pm), 3)
        self.assertEqual(pm["type"], "permission-mode")
        self.assertEqual(pm["permissionMode"], "default")
        self.assertEqual(pm["sessionId"], "session-123")

    def test_build_system_turn_duration_accepts_none_parent(self):
        """build_system_turn_duration accepts parent_uuid=None and emits parentUuid: None (F10)."""
        ctx = _make_context()
        ts = _make_ts()
        record = records.build_system_turn_duration(
            parent_uuid=None,
            duration_ms=500,
            message_count=3,
            timestamp_seq=ts,
            context=ctx,
        )
        self.assertIn("parentUuid", record)
        self.assertIsNone(record["parentUuid"])

    def test_build_system_turn_duration_parent_uuid_not_empty_string(self):
        ctx = _make_context()
        ts = _make_ts()
        record = records.build_system_turn_duration(
            parent_uuid=None,
            duration_ms=100,
            message_count=1,
            timestamp_seq=ts,
            context=ctx,
        )
        self.assertNotEqual(record["parentUuid"], "")

    def test_build_attachment_includes_envelope_and_data(self):
        ctx = _make_context()
        ts = _make_ts()
        attachment_data = {"kind": "deferred_tools_delta", "tools": []}
        record = records.build_attachment(
            parent_uuid="parent-uuid",
            attachment_data=attachment_data,
            timestamp_seq=ts,
            context=ctx,
        )
        self.assertEqual(record["type"], "attachment")
        self.assertEqual(record["attachment"], attachment_data)
        self.assertIn("uuid", record)
        self.assertIn("timestamp", record)

    def test_build_last_prompt_shape(self):
        lp = records.build_last_prompt("what is 2+2?", "session-456")
        self.assertEqual(len(lp), 3)
        self.assertEqual(lp["type"], "last-prompt")
        self.assertEqual(lp["lastPrompt"], "what is 2+2?")
        self.assertEqual(lp["sessionId"], "session-456")

    def test_build_file_snapshot_shape(self):
        ts = _make_ts()
        msg_id = records.new_uuid()
        snapshot = records.build_file_snapshot(msg_id, ts)
        self.assertEqual(snapshot["type"], "file-history-snapshot")
        self.assertEqual(snapshot["messageId"], msg_id)
        self.assertFalse(snapshot["isSnapshotUpdate"])
        self.assertEqual(snapshot["snapshot"]["messageId"], msg_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
