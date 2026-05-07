# extract-session-templates

One-time bootstrap that analyzes real Claude Code session `.jsonl` files under
`~/.claude/projects/` and produces an archetype template library consumed by
the `generate-mock-sessions` skill.

---

## When to Run

Run this skill once after accumulating a new batch of sessions (e.g., 50+ new
files since the last run). It is a human-in-the-loop pipeline — you will be
asked to review the cluster proposal before templates are written.

---

## Invoke

```
/extract-session-templates [in=~/.claude/projects] [out=~/.claude/data/session-templates]
```

Both arguments are optional. Defaults:
- `in` — `~/.claude/projects`
- `out` — `~/.claude/data/session-templates` (created if absent)

---

## Pipeline

The skill runs a 5-step pipeline:

1. **Featurize** — Walk all `*.jsonl` files under `<in>` (including subagent
   files) and write `<out>/features.csv` with one row per file.

2. **Cluster** — Read the CSV, propose 5–15 main archetypes and 3–8 subagent
   archetypes, write `<out>/clusters.json`.

3. **User review** — Pause and ask you to edit `clusters.json` (split, merge,
   rename) until the archetype list feels right. Resume by saying "continue".

4. **Distill** — For each archetype, read its 3 representative files in full,
   identify the common event flow, write `<out>/<archetype-name>.json`.

5. **Distribution** — Compute relative weights from `member_files` counts and
   write `<out>/distribution.json`.

---

## Outputs

```
<out>/
  features.csv              # one row per .jsonl file, structural features
  clusters.json             # archetype proposal (main + subagent)
  distribution.json         # relative weights per main archetype
  typescript-bug-fix.json   # example main archetype template
  nixos-package-add.json    # example main archetype template
  explore-codebase.json     # example subagent archetype template
  ...
```

---

## Running Scripts Directly

The skill directory contains standalone Python scripts (stdlib only, Python 3.10+):

```bash
SKILL=~/.claude/skills/extract-session-templates

# Extract features from a directory of .jsonl files
python3 $SKILL/featurize.py ~/.claude/projects /tmp/features.csv

# Validate a clusters.json proposal
python3 $SKILL/validate_clusters.py /tmp/clusters.json

# Validate a single archetype template
python3 $SKILL/validate_template.py /tmp/typescript-bug-fix.json
```

Exit codes: `0` = valid / success, `1` = validation errors, `2` = usage error.

---

## Testing

```bash
cd ~/.local/share/chezmoi/.worktrees/rebuild-skills/dot_claude/skills/extract-session-templates
python3 -m unittest discover tests -v
```

All tests use stdlib `unittest` only — no external dependencies required.
