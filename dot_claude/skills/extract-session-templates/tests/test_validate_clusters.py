"""
Tests for validate_clusters.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import validate_clusters  # type: ignore[import-not-found]


def _write_json(data: object) -> Path:
    """Write data to a temp file and return its Path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(data, tmp)
    tmp.flush()
    tmp.close()
    return Path(tmp.name)


class TestValidateClusters(unittest.TestCase):
    def _valid_data(self) -> dict:
        return {
            "main_archetypes": [
                {
                    "name": "typescript-bug-fix",
                    "description": "Sessions fixing TypeScript bugs",
                    "member_files": ["proj/a.jsonl", "proj/b.jsonl"],
                    "representative_files": ["proj/a.jsonl"],
                }
            ],
            "subagent_archetypes": [
                {
                    "name": "explore-codebase",
                    "description": "Subagent sessions exploring codebase",
                    "member_files": ["proj/sub/agent-x.jsonl"],
                    "representative_files": ["proj/sub/agent-x.jsonl"],
                }
            ],
        }

    def test_valid_passes(self):
        path = _write_json(self._valid_data())
        errors = validate_clusters.validate(path)
        self.assertEqual(errors, [])

    def test_missing_top_key_main(self):
        data = self._valid_data()
        del data["main_archetypes"]
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertTrue(any("main_archetypes" in e for e in errors))

    def test_missing_top_key_subagent(self):
        data = self._valid_data()
        del data["subagent_archetypes"]
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertTrue(any("subagent_archetypes" in e for e in errors))

    def test_archetype_missing_field(self):
        data = self._valid_data()
        del data["main_archetypes"][0]["description"]
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertTrue(any("description" in e for e in errors))

    def test_duplicate_names_across_lists(self):
        data = self._valid_data()
        data["subagent_archetypes"][0]["name"] = "typescript-bug-fix"
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertTrue(any("Duplicate" in e and "typescript-bug-fix" in e for e in errors))

    def test_representative_not_in_members(self):
        data = self._valid_data()
        data["main_archetypes"][0]["representative_files"] = ["proj/NOT-IN-MEMBERS.jsonl"]
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertTrue(
            any("representative_file" in e and "NOT-IN-MEMBERS" in e for e in errors)
        )

    def test_name_not_kebab_case(self):
        data = self._valid_data()
        data["main_archetypes"][0]["name"] = "TypeScript_Bug_Fix"
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertTrue(any("kebab" in e.lower() or "kebab-case" in e for e in errors))

    def test_null_main_archetypes(self):
        data = self._valid_data()
        data["main_archetypes"] = None
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertTrue(any("NoneType" in e or "null" in e.lower() for e in errors))

    def test_name_wrong_type(self):
        data = self._valid_data()
        data["main_archetypes"][0]["name"] = 42
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertTrue(any("int" in e for e in errors))

    def test_member_files_wrong_type(self):
        data = self._valid_data()
        data["main_archetypes"][0]["member_files"] = "not-a-list"
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertTrue(any("member_files" in e and ("list" in e or "str" in e) for e in errors))

    def test_collects_all_errors(self):
        """Multiple errors should all be reported, not fail-fast."""
        data = {
            "main_archetypes": [
                {
                    "name": "Bad Name!",  # not kebab-case
                    "description": "ok",
                    "member_files": ["a.jsonl"],
                    "representative_files": ["MISSING.jsonl"],  # not in members
                }
            ],
            "subagent_archetypes": [],
        }
        path = _write_json(data)
        errors = validate_clusters.validate(path)
        self.assertGreaterEqual(len(errors), 2)


class TestValidateClustersMain(unittest.TestCase):
    def test_main_valid_returns_zero(self):
        data = {
            "main_archetypes": [
                {
                    "name": "jira-triage",
                    "description": "Jira triage sessions",
                    "member_files": ["p/a.jsonl"],
                    "representative_files": ["p/a.jsonl"],
                }
            ],
            "subagent_archetypes": [],
        }
        path = _write_json(data)
        result = validate_clusters._main(["prog", str(path)])
        self.assertEqual(result, 0)

    def test_main_invalid_returns_one(self):
        data = {"main_archetypes": [], "subagent_archetypes": [{"name": "Bad Name"}]}
        path = _write_json(data)
        result = validate_clusters._main(["prog", str(path)])
        self.assertEqual(result, 1)

    def test_main_usage_error_returns_two(self):
        result = validate_clusters._main(["prog"])
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
