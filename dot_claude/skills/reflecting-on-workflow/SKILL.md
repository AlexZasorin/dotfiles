---
name: reflecting-on-workflow
description: Use after completing a task, being corrected by the user, or learning something new about how the user prefers to work. Use when the user redirects your approach, expresses a preference, or tells you to do something differently.
---

# Reflecting on Workflow

## Overview

After completing tasks or being corrected, proactively update `~/.claude/CLAUDE.md` with notes about the user's preferences, workflow patterns, and corrections. This builds persistent memory across sessions so the user doesn't have to repeat themselves.

**Core principle:** Every correction or preference the user expresses is a lesson. Write it down immediately so future sessions start smarter.

## When to Reflect

- User corrects your approach ("don't do X, do Y instead")
- User expresses a preference ("I prefer concise responses")
- User redirects you ("use this tool instead")
- You complete a task and noticed patterns in how the user works
- User explicitly asks you to reflect or take notes

**Do NOT ask permission.** The user wants this to happen proactively. Just do it.

## What to Note

| Category | Examples |
|----------|----------|
| **Tool preferences** | "Use `gh search code` instead of WebSearch for configs" |
| **Communication style** | "Keep responses concise", "No emoji", "Show code not explanations" |
| **Workflow patterns** | "Show changes before editing", "Don't commit without asking" |
| **Code style** | "Minimal comments", "Prefer X pattern over Y" |
| **Things that annoyed them** | Any correction = something to avoid next time |

## Where to Write

- **Global preferences** (apply everywhere) → `~/.claude/CLAUDE.md`
- **Project-specific** (apply to this repo only) → repo's `CLAUDE.md`

Most user preferences are global. When in doubt, use `~/.claude/CLAUDE.md`.

## How to Update

1. Read the current `~/.claude/CLAUDE.md` (create if it doesn't exist)
2. Check if the preference is already noted — don't duplicate
3. Add the new note under the appropriate section
4. Keep entries concise — one line per preference
5. Tell the user what you noted (briefly, one sentence)

### Format

Use a simple, scannable structure:

```markdown
# User Preferences

## Research & Problem Solving
- Use `gh search code` with path filters to find real-world examples instead of web search
- Cross-reference multiple GitHub configs before recommending a solution

## Communication
- Keep responses concise and focused on the solution
- Skip lengthy explanations unless asked

## Workflow
- Show proposed changes before editing files
- Don't commit without explicit approval

## Code Style
- Minimal comments — only when logic is non-obvious
- Follow existing patterns in the codebase
```

## Common Mistakes

- **Asking permission**: The user already wants this. Just update the file and briefly mention what you noted.
- **Writing too much**: One line per preference. Not a paragraph.
- **Wrong file**: Personal preferences go in `~/.claude/CLAUDE.md`, not the repo CLAUDE.md.
- **Forgetting to check existing notes**: Read first, don't duplicate.
- **Only reflecting when asked**: The whole point is to do this proactively after corrections and completed tasks.
