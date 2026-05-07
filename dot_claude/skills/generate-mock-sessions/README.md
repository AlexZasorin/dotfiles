# generate-mock-sessions

Per-run generator that fabricates plausible Claude Code session `.jsonl` files for training a local content-aware model. Consumes the archetype template library produced by `extract-session-templates`.

---

## Prerequisites

Run `/extract-session-templates` first to populate the template library at `~/.claude/data/session-templates/`. That skill produces `distribution.json` plus one `<archetype>.json` per archetype.

---

## Invoke

```
/generate-mock-sessions [count=N] [out=PATH] [archetype=NAME] [run-id=ID]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `count` | `5` | Number of session files to generate |
| `out` | `./mock-data` | Output root directory |
| `template-dir` | `~/.claude/data/session-templates` | Template library location |
| `archetype` | — | Pin all files to one archetype |
| `run-id` | auto | Identifier for checkpoint resumption |

---

## How it works

For each file index `i` in `range(count)`:

1. **Read checkpoint** — skip indices already completed in a previous run.
2. **Pick template** — sample an archetype from `distribution.json`, or use the `archetype` argument.
3. **Generate skeleton** — `scaffolder.py skeleton` builds a structural scaffold: UUID chains, timestamps, envelope fields, and `{_slot}` markers for content that needs filling.
4. **Fill slots** — read the `slot_manifest` and write coherent content for every slot in a single pass. All slots should belong to the same scenario.
5. **Assemble** — `scaffolder.py assemble` substitutes slots, validates the result, and writes JSONL files. Retries up to 2 times on validation failure; skips on third failure.
6. **Mark checkpoint** — record the completed index for resumption.
7. **Clean up** — remove temporary skeleton and filled-slots files.

---

## Running scripts directly

```bash
SKILL=~/.claude/skills/generate-mock-sessions

# Build a skeleton from a template
python3 $SKILL/scaffolder.py skeleton <template.json> \
    --template-dir <dir> \
    --seed N > skeleton.json

# Fill slots and write JSONL output
python3 $SKILL/scaffolder.py assemble skeleton.json filled-slots.json --out PATH

# Mark an index completed
python3 $SKILL/scaffolder.py checkpoint-mark <run-id> <index> <total>

# Load checkpoint state
python3 $SKILL/scaffolder.py checkpoint-load <run-id>
```

**Exit codes**: `0` = success, `1` = validation error, `2` = usage error.

---

## Testing

```bash
cd ~/.local/share/chezmoi/.worktrees/rebuild-skills/dot_claude/skills/generate-mock-sessions
python3 -m unittest discover tests -v
```

112 tests across 4 modules (`test_records`, `test_validate`, `test_scaffolder`, `test_integration`).

---

## Limitations

- **Token counts are approximate.** `output_tokens` is recomputed from filled-content character length using a `chars/4` heuristic. `input_tokens` is sampled from a coarse range. These figures are not predictive of real API token usage.
- **Not all record types have generation paths.** `attachment` requires a caller-supplied payload dict; it is not auto-generated from templates. `last-prompt` is supported as a builder but is not auto-emitted per-turn.
- **Assemble is single-threaded.** For large batch runs, use checkpoint resumption across multiple invocations rather than parallelizing within one invocation.
