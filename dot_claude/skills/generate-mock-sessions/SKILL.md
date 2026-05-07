---
name: generate-mock-sessions
description: Per-run generator that fabricates plausible Claude Code session .jsonl files for training a local content-aware model. Consumes the archetype template library produced by extract-session-templates.
---

# generate-mock-sessions

Per-run generator. Each invocation produces N coherent mock session `.jsonl` files matching the archetype distribution at `~/.claude/data/session-templates/`. Pipeline: pick archetype → run scaffolder skeleton → fill slots coherently → run scaffolder assemble → checkpoint.

---

## Inputs

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `count` | int | `5` | Number of session files to generate |
| `out` | path | `./mock-data` | Output root directory |
| `template-dir` | path | `~/.claude/data/session-templates` | Directory containing archetype templates and `distribution.json` |
| `archetype` | string | — | Pin all files to one archetype (optional) |
| `run-id` | string | auto | Identifier for checkpoint resumption (alphanumeric, hyphens, underscores) |

If `run-id` is not supplied, generate one (e.g. the current date + a short random suffix).

---

## Per-file loop

Repeat steps 1–7 for each index `i` in `range(count)`.

### Step 1 — Read checkpoint

```bash
python3 <skill-dir>/scaffolder.py checkpoint-load <run-id>
```

Returns `{"completed": [int, ...], "remaining": int}`. If `i` is in `completed`, skip to the next index.

### Step 2 — Pick template

Read `<template-dir>/distribution.json`. Sample one archetype name weighted by the distribution, or use the `archetype` argument if supplied.

### Step 3 — Generate skeleton

```bash
python3 <skill-dir>/scaffolder.py skeleton \
    <template-dir>/<archetype>.json \
    --template-dir <template-dir> \
    --seed <int> > /tmp/skeleton-<run-id>-<i>.json
```

Use `i` (or a derived int) as the seed for reproducibility. The returned JSON contains:

```json
{
  "records": [...],
  "slot_manifest": [{"id": "slot_id", "kind": "user_prompt|text|thinking|tool_input|tool_result", "context": ""}],
  "session_id": "uuid",
  "project_slug": "-Users-...",
  "output_path": "<slug>/<session_id>.jsonl",
  "subagent_skeletons": [...]
}
```

### Step 4 — Fill slots in one pass

Read the `slot_manifest`. For every slot, write coherent content into a `filled-slots.json`:

```json
{
  "user_q_1": "How do I configure the retry policy in the assignment service?",
  "asst_text_1": "Let me look at the retry configuration...",
  "bash_input_1": {"command": "grep -r 'retry' apps/server/src --include='*.ts'", "description": "Search for retry configuration"},
  "bash_result_1": "apps/server/src/config/retry.ts:  retryCount: 3,\napps/server/src/config/retry.ts:  retryDelay: 1000"
}
```

**Coherence guidance**:
- Pick one scenario up front (e.g. "user is debugging a TypeScript import error"). All slots should belong to that scenario.
- File paths and command arguments should be plausible for the `project_slug` in the skeleton.
- `tool_input` slots must be valid argument dicts for the named tool (e.g. `Bash` takes `{command, description}`; `Read` takes `{file_path}`; `Grep` takes `{pattern, path}`).
- `tool_result` slots should look like real output from the corresponding tool invocation.
- Subagent slots (those for records in `subagent_skeletons`) should be consistent with the parent session's delegation prompt.
- Use the template's `authoring_note` as the style guide for tone and domain.
- Keep `thinking` slot content short — a few sentences of internal reasoning.

### Step 5 — Assemble

```bash
python3 <skill-dir>/scaffolder.py assemble \
    /tmp/skeleton-<run-id>-<i>.json \
    /tmp/filled-<run-id>-<i>.json \
    <out>
```

The script prints a JSON result to stdout and exits:
- `0` — success. Result: `{"output_file": "...", "subagent_files": [...], "errors": []}`
- `1` — validation errors. Result: `{"output_file": null, "subagent_files": [], "errors": ["..."]}`

On validation failure, fix the slot content and retry up to **2** additional times. On the third failure, log the errors and skip this index (do not mark it complete).

### Step 6 — Mark checkpoint

```bash
python3 <skill-dir>/scaffolder.py checkpoint-mark <run-id> <i> <count>
```

Only call this after a successful assemble.

### Step 7 — Clean up scratch files

Remove `/tmp/skeleton-<run-id>-<i>.json` and `/tmp/filled-<run-id>-<i>.json`.

---

## Supported template event kinds

| Kind | Required fields | Notes |
|------|-----------------|-------|
| `hook` | `event` | `event` in `{SessionStart, PostToolUse, Stop}` |
| `permission_mode` | `mode` | Flat meta record; `mode` e.g. `"default"`, `"auto"`, `"plan"` |
| `file_snapshot` | — | Anchors to the next user_turn UUID (F2) |
| `user_turn` | `content_slot?` | Non-sidechain only; subagent user turns go inside subagent templates |
| `assistant_turn` | `blocks` | Each block: `{type: thinking\|text, slot}` or `{type: tool_use, tool, input_slot}` |
| `tool_result` | `content_slot?`, `result_kind?` | Pairs FIFO with prior tool_use blocks (F3); `result_kind` in `{string, structured}` |
| `subagent` | `template` | Recursive delegation; `template` is another archetype name in `template-dir` |
| `system_turn_duration` | `duration_ms`, `message_count` | End-of-turn metadata |

---

## Coherence guidance

Before filling any slots, decide on a concrete scenario: what is the user trying to do, in what project, with what outcome? Use that scenario consistently for all slot values in the file. Don't break character — if the user prompt mentions TypeScript, keep all tool invocations in that domain. Match file paths to the `project_slug` in the skeleton (e.g. `project_slug == "-Users-azasorin-Repos-assignment"` → paths under `/Users/azasorin/Repos/assignment`). Tool inputs must satisfy the tool's actual parameter schema (see schema.md §14). Assistant thinking and text should read like real Claude output — concise, direct, and technically accurate within the chosen scenario.

---

## Done

After all indices are processed, report:
- Total files written successfully
- Output directory path
- Any skipped indices and their error summaries
