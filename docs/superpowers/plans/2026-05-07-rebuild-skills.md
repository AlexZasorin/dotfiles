# Rebuild: extract-session-templates + generate-mock-sessions skills

## Context

The user lost two in-progress Claude Code skills when moving laptops. The work was on local-only feature branches that were never pushed to GitHub. State on the new laptop:

**Preserved:**
- Chezmoi dotfiles repo at `/Users/azasorin/.local/share/chezmoi/` (synced from `github.com:AlexZasorin/dotfiles.git`).
- Real Claude session files at `~/.claude/projects/**/*.jsonl` (621 files — up from 415 originally).
- Two existing skills at `dot_claude/skills/{github-code-search,reflecting-on-workflow}/` that serve as the structural pattern.

**Lost:**
- `dot_claude/skills/extract-session-templates/` (entire skill).
- `dot_claude/skills/generate-mock-sessions/` (entire skill).
- `docs/superpowers/{specs,plans}/` (design doc + 2 implementation plans).
- Local-only feature branches `feat/extract-session-templates`, `feat/generate-mock-sessions` — both deleted with the prior laptop.
- `/tmp/mock-run-demo/` and `/tmp/templates-test/` demo outputs.

**Goal:** Rebuild both skills end-to-end. The previous build went through 4 rounds of independent code review (1 Sonnet + 3 Opus, ~30+ findings catalogued). This rebuild **incorporates all critical/important fixes upfront** instead of repeating the v1-then-patch cycle.

## Approach

**Single rebuild pass with fixes baked in.** The architecture, event grammar, and CLI surface are unchanged from the lost v1 (those decisions were sound). What changes is that ~25 known bugs and realism gaps are corrected during the initial build, not as follow-ups.

## High-level architecture

Two skills sharing a runtime data directory at `~/.claude/data/session-templates/`:

```
dot_claude/skills/
  extract-session-templates/      # Skill 1: bootstrap (template library)
    SKILL.md, README.md
    featurize.py                  # Walks real jsonl, emits CSV of structural features
    validate_clusters.py          # clusters.json validator
    validate_template.py          # template JSON validator (event grammar)
    tests/
      __init__.py
      fixtures.py
      test_featurize.py
      test_validate_clusters.py
      test_validate_template.py

  generate-mock-sessions/         # Skill 2: per-run mock generator
    SKILL.md, README.md, schema.md
    records.py                    # Pure record builders (record-shape realism)
    scaffolder.py                 # CLI + skeleton/assemble/checkpoint orchestration
    validate.py                   # Structural validator with null + pairing checks
    tests/
      __init__.py
      fixtures.py
      test_records.py
      test_scaffolder.py
      test_validate.py
```

Pipeline flow:
1. `extract-session-templates` analyzes real sessions at `~/.claude/projects/`, produces archetype templates + distribution at `~/.claude/data/session-templates/`.
2. `generate-mock-sessions` consumes those templates: scaffolder builds a skeleton with structural fields filled and content-slot markers; Claude (the agent) fills the slots in one pass; scaffolder substitutes, validates, writes the final `.jsonl`. Per-file checkpointing for resumable runs.

## Critical fixes baked into v1 rebuild

Numbered per the convergent code-review findings catalogued in the prior session's reports.

**Correctness bugs:**
- F1. **UUID v4 format**: monkey-patch must set version/variant nibbles. Use `_uuid.UUID(int=random.getrandbits(128), version=4)` instead of raw `bytes(...)` constructor.
- F2. **`file-history-snapshot.messageId`** anchors the *next* user record (forward), not the prior one. Implement two-pass: pre-allocate user-turn UUIDs, look ahead from snapshot events.
- F3. **Multi-tool-use ID pairing**: track tool-use ids in a FIFO queue (`state["pending_tool_use_ids"]: list[str]`); each `tool_result` pops oldest. Single `last_tool_use_id` was wrong when assistant emitted ≥2 tool_uses.
- F4. **Parent vs subagent-file `output_tokens` divergence**: `_recompute_usage` must recurse into `agent_progress.data.message` so the parent's mirror gets the same recompute as the standalone subagent record.
- F5. **`agent_progress.data.message` envelope strip**: project inner record to `{type, message, uuid, timestamp, requestId?}` only. Real files do not embed `parentUuid`/`isSidechain`/`cwd`/`sessionId`/`version`/`gitBranch`/`agentId` inside `data.message`.
- F6. **`agent_progress.toolUseID` constant per delegation**: derive once from parent assistant `message.id` (or one fresh `agent_msg_*` per delegation), share across all wrappers for that delegation.
- F7. **`build_hook` event-driven command/hookName**: don't hardcode `:startup` / `session-start`. Derive from `event` (e.g., `PostToolUse:post-tool-use`).
- F8. **Subagent record fields**: omit `entrypoint`, `promptId`, `permissionMode` from sidechain records — they're parent-file-only fields.
- F9. **`build_tool_result` cleanup**: do NOT add `permissionMode`; do NOT regenerate `promptId` (reuse the round's promptId so all turn-related records share it); make `is_error` opt-in (omit on success); add `toolUseResult` field.
- F10. **`system_turn_duration` parentUuid**: don't emit `parentUuid: ""`; use `None` and update validator to treat them as equivalent.
- F11. **First user record `parentUuid: null`** even after a `SessionStart` hook. Hook is its own root.

**Security:**
- F12. **Path traversal** at three sinks: `mark_checkpoint` (run_id), `assemble` (output_path), `_expand_subagent_event` (template name). Validate names match `[a-z0-9-]+` and assert resolved paths stay inside the configured root.
- F13. **Atomic checkpoint writes**: write to `<path>.tmp` then `os.replace`; wrap `load_checkpoint` parse in try/except so a corrupt file resets to clean state instead of crashing.

**Validator hardening:**
- V1. Reject null `uuid`/`timestamp`/`parentUuid`-key-missing instead of silently accepting.
- V2. Add `queue-operation` to flat-meta types; rename set to clarify "records without uuid/timestamp at top level".
- V3. Cross-reference check: every `tool_result.tool_use_id` must match a prior assistant `tool_use.id`; every `sourceToolAssistantUUID` must match a prior assistant uuid.
- V4. Snapshot anchor check: `file-history-snapshot.messageId` must match a user-record uuid in the file (after F2 is fixed, this becomes enforceable).
- V5. Allow nested `progress` records to be handled (after F5/F6 the inner `message.type` may be `assistant`/`user`/`progress` for nested cases).

**Schema realism (so generated files aren't trivially distinguishable from real):**
- R1. Add `slug` (e.g., adjective-adjective-noun, one per session) to every record carrying the session envelope.
- R2. Thinking `signature`: emit ~380-char base64-ish placeholder (not empty string).
- R3. Full `usage` shape on assistant messages: `input_tokens` (sampled non-zero), `cache_creation` nested object, `inference_geo: ""`, `service_tier`, plus `stop_details: null` on the message.
- R4. Anthropic ID format: base62 with `01` prefix (e.g., `req_011CZAv5b...`), not lowercase hex.
- R5. Sample `version` (e.g., from `["2.1.83","2.1.91","2.1.92","2.1.110","2.1.112"]`) and `git_branch` (`main` for chezmoi, `trunk` for Repos) per session, not hardcoded.
- R6. Sample agent_id length: 60% 17-char + 40% 7-char to match real distribution.

**Code quality:**
- C1. `_substitute_slots` and `validate._walk_for_slots` should share a single `is_slot_marker(value)` helper (currently duplicated).
- C2. Remove dead code: `seed` parameter on `_expand_subagent_event`, `missing` list in `assemble`, unreferenced helpers.
- C3. Either implement `optional_branch` event field (probabilistic skip) or remove it from spec/SKILL.md.
- C4. Either implement `length_distribution` sampling (vary record count per session) or document that templates emit a fixed pattern.
- C5. Mid-file imports → top of file (PEP 8).

**Testing:**
- T1. **Real-file roundtrip test**: pick a real `.jsonl`, run `validate.validate_jsonl_file` on it, expect 0 errors. Add this for both parent and subagent shapes.
- T2. **Schema-equivalence test**: generate a mock file, compare `set(record.keys())` per record-type against a real file of the same shape; allow only documented/intentional differences.
- T3. **Golden-file snapshot tests**: for fixed `(template, seed, slots)` triples, snapshot the resulting `.jsonl` and assert byte-equality on subsequent runs.
- T4. **Multi-tool-use pairing test**: 2+ tool_use blocks → 2+ tool_results referencing them in order.
- T5. **Parent/subagent recompute equality test**: assert `agent_progress.data.message.usage` matches the same field in the subagent file.
- T6. **Tests do not depend on global UUID monkey-patch state** — use `setUp` save/restore around tests that need a clean `uuid.uuid4`.

## Build phases

Each phase ends with all tests passing and a commit. Work happens in a worktree at `.worktrees/rebuild-skills/` on branch `feat/rebuild-skills`.

### Phase 0 — Setup (≈10 min)
- Create worktree, gitignore `.worktrees/` and `__pycache__/`.
- Scaffold both skill directory trees (empty SKILL.md/README.md/schema.md stubs).
- Create `docs/superpowers/specs/` dir for the design doc reproduction.
- **Commit and push immediately** — never lose this work again.

### Phase 1 — extract-session-templates (≈3–4 hours)
TDD throughout. Order:
1. `tests/fixtures.py` — sample jsonl record dicts covering all real record types observed in `~/.claude/projects/`.
2. `featurize.py` — record parsing → feature extraction (tool sequence, length, duration, model mix, plan-mode flag, topic fingerprint, subagent delegation count using `Agent` not `Task`) → CSV writer + CLI.
3. `validate_clusters.py` — clusters.json schema validator.
4. `validate_template.py` — template JSON validator with **expanded event-kind allowlist** (`permission_mode`, `system_turn_duration` plus all originals).
5. SKILL.md prose for the four pipeline steps (featurize → cluster → user review → distill).
6. README.md.
7. End-to-end smoke against `~/.claude/projects` (621 files).
8. **Commit + push.**

### Phase 2 — generate-mock-sessions records.py (≈2 hours)
TDD. Order:
1. `tests/fixtures.py` — synthetic templates (minimal, delegation, subagent-target).
2. `records.py` utilities — `new_uuid` (with **F1 v4 fix**), `new_request_id`/`new_message_id`/`new_tool_use_id`/`new_agent_id` using **R4 base62**, `TimestampSequence`, `weighted_choice`, `sample_length`, `sample_slug` (**R1**).
3. `records.py` builders — `build_hook` (**F7 event-driven**), `build_file_snapshot`, `build_user_turn`, `build_tool_result` (**F9 cleanup**), `build_assistant_turn` (**R2 signature**, **R3 usage shape, stop_details**), `build_agent_progress` (**F5 envelope strip**), `build_permission_mode`, `build_system_turn_duration` (**F10 None parent**), `build_attachment`, `build_last_prompt` (the latter two new — close real-file gaps).
4. `SessionContext` carries `slug`, `version` (**R5 sampled**), `git_branch` (**R5 sampled**), `agent_id`, plus a `is_sidechain` flag (**F8** controls field omission).
5. **Commit + push.**

### Phase 3 — generate-mock-sessions validate.py (≈1 hour)
TDD. Order:
1. `_FLAT_META_TYPES = frozenset({"file-history-snapshot","permission-mode","last-prompt","custom-title","agent-name","queue-operation"})` (**V2**).
2. `validate(records)` with **V1** null-key handling, **V3** tool_use/tool_result pairing, **V4** snapshot anchor check, **V5** nested-progress traversal.
3. `validate_jsonl_file(path)` convenience.
4. Tests: **T1 real-file roundtrip** against 5 sampled real files (must pass with 0 errors).
5. **Commit + push.**

### Phase 4 — generate-mock-sessions scaffolder.py (≈3 hours)
TDD. Order:
1. `_DEFAULT_PROJECTS` as `(slug, cwd, branch)` tuples (**R5**) sampled from `_sample_session_context`.
2. `_emit_event` dispatcher with state dict tracking `pending_tool_use_ids` queue (**F3**), `last_user_uuid` (forward look-ahead per **F2**), `current_promptId` (turn-stable per **F9**).
3. `build_skeleton` — two-pass: pre-allocate user-turn UUIDs, then emit. Apply **F11** for first user parent. Hook + permission_mode handled per **F11**/F10.
4. `_expand_subagent_event` with **F6** stable-toolUseID, nested-recursion handling. Reject typo'd template names with `ValueError` (**F12**).
5. `assemble` — `_substitute_slots` (with **C1** shared helper), `_recompute_usage` recursing into `agent_progress` (**F4**), validate, **F12** path-traversal check on `output_path`, atomic write.
6. `load_checkpoint`/`mark_checkpoint` with **F13** atomic writes + corrupt-file recovery.
7. CLI: argparse with `skeleton`, `assemble`, `checkpoint-mark`, `checkpoint-load` subcommands.
8. Tests: **T3 golden snapshots**, **T4 multi-tool-use pairing**, **T5 parent/subagent recompute equality**, **T6 monkey-patch isolation**.
9. **Commit + push.**

### Phase 5 — Documentation (≈1 hour)
1. `schema.md` for generate-mock-sessions — full real-file record-shape reference (every record type with all observed fields documented).
2. `SKILL.md` per-file loop instructions for Claude — covers permission_mode + system_turn_duration event kinds, slot manifest, retry on validation failure.
3. `README.md` — invocation, supported events, known limitations (with the rebuild's smaller list since most prior limitations are fixed).
4. Reproduce `docs/superpowers/specs/2026-04-21-mock-session-generation-design.md` (the design spec, simplified).
5. **Commit + push.**

### Phase 6 — End-to-end verification (≈1 hour)
1. Run extract-session-templates skill against `~/.claude/projects` to produce template library.
2. Generate one mock session per archetype using generate-mock-sessions.
3. Run validate.py against each generated `.jsonl` — must pass.
4. Run validate.py against 10 random real `.jsonl` files — must also pass (with **V2** queue-operation fix).
5. Diff `set(keys())` between generated and real records of each type — assert minimal/documented differences.
6. `chezmoi apply` to install both skills under `~/.claude/skills/`.
7. Verify the user can `/extract-session-templates` and `/generate-mock-sessions` commands work.
8. **Final push.**

## Critical files to be modified

- `dot_claude/skills/extract-session-templates/{SKILL.md,README.md,featurize.py,validate_clusters.py,validate_template.py,tests/*}`
- `dot_claude/skills/generate-mock-sessions/{SKILL.md,README.md,schema.md,records.py,scaffolder.py,validate.py,tests/*}`
- `docs/superpowers/specs/2026-04-21-mock-session-generation-design.md` (recreated)
- `.gitignore` — add `.worktrees/` and `__pycache__/` if not already present

## References / patterns to reuse

- `dot_claude/skills/github-code-search/` and `dot_claude/skills/reflecting-on-workflow/` — existing skill directory layout, SKILL.md frontmatter format, plugin convention.
- `~/.claude/projects/**/*.jsonl` — 621 real session files, primary source of schema truth and featurization input.
- Stdlib-only Python constraint (no pip dependencies) — same as before.
- Python 3.10+ syntax (matches the user's environment).

## Verification

After Phase 6 the rebuild is complete when:

1. **Both test suites pass:**
   ```bash
   cd dot_claude/skills/extract-session-templates && python3 -m unittest discover tests -v
   cd dot_claude/skills/generate-mock-sessions && python3 -m unittest discover tests -v
   ```
   Expected: ~70+ tests across the two skills, 0 failures.

2. **Featurize runs against real data:**
   ```bash
   python3 dot_claude/skills/extract-session-templates/featurize.py ~/.claude/projects /tmp/features.csv
   wc -l /tmp/features.csv   # ≈ 622 (621 files + header)
   ```

3. **Mock generation works end-to-end** with a sample template; resulting `.jsonl` validates clean and is structurally indistinguishable from a real file at the per-record `set(keys())` level (modulo documented gaps).

4. **Validator passes on real files:** `validate.validate_jsonl_file` on 10 random real sessions must return `[]` for every file (no false positives from `queue-operation` or other flat-meta records).

5. **`chezmoi apply` installs cleanly** and both `/extract-session-templates` and `/generate-mock-sessions` skills are available.

6. **Branch pushed to GitHub** — never lose this work again. `git push -u origin feat/rebuild-skills`.
