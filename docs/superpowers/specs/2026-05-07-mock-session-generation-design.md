# Mock Claude Session Generation — Design

## Context

Goal: train a local content-aware model on Claude Code session structure. We need plausible mock `.jsonl` files in volume — files that are structurally identical to real sessions at the per-record `set(keys())` level, with coherent content across tool invocations and assistant responses.

Two skills implement this:

1. **`extract-session-templates`** — analyzes the real session archive at `~/.claude/projects/`, produces archetype templates + a weighted distribution at `~/.claude/data/session-templates/`. Run once per machine or once per major archive growth event.

2. **`generate-mock-sessions`** — per-run generator. Consumes templates. Emits mock `.jsonl` files. Claude fills the content; Python handles structure.

---

## Architecture

**Helper-script + content-slots split:**
- Python (`records.py`, `scaffolder.py`, `validate.py`) handles structural correctness — UUIDs, timestamps, parent chains, schema-compliant envelopes.
- Claude (the agent) handles content — user prompts, assistant text, tool inputs, tool outputs, subagent prompts. Single-pass slot filling per file for intra-file coherence.

**Pipeline:**

```
~/.claude/projects/**/*.jsonl
        │
        ▼
   featurize.py (extract-session-templates)
        │
        ▼
   features.csv
        │
        ▼  (cluster + user review + distill)
        ▼
~/.claude/data/session-templates/
   ├ distribution.json
   ├ <archetype-1>.json
   ├ <archetype-2>.json
   └ ...
        │
        ▼
   scaffolder.py skeleton (per file)
        │
        ▼
   skeleton.json (records with {_slot} markers)
        │
        ▼
   Claude fills slots → filled-slots.json
        │
        ▼
   scaffolder.py assemble
        │
        ▼
<out>/<slug>/<sessionId>.jsonl
<out>/<slug>/<sessionId>/subagents/agent-<id>.jsonl
```

---

## Key correctness invariants enforced

**`records.py` / `scaffolder.py` are responsible for:**
- UUID v4 format (uses `uuid.UUID(int=random.getrandbits(128), version=4)` — not `uuid.uuid4()`, which would bypass seeding)
- Monotonically increasing timestamps within a file via `TimestampSequence`
- Tool-use/tool-result FIFO pairing: tool_use IDs are queued in order and popped by subsequent tool_result events (F3)
- `file-history-snapshot.messageId` anchors to the **next** user record's UUID via two-pass pre-allocation (F2)
- `agent_progress.data.message` is a stripped projection of the subagent record — only `{type, uuid, timestamp, message?, data?, requestId?}`, no envelope fields (F5)
- Single stable `toolUseID` (agent_msg_011…) shared across all agent_progress wrappers for one delegation (F6)
- Subagent records omit parent-only fields (`entrypoint`, `promptId`, `permissionMode`) via `is_sidechain` flag (F8)
- `is_error: true` emitted only when True; absent on success (F9)
- `stop_details: null` always present on assistant message records (R3)

**`validate.py` checks:**
- UUID v4 format strictly enforced
- UUID chain continuity within a file
- Strictly non-decreasing timestamps
- No `{_slot: ...}` markers in assembled output
- `tool_use` / `tool_result` count balance
- `file-history-snapshot.messageId` references a user record that follows it
- No sidechain-prohibited fields on subagent user records

---

## Out of scope

- **Token count accuracy.** `output_tokens` is recomputed as `chars/4`. Real prediction requires a tokenizer and is not needed for structural training data.
- **Image/audio attachments.** Some real sessions contain image data (visual session resumes); mock generation omits these.
- **Session compaction events.** The compaction record type is not observed in the current archive and is not implemented.
- **Parallel assembly.** The assemble step is single-threaded by design. Resumption via checkpointing handles large batch runs.

---

## Status

Rebuild complete (2026-05-07). Branch `feat/rebuild-skills`. 189 tests passing total (77 extract-session-templates + 112 generate-mock-sessions).
