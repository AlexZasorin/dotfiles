---
name: extract-session-templates
description: One-time bootstrap that analyzes real Claude Code session .jsonl files under ~/.claude/projects/ and produces an archetype template library at ~/.claude/data/session-templates/ for the generate-mock-sessions skill to consume.
---

# extract-session-templates

Walks `~/.claude/projects/**/*.jsonl` (main sessions and subagent files), extracts structural features per file, clusters them into workflow archetypes, distills per-archetype JSON templates, and writes a distribution file. Run once; re-run when the session library has grown substantially.

---

## Step 1: Featurize

Run `featurize.py` to walk the session library and produce a CSV of structural features, one row per file.

```bash
python3 ~/.claude/skills/extract-session-templates/featurize.py \
  ~/.claude/projects \
  <out>/features.csv
```

**CSV columns** (in order):

| Column | Description |
|--------|-------------|
| `path` | Absolute path to the `.jsonl` file |
| `project_slug` | First path component relative to `<input-dir>` |
| `is_subagent` | `True` if `subagents/` appears in path |
| `session_id` | Filename stem (UUID) |
| `length` | Total number of records in the file |
| `duration_seconds` | Elapsed seconds from first to last timestamped record (0.0 if < 2 timestamps) |
| `tool_sequence` | JSON array of assistant tool_use names in order |
| `subagent_delegation_count` | Count of `Agent` tool_use blocks |
| `uses_plan_mode` | `True` if any user record has `permissionMode == "plan"` |
| `model_mix` | JSON object of `{model: count}` for assistant records |
| `topic_fingerprint` | JSON array of distinctive tokens from the first non-sidechain user turn |

---

## Step 2: Cluster

Read `<out>/features.csv` and propose archetypes (5–15 main, 3–8 subagent) that cover the distribution. Write the proposal to `<out>/clusters.json`.

**clusters.json schema:**

```json
{
  "main_archetypes": [
    {
      "name": "kebab-case-name",
      "description": "One-sentence description of what sessions in this archetype do",
      "member_files": ["path/to/session.jsonl", "..."],
      "representative_files": ["path/to/best-example.jsonl", "..."]
    }
  ],
  "subagent_archetypes": [
    {
      "name": "kebab-case-name",
      "description": "...",
      "member_files": ["..."],
      "representative_files": ["..."]
    }
  ]
}
```

**Naming guidance:** Archetype names should be kebab-case and grounded in the real workflow the session represents. Good examples:

- `jira-triage` — reviewing/creating/updating Jira tickets
- `nixos-package-add` — adding packages to NixOS configuration
- `typescript-bug-fix` — debugging and fixing TypeScript errors
- `integration-test-setup` — writing or wiring integration tests
- `dotfiles-tweak` — editing chezmoi-managed dotfiles
- `code-review-response` — implementing feedback from code review
- `explore-codebase` — read-only exploration with multiple search/read tools

Pick exactly 3 representative files per archetype — choose the clearest, most self-contained examples.

Subagent files (where `is_subagent == True`) should be assigned to **subagent_archetypes** only, not main archetypes.

---

## Step 3: User Review

> **STOP.** Cluster proposal written to `<out>/clusters.json`. Please review and edit — split, merge, or rename archetypes until the list feels right. When you're done, tell me to continue.

After the user says to continue, validate the schema:

```bash
python3 ~/.claude/skills/extract-session-templates/validate_clusters.py \
  <out>/clusters.json
```

Fix any reported errors and re-validate before proceeding.

---

## Step 4: Distill

For each archetype in `clusters.json`, read its 3 representative files in full. Identify the common event flow — what kinds of records appear, in what order, with what tools and models. Write `<out>/<archetype-name>.json` following the template schema below.

After writing each template, validate it:

```bash
python3 ~/.claude/skills/extract-session-templates/validate_template.py \
  <out>/<archetype-name>.json
```

Fix any errors before moving to the next archetype.

### Template Schema

```json
{
  "archetype": "kebab-case-name",
  "authoring_note": "Human-readable note about how this was derived",
  "length_distribution": {
    "min_records": 10,
    "typical": 50,
    "max": 300
  },
  "model_weights": {
    "claude-opus-4-7": 0.6,
    "claude-haiku-4-5": 0.4
  },
  "subagent_probability": 0.3,
  "events": [
    { "kind": "...", ... }
  ]
}
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `archetype` | string (kebab-case) | Must match the filename stem |
| `authoring_note` | string | How this template was derived; used for provenance |
| `length_distribution` | object | `min_records ≤ typical ≤ max` (record counts) |
| `model_weights` | object | `{model_id: weight}` — weights must sum to 1.0 |
| `subagent_probability` | float [0,1] | Probability that a session of this archetype spawns subagents |
| `events` | array | Ordered list of event descriptors (see grammar below) |

### Event-Kind Grammar

Each event in the `events` array has a required `kind` field. Valid kinds:

| Kind | Extra fields | Description |
|------|-------------|-------------|
| `hook` | — | SessionStart/Stop hook progress record |
| `file_snapshot` | — | `file-history-snapshot` record at session open |
| `user_turn` | `content_slot?` | User submitting a prompt (non-sidechain) |
| `assistant_turn` | `blocks?` | Assistant response; blocks have `type` in `{thinking, text, tool_use}` |
| `tool_result` | `result_kind?` | User record returning a tool result; `result_kind` in `{string, structured}` |
| `subagent` | `template` | Agent delegation — `template` names the subagent archetype JSON |
| `permission_mode` | `mode` | `permission-mode` record recording a mode change (e.g. `"auto"`, `"plan"`) |
| `system_turn_duration` | `duration_ms`, `message_count` | Synthetic record summarizing typical tool-use round-trip duration |

Blocks within `assistant_turn`:
- `{"type": "thinking", "slot": "..."}` — extended thinking block
- `{"type": "text", "slot": "..."}` — prose response
- `{"type": "tool_use", "name": "ToolName", "input_slot": "..."}` — tool invocation

All `slot` / `input_slot` / `content_slot` values must be unique across the entire template.

---

## Step 5: Write distribution.json

After all archetype templates are written and validated, compute the relative weight of each main archetype and write `<out>/distribution.json`:

```json
{
  "main": {
    "typescript-bug-fix": 0.18,
    "jira-triage": 0.12,
    "..."
  }
}
```

Each weight is `len(archetype.member_files) / total_main_member_files`. Values must sum to 1.0.

---

## Done

Artifacts are in `<out>/`:

```
<out>/
  features.csv
  clusters.json
  distribution.json
  <archetype-name>.json    (one per main archetype)
  <archetype-name>.json    (one per subagent archetype)
```

The `generate-mock-sessions` skill reads `distribution.json` plus the per-archetype templates to synthesize new session files.
