"""Tests for scaffolder.py — TDD-first, covers all F-prefixed bug fixes."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_SKILL_DIR))

import scaffolder  # type: ignore[import-not-found]
from tests.fixtures import (
    DELEGATION_TEMPLATE,
    FILE_SNAPSHOT_TEMPLATE,
    MINIMAL_TEMPLATE,
    MULTI_TOOL_TEMPLATE,
    SUBAGENT_TEMPLATE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_template(tmp_dir: Path, name: str, template: dict) -> Path:
    """Write a template dict as JSON into tmp_dir/<name>.json."""
    p = tmp_dir / f"{name}.json"
    p.write_text(json.dumps(template))
    return p


def _filled_minimal() -> dict:
    return {"user_q": "Hello world", "asst_a": "Hi there!"}


def _filled_delegation() -> dict:
    return {
        "user_q": "Do some work",
        "agent_input": {"task": "search"},
        "agent_finding": "Found result",
        "synthesis": "Here is the synthesis",
        "sub_user": "Please search",
        "glob_in": {"pattern": "*.py"},
        "glob_out": "file1.py\nfile2.py",
        "sub_reply": "Found 2 Python files",
    }


def _filled_multi_tool() -> dict:
    return {
        "u": "Use two tools",
        "grep_in": {"pattern": "foo"},
        "read_in": {"path": "bar.txt"},
        "grep_out": "grep output",
        "read_out": "file contents",
    }


def _filled_snapshot() -> dict:
    return {"u": "First user message"}


# ---------------------------------------------------------------------------
# TestBuildSkeleton — basic
# ---------------------------------------------------------------------------


class TestBuildSkeleton(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "minimal-test", MINIMAL_TEMPLATE)

    def test_minimal_template_produces_expected_record_types(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        types = [r.get("type") for r in skel["records"]]
        # hook → progress, user_turn → user, assistant_turn → assistant
        self.assertIn("progress", types)
        self.assertIn("user", types)
        self.assertIn("assistant", types)

    def test_seed_reproducibility(self):
        skel1 = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=42)
        skel2 = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=42)
        # Same uuids and timestamps
        uuids1 = [r.get("uuid") for r in skel1["records"] if "uuid" in r]
        uuids2 = [r.get("uuid") for r in skel2["records"] if "uuid" in r]
        self.assertEqual(uuids1, uuids2)

    def test_slot_manifest_collected(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        slot_ids = [s["id"] for s in skel["slot_manifest"]]
        self.assertIn("user_q", slot_ids)
        self.assertIn("asst_a", slot_ids)

    def test_slot_manifest_kinds(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        by_id = {s["id"]: s["kind"] for s in skel["slot_manifest"]}
        self.assertEqual(by_id["user_q"], "user_prompt")
        self.assertEqual(by_id["asst_a"], "text")

    def test_subagent_skeleton_present_for_subagent_event(self):
        # write delegation + subagent templates
        del_path = _write_template(self.tmp, "delegation-test", DELEGATION_TEMPLATE)
        _write_template(self.tmp, "subagent-test", SUBAGENT_TEMPLATE)
        skel = scaffolder.build_skeleton(str(del_path), self.tmp, seed=0)
        self.assertEqual(len(skel["subagent_skeletons"]), 1)
        sub = skel["subagent_skeletons"][0]
        self.assertIn("records", sub)
        self.assertIn("agent_id", sub)
        self.assertIn("output_path", sub)

    def test_output_path_format(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        parts = skel["output_path"].split("/")
        self.assertEqual(len(parts), 2)
        self.assertTrue(parts[1].endswith(".jsonl"))

    def test_skeleton_has_session_and_project(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        self.assertIsInstance(skel["session_id"], str)
        self.assertIsInstance(skel["project_slug"], str)
        self.assertTrue(len(skel["session_id"]) > 8)


# ---------------------------------------------------------------------------
# TestF2 — file_snapshot.messageId anchors the NEXT user turn
# ---------------------------------------------------------------------------


class TestF2_FileSnapshotAnchorForward(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "file-snap", FILE_SNAPSHOT_TEMPLATE)

    def test_file_snapshot_messageid_matches_next_user_uuid(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=7)
        records = skel["records"]

        # find the file-history-snapshot record
        snapshots = [r for r in records if r.get("type") == "file-history-snapshot"]
        self.assertEqual(len(snapshots), 1, "Expected exactly one snapshot")
        snap = snapshots[0]

        # find the next user record after the snapshot
        snap_idx = records.index(snap)
        user_after = next(
            (r for r in records[snap_idx + 1:] if r.get("type") == "user"),
            None,
        )
        self.assertIsNotNone(user_after, "Expected a user record after snapshot")
        self.assertEqual(
            snap["messageId"],
            user_after["uuid"],
            "F2: snapshot.messageId must equal the NEXT user record's uuid",
        )

    def test_file_snapshot_inner_messageid_also_matches(self):
        """snapshot.snapshot.messageId inner field also matches."""
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=7)
        records = skel["records"]
        snapshots = [r for r in records if r.get("type") == "file-history-snapshot"]
        snap = snapshots[0]
        snap_idx = records.index(snap)
        user_after = next(
            (r for r in records[snap_idx + 1:] if r.get("type") == "user"), None
        )
        self.assertEqual(snap["snapshot"]["messageId"], user_after["uuid"])


# ---------------------------------------------------------------------------
# TestF3 — multi tool_use FIFO pairing
# ---------------------------------------------------------------------------


class TestF3_MultiToolUseFifo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "multi-tool", MULTI_TOOL_TEMPLATE)

    def test_two_tool_use_two_tool_results_pair_in_order(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=3)
        records = skel["records"]

        # Collect tool_use ids from assistant record (in order)
        asst = next(r for r in records if r.get("type") == "assistant")
        tu_ids = [
            b["id"]
            for b in asst["message"]["content"]
            if b.get("type") == "tool_use"
        ]
        self.assertEqual(len(tu_ids), 2, "Expected 2 tool_use blocks")

        # Collect tool_result records (in order)
        tool_results = []
        for r in records:
            if r.get("type") == "user":
                content = r.get("message", {}).get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_result":
                            tool_results.append(block)
        self.assertEqual(len(tool_results), 2, "Expected 2 tool_result blocks")

        # F3: FIFO — first result pairs with first tool_use
        self.assertEqual(
            tool_results[0]["tool_use_id"], tu_ids[0],
            "F3: first tool_result must reference first tool_use (FIFO)",
        )
        self.assertEqual(
            tool_results[1]["tool_use_id"], tu_ids[1],
            "F3: second tool_result must reference second tool_use (FIFO)",
        )


# ---------------------------------------------------------------------------
# TestF4 — recompute_usage recurses into agent_progress
# ---------------------------------------------------------------------------


class TestF4_RecomputeRecursion(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        _write_template(self.tmp, "delegation-test", DELEGATION_TEMPLATE)
        _write_template(self.tmp, "subagent-test", SUBAGENT_TEMPLATE)
        self.del_path = self.tmp / "delegation-test.json"

    def test_assistant_in_agent_progress_gets_recomputed(self):
        skel = scaffolder.build_skeleton(str(self.del_path), self.tmp, seed=5)
        filled = _filled_delegation()
        out_root = self.tmp / "out"
        result = scaffolder.assemble(skel, filled, out_root)

        self.assertEqual(result["errors"], [], f"Unexpected errors: {result['errors']}")
        self.assertIsNotNone(result["output_file"])

        # Read the parent file, find agent_progress records with assistant inner
        parent_lines = result["output_file"].read_text().splitlines()
        parent_records = [json.loads(l) for l in parent_lines if l.strip()]

        progress_with_asst = [
            r for r in parent_records
            if r.get("type") == "progress"
            and r.get("data", {}).get("type") == "agent_progress"
            and r.get("data", {}).get("message", {}).get("type") == "assistant"
        ]
        self.assertGreater(len(progress_with_asst), 0, "Expected agent_progress with assistant inner")

        for prog in progress_with_asst:
            inner = prog["data"]["message"]
            usage = inner.get("message", {}).get("usage", {})
            output_tokens = usage.get("output_tokens", 0)
            self.assertGreater(
                output_tokens, 0,
                "F4: agent_progress inner assistant output_tokens must be > 0 after recompute",
            )


# ---------------------------------------------------------------------------
# TestF6 — all agent_progress wrappers share one toolUseID
# ---------------------------------------------------------------------------


class TestF6_StableToolUseId(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        _write_template(self.tmp, "delegation-test", DELEGATION_TEMPLATE)
        _write_template(self.tmp, "subagent-test", SUBAGENT_TEMPLATE)
        self.del_path = self.tmp / "delegation-test.json"

    def test_all_agent_progress_records_share_one_toolUseID(self):
        skel = scaffolder.build_skeleton(str(self.del_path), self.tmp, seed=9)
        filled = _filled_delegation()
        out_root = self.tmp / "out"
        result = scaffolder.assemble(skel, filled, out_root)
        self.assertEqual(result["errors"], [], f"Errors: {result['errors']}")

        parent_lines = result["output_file"].read_text().splitlines()
        parent_records = [json.loads(l) for l in parent_lines if l.strip()]

        progress_records = [
            r for r in parent_records
            if r.get("type") == "progress"
            and r.get("data", {}).get("type") == "agent_progress"
        ]
        self.assertGreater(len(progress_records), 1, "Need >1 agent_progress for this test")

        tool_use_ids = {r["toolUseID"] for r in progress_records}
        self.assertEqual(
            len(tool_use_ids), 1,
            f"F6: all agent_progress wrappers must share ONE toolUseID, got: {tool_use_ids}",
        )


# ---------------------------------------------------------------------------
# TestF8 — sidechain field omission
# ---------------------------------------------------------------------------


class TestF8_SidechainFieldOmission(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        _write_template(self.tmp, "delegation-test", DELEGATION_TEMPLATE)
        _write_template(self.tmp, "subagent-test", SUBAGENT_TEMPLATE)
        self.del_path = self.tmp / "delegation-test.json"

    def _get_subagent_records(self) -> list[dict]:
        skel = scaffolder.build_skeleton(str(self.del_path), self.tmp, seed=11)
        filled = _filled_delegation()
        out_root = self.tmp / "out"
        result = scaffolder.assemble(skel, filled, out_root)
        self.assertEqual(result["errors"], [], f"Errors: {result['errors']}")
        self.assertGreater(len(result["subagent_files"]), 0)
        lines = result["subagent_files"][0].read_text().splitlines()
        return [json.loads(l) for l in lines if l.strip()]

    def test_subagent_user_records_omit_promptId(self):
        sub_records = self._get_subagent_records()
        user_records = [r for r in sub_records if r.get("type") == "user"]
        self.assertGreater(len(user_records), 0)
        for r in user_records:
            self.assertNotIn(
                "promptId", r,
                f"F8: subagent user records must NOT have promptId, got: {list(r.keys())}",
            )

    def test_subagent_user_records_omit_entrypoint(self):
        sub_records = self._get_subagent_records()
        user_records = [r for r in sub_records if r.get("type") == "user"]
        self.assertGreater(len(user_records), 0)
        for r in user_records:
            self.assertNotIn(
                "entrypoint", r,
                "F8: subagent user records must NOT have entrypoint",
            )


# ---------------------------------------------------------------------------
# TestF11 — first user record has parentUuid=None after hook
# ---------------------------------------------------------------------------


class TestF11_FirstUserParentNull(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "minimal-test", MINIMAL_TEMPLATE)

    def test_first_user_after_hook_has_null_parent(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=13)
        records = skel["records"]

        user_records = [r for r in records if r.get("type") == "user"]
        self.assertGreater(len(user_records), 0)
        first_user = user_records[0]
        self.assertIsNone(
            first_user.get("parentUuid"),
            "F11: first user record must have parentUuid=None even after hook",
        )


# ---------------------------------------------------------------------------
# TestF12 — path traversal guards
# ---------------------------------------------------------------------------


class TestF12_PathTraversal(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "minimal-test", MINIMAL_TEMPLATE)

    def test_assemble_blocks_traversal_in_output_path(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        # Craft a skeleton with a traversal output_path
        evil_skel = dict(skel)
        evil_skel["output_path"] = "../../escape.jsonl"
        out_root = self.tmp / "out"
        out_root.mkdir(exist_ok=True)
        result = scaffolder.assemble(evil_skel, _filled_minimal(), out_root)
        self.assertIsNone(result["output_file"], "F12b: output_file must be None on traversal")
        self.assertTrue(len(result["errors"]) > 0, "F12b: errors must be non-empty on traversal")

    def test_mark_checkpoint_rejects_invalid_run_id(self):
        with tempfile.TemporaryDirectory() as cpdir:
            with self.assertRaises(ValueError, msg="F12a: must reject run_id with path traversal"):
                scaffolder.mark_checkpoint("../../etc/passwd", 0, 10, checkpoint_dir=cpdir)

    def test_mark_checkpoint_rejects_slash_in_run_id(self):
        with tempfile.TemporaryDirectory() as cpdir:
            with self.assertRaises(ValueError):
                scaffolder.mark_checkpoint("foo/bar", 1, 5, checkpoint_dir=cpdir)

    def test_subagent_template_name_must_be_kebab(self):
        evil_template = dict(DELEGATION_TEMPLATE)
        evil_events = list(evil_template["events"])
        evil_events[2] = {"kind": "subagent", "template": "../bad"}
        evil_template = dict(evil_template, events=evil_events)
        evil_path = _write_template(self.tmp, "evil-delegation", evil_template)
        with self.assertRaises(ValueError, msg="F12c: must reject non-kebab template names"):
            scaffolder.build_skeleton(str(evil_path), self.tmp, seed=0)


# ---------------------------------------------------------------------------
# TestF13 — atomic checkpoint writes + corrupt-file recovery
# ---------------------------------------------------------------------------


class TestF13_AtomicCheckpoint(unittest.TestCase):
    def test_corrupt_checkpoint_resets_to_empty(self):
        with tempfile.TemporaryDirectory() as cpdir:
            # write invalid JSON
            p = Path(cpdir) / "my-run.json"
            p.write_text("{not valid json{{}")
            result = scaffolder.load_checkpoint("my-run", checkpoint_dir=cpdir)
            self.assertEqual(result, {"completed": [], "remaining": None})

    def test_missing_checkpoint_returns_empty(self):
        with tempfile.TemporaryDirectory() as cpdir:
            result = scaffolder.load_checkpoint("nonexistent-run", checkpoint_dir=cpdir)
            self.assertEqual(result, {"completed": [], "remaining": None})

    def test_mark_then_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as cpdir:
            scaffolder.mark_checkpoint("test-run-1", 0, 5, checkpoint_dir=cpdir)
            scaffolder.mark_checkpoint("test-run-1", 1, 5, checkpoint_dir=cpdir)
            result = scaffolder.load_checkpoint("test-run-1", checkpoint_dir=cpdir)
            self.assertIn(0, result["completed"])
            self.assertIn(1, result["completed"])

    def test_atomic_write_no_tmp_left_behind(self):
        with tempfile.TemporaryDirectory() as cpdir:
            scaffolder.mark_checkpoint("clean-run", 0, 3, checkpoint_dir=cpdir)
            tmp_files = list(Path(cpdir).glob("*.tmp"))
            self.assertEqual(tmp_files, [], "No .tmp files should remain after atomic write")


# ---------------------------------------------------------------------------
# TestAssemble
# ---------------------------------------------------------------------------


class TestAssemble(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "minimal-test", MINIMAL_TEMPLATE)

    def test_substitutes_slots_into_records(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        out_root = self.tmp / "out"
        result = scaffolder.assemble(skel, _filled_minimal(), out_root)
        self.assertEqual(result["errors"], [])
        content = result["output_file"].read_text()
        self.assertIn("Hello world", content)
        self.assertIn("Hi there!", content)

    def test_validation_failure_blocks_write(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        out_root = self.tmp / "out"
        # Pass empty filled_slots — slots remain as {_slot: ...} markers
        result = scaffolder.assemble(skel, {}, out_root)
        self.assertIsNone(result["output_file"], "Unfilled slots must block write")
        self.assertTrue(len(result["errors"]) > 0)

    def test_writes_clean_jsonl_when_valid(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        out_root = self.tmp / "out"
        result = scaffolder.assemble(skel, _filled_minimal(), out_root)
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["output_file"].exists())
        lines = [l for l in result["output_file"].read_text().splitlines() if l.strip()]
        # Every line must be valid JSON
        for line in lines:
            json.loads(line)  # raises if invalid

    def test_writes_subagent_sibling_files(self):
        _write_template(self.tmp, "delegation-test", DELEGATION_TEMPLATE)
        _write_template(self.tmp, "subagent-test", SUBAGENT_TEMPLATE)
        del_path = self.tmp / "delegation-test.json"
        skel = scaffolder.build_skeleton(str(del_path), self.tmp, seed=0)
        out_root = self.tmp / "out"
        result = scaffolder.assemble(skel, _filled_delegation(), out_root)
        self.assertEqual(result["errors"], [], f"Errors: {result['errors']}")
        self.assertGreater(len(result["subagent_files"]), 0)
        for sf in result["subagent_files"]:
            self.assertTrue(sf.exists(), f"Subagent file missing: {sf}")

    def test_output_file_is_within_out_root(self):
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        out_root = self.tmp / "out"
        result = scaffolder.assemble(skel, _filled_minimal(), out_root)
        self.assertEqual(result["errors"], [])
        resolved = result["output_file"].resolve()
        self.assertTrue(str(resolved).startswith(str(out_root.resolve())))


# ---------------------------------------------------------------------------
# TestCli
# ---------------------------------------------------------------------------


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "minimal-test", MINIMAL_TEMPLATE)

    def _capture_stdout(self, argv: list[str]) -> tuple[int, str]:
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            rc = scaffolder._main(argv)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout = old_stdout
        return rc, out

    def test_cli_skeleton_subcommand(self):
        rc, out = self._capture_stdout([
            "scaffolder.py", "skeleton",
            str(self.tpl_path),
            "--template-dir", str(self.tmp),
            "--seed", "0",
        ])
        self.assertEqual(rc, 0)
        parsed = json.loads(out)
        self.assertIn("records", parsed)
        self.assertIn("slot_manifest", parsed)

    def test_cli_assemble_subcommand(self):
        # First build skeleton, save it
        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        skel_path = self.tmp / "skel.json"
        skel_path.write_text(json.dumps(skel))
        slots_path = self.tmp / "slots.json"
        slots_path.write_text(json.dumps(_filled_minimal()))
        out_root = self.tmp / "out"
        out_root.mkdir()

        rc, out = self._capture_stdout([
            "scaffolder.py", "assemble",
            str(skel_path),
            str(slots_path),
            str(out_root),
        ])
        self.assertEqual(rc, 0)
        parsed = json.loads(out)
        self.assertIn("output_file", parsed)
        self.assertEqual(parsed["errors"], [])

    def test_cli_checkpoint_mark_then_load(self):
        cpdir = self.tmp / "checkpoints"
        cpdir.mkdir()
        rc1, _ = self._capture_stdout([
            "scaffolder.py", "checkpoint-mark",
            "my-session", "3", "10",
            "--checkpoint-dir", str(cpdir),
        ])
        self.assertEqual(rc1, 0)

        rc2, out = self._capture_stdout([
            "scaffolder.py", "checkpoint-load",
            "my-session",
            "--checkpoint-dir", str(cpdir),
        ])
        self.assertEqual(rc2, 0)
        parsed = json.loads(out)
        self.assertIn(3, parsed["completed"])

    def test_cli_unknown_subcommand_exits_nonzero(self):
        # argparse may call sys.exit() for invalid choices — catch SystemExit
        try:
            rc, _ = self._capture_stdout(["scaffolder.py", "bogus-command"])
            self.assertNotEqual(rc, 0)
        except SystemExit as exc:
            self.assertNotEqual(exc.code, 0)


# ---------------------------------------------------------------------------
# TestT3 — golden snapshot (hash-based stability)
# ---------------------------------------------------------------------------


class TestT3_GoldenSnapshot(unittest.TestCase):
    """Structural stability test.

    records.new_uuid() uses random.getrandbits (seeded) so UUIDs are stable.
    Other IDs (requestId, toolUseId, etc.) use secrets._b62 which bypasses
    random.seed(), so full byte-for-byte reproducibility is not possible.
    We verify the seeded parts (uuids, timestamps, structure) are stable.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "minimal-test", MINIMAL_TEMPLATE)

    def test_fixed_seed_template_filling_produces_stable_output(self):
        skel1 = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=99)
        skel2 = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=99)

        # UUIDs are seeded and must match
        uuids1 = [r.get("uuid") for r in skel1["records"] if "uuid" in r]
        uuids2 = [r.get("uuid") for r in skel2["records"] if "uuid" in r]
        self.assertEqual(uuids1, uuids2, "Same seed must produce identical UUIDs")

        # Timestamps are seeded and must match
        ts1 = [r.get("timestamp") for r in skel1["records"] if "timestamp" in r]
        ts2 = [r.get("timestamp") for r in skel2["records"] if "timestamp" in r]
        self.assertEqual(ts1, ts2, "Same seed must produce identical timestamps")

        # Record types must match
        types1 = [r.get("type") for r in skel1["records"]]
        types2 = [r.get("type") for r in skel2["records"]]
        self.assertEqual(types1, types2, "Same seed must produce identical record types")

        # Both must assemble cleanly
        filled = _filled_minimal()
        out_root1 = self.tmp / "out1"
        out_root2 = self.tmp / "out2"
        result1 = scaffolder.assemble(skel1, filled, out_root1)
        result2 = scaffolder.assemble(skel2, filled, out_root2)
        self.assertEqual(result1["errors"], [])
        self.assertEqual(result2["errors"], [])


# ---------------------------------------------------------------------------
# TestT5 — real file shape (light)
# ---------------------------------------------------------------------------


class TestT5_RealFileShape(unittest.TestCase):
    REAL_SESSION_PATH = Path(
        "/Users/azasorin/.claude/projects/"
        "-Users-azasorin--local-share-chezmoi/"
        "0d51e052-d5a5-4281-9838-25ef0211629b.jsonl"
    )

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "minimal-test", MINIMAL_TEMPLATE)

    def test_generated_record_keys_overlap_with_real_record_keys(self):
        if not self.REAL_SESSION_PATH.exists():
            self.skipTest("Real session file not available on this machine")

        real_records = [
            json.loads(l)
            for l in self.REAL_SESSION_PATH.read_text().splitlines()
            if l.strip()
        ]
        real_by_type: dict[str, set] = {}
        for r in real_records:
            t = r.get("type", "unknown")
            real_by_type.setdefault(t, set()).update(r.keys())

        skel = scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=0)
        filled = _filled_minimal()
        out_root = self.tmp / "out"
        result = scaffolder.assemble(skel, filled, out_root)
        self.assertEqual(result["errors"], [])

        mock_records = [
            json.loads(l)
            for l in result["output_file"].read_text().splitlines()
            if l.strip()
        ]
        # For each mock record, its keys must be a subset of real keys for that type
        # (known extras allowed: none required here)
        for mock_rec in mock_records:
            t = mock_rec.get("type", "unknown")
            if t in real_by_type:
                extra = set(mock_rec.keys()) - real_by_type[t]
                self.assertEqual(
                    extra, set(),
                    f"Mock {t} record has extra keys not in real data: {extra}",
                )


# ---------------------------------------------------------------------------
# TestT6 — test isolation (uuid v4 stays valid across seeded runs)
# ---------------------------------------------------------------------------


class TestT6_TestIsolation(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tpl_path = _write_template(self.tmp, "minimal-test", MINIMAL_TEMPLATE)

    def test_uuid_v4_format_holds_across_back_to_back_skeletons(self):
        import records as rec_mod  # type: ignore[import-not-found]
        import re

        UUID_V4_RE = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )

        scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=1)
        scaffolder.build_skeleton(str(self.tpl_path), self.tmp, seed=2)

        # After seeded runs, new_uuid() must still produce valid v4
        for _ in range(20):
            u = rec_mod.new_uuid()
            self.assertRegex(u, UUID_V4_RE, f"new_uuid() produced invalid v4: {u!r}")


if __name__ == "__main__":
    unittest.main()
