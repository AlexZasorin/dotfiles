# Real Claude Code Session Record Schema

Reference for what each record type looks like in real `~/.claude/projects/**/*.jsonl` files. Used to verify scaffolder output against reality.

Sampled from ~627 real session files across multiple projects. Cross-referenced with `records.py` builders and `validate.py` checks.

---

## 1. Common envelope fields

Most interactive records (those with a `uuid`) carry these fields. Flat metadata records (see §10–12) are exceptions.

| Field | Type | Notes |
|-------|------|-------|
| `type` | string | Record discriminator |
| `uuid` | string (UUID4) | Unique record ID |
| `parentUuid` | string \| null | Links into the turn chain; first record in chain is `null` |
| `isSidechain` | boolean | `false` in parent session, `true` in subagent files |
| `timestamp` | string (ISO 8601 ms+Z) | e.g. `"2026-04-13T19:04:53.878Z"` |
| `userType` | string | Always `"external"` in observed data |
| `entrypoint` | string | Always `"cli"` in observed data. **Omitted on sidechain records.** |
| `cwd` | string | Absolute path of the project directory |
| `sessionId` | string (UUID4) | Shared across all records in one file |
| `version` | string | Claude Code version, e.g. `"2.1.104"` |
| `gitBranch` | string | Active branch at session start |
| `slug` | string | Human-readable slug like `"jazzy-finding-sky"`. Present on most interactive records once emitted. |
| `agentId` | string | Present only on subagent records; identifies the agent within its session |

---

## 2. `progress` (hook events)

Hook progress records are emitted before/after key lifecycle events. They appear as the **first** record in a session (SessionStart) and after tool invocations (PostToolUse).

```json
{
  "parentUuid": null,
  "isSidechain": false,
  "type": "progress",
  "data": {
    "type": "hook_progress",
    "hookEvent": "SessionStart",
    "hookName": "SessionStart:startup",
    "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start"
  },
  "parentToolUseID": "1ffd34a5-b352-4cdb-ad06-0ac4fb54a2e9",
  "toolUseID": "1ffd34a5-b352-4cdb-ad06-0ac4fb54a2e9",
  "timestamp": "2026-03-25T18:06:57.525Z",
  "uuid": "edc2b2e6-d9db-4887-a338-29675ae5b8a1",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "/Users/azasorin/Repos/platform-agent",
  "sessionId": "7f130bf1-690f-48f5-9058-5c72c00ad172",
  "version": "2.1.83",
  "gitBranch": "trunk"
}
```

**`data.type` discriminator**: `"hook_progress"`

**Observed `hookEvent` values**: `SessionStart`, `PostToolUse`

Note: `toolUseID` and `parentToolUseID` are the same UUID on hook progress records (unlike agent_progress where they differ).

---

## 3. `progress` (agent_progress)

This record type appears in the **parent session file** as a wrapper for each record emitted by a subagent. It is the in-parent mirror of the subagent's own `.jsonl` file.

```json
{
  "parentUuid": "94c32d17-ec88-4dcc-bfa4-2995478389a7",
  "isSidechain": false,
  "type": "progress",
  "data": {
    "type": "agent_progress",
    "agentId": "a8b18af694ccece85",
    "message": {
      "type": "user",
      "uuid": "9a8d2e49-d110-4aa9-b737-31e8fa99374c",
      "timestamp": "2026-03-25T20:20:05.744Z",
      "message": { "role": "user", "content": [{"type": "text", "text": "..."}] }
    },
    "prompt": "Search the codebase for..."
  },
  "toolUseID": "agent_msg_011<22 chars>",
  "parentToolUseID": "toolu_011<22 chars>",
  "uuid": "81f6db6a-e1fc-4d24-9dda-423aa8ca2114",
  "timestamp": "2026-03-25T20:20:05.747Z",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "/Users/azasorin/Repos/platform-agent",
  "sessionId": "7f130bf1-690f-48f5-9058-5c72c00ad172",
  "version": "2.1.83",
  "gitBranch": "trunk"
}
```

**`data.message` payload is STRIPPED** — it is NOT the full subagent envelope. It contains only:

- `type` — the original record type (`"user"`, `"assistant"`, `"progress"`)
- `uuid` — the subagent record's UUID
- `timestamp` — the subagent record's timestamp
- `message` — the content payload (present for `user`/`assistant` records)
- `data` — present for nested `progress` records
- `requestId` — present only when `type == "assistant"`

No `cwd`, `sessionId`, `isSidechain`, `entrypoint`, or other envelope fields appear inside `data.message`. This is fix F5 in the rebuild plan.

`toolUseID` uses the `agent_msg_011…` prefix (not `toolu_011…`). A single delegation shares one stable `toolUseID` across all its wrapper records.

---

## 4. `file-history-snapshot`

Flat record emitted just before the first (or continuation) user turn. The `messageId` field anchors the **following** user record — i.e., it equals the `uuid` of the next `user` record in the file.

```json
{
  "type": "file-history-snapshot",
  "messageId": "82f4fce7-7c01-4cfb-817e-ef2dba55f357",
  "snapshot": {
    "messageId": "82f4fce7-7c01-4cfb-817e-ef2dba55f357",
    "trackedFileBackups": {},
    "timestamp": "2026-04-13T19:04:53.879Z"
  },
  "isSnapshotUpdate": false
}
```

No envelope fields (`uuid`, `sessionId`, etc.) on this record. This is fix F2.

---

## 5. `user` (string content)

The opening user prompt in a session. Content is a plain string.

```json
{
  "parentUuid": "de7e5190-07da-4d7e-a64c-03c82166889f",
  "isSidechain": false,
  "promptId": "d1eddb5c-3c53-4e0a-959c-bfd475121b48",
  "type": "user",
  "message": {
    "role": "user",
    "content": "There's a libssl3 vulnerability in our docker image..."
  },
  "uuid": "82f4fce7-7c01-4cfb-817e-ef2dba55f357",
  "timestamp": "2026-04-13T19:04:53.878Z",
  "permissionMode": "default",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "/Users/azasorin/Repos/pipes",
  "sessionId": "89e25e74-d0bf-4eed-9a01-b9c877fb1972",
  "version": "2.1.104",
  "gitBranch": "trunk"
}
```

`promptId` and `permissionMode` appear **only on non-sidechain user records** (fix F8). Subagent user records omit both fields.

---

## 6. `user` (tool_result content)

Emitted after the assistant invokes a tool. Content is a list with a single `tool_result` block.

```json
{
  "parentUuid": "45fac718-f793-459a-945e-eeb7064bec19",
  "isSidechain": false,
  "promptId": "d1eddb5c-3c53-4e0a-959c-bfd475121b48",
  "type": "user",
  "message": {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "toolu_01PepbncPK6qG63cEdhVpgxC",
        "content": "Launching skill: superpowers:systematic-debugging"
      }
    ]
  },
  "uuid": "910e267d-07f1-4f7c-8b45-5dda360d84da",
  "timestamp": "2026-04-13T19:05:26.591Z",
  "toolUseResult": {
    "success": true,
    "commandName": "superpowers:systematic-debugging"
  },
  "sourceToolAssistantUUID": "45fac718-f793-459a-945e-eeb7064bec19",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "/Users/azasorin/Repos/pipes",
  "sessionId": "89e25e74-d0bf-4eed-9a01-b9c877fb1972",
  "version": "2.1.104",
  "gitBranch": "trunk"
}
```

Key fields (fix F9):
- `toolUseResult` — top-level field; a dict on success, a string on error (e.g. `"Error: Exit code 1\n..."`)
- `sourceToolAssistantUUID` — UUID of the assistant record that issued the tool_use
- `is_error: true` — added to the inner `tool_result` block **only when** the tool failed; absent on success
- `promptId` and `permissionMode` are **absent** on tool_result user records (unlike string user turns)

---

## 7. `assistant`

```json
{
  "parentUuid": "65199600-95e4-4f92-b23c-86b7db0e0682",
  "isSidechain": false,
  "message": {
    "model": "claude-opus-4-6",
    "id": "msg_011o8UNnshHGJHUAea5SB2eL",
    "type": "message",
    "role": "assistant",
    "content": [
      {
        "type": "thinking",
        "thinking": "...",
        "signature": "EtsECmwIDBgCKkBDxajnH/ijq..."
      },
      {
        "type": "text",
        "text": "I'll investigate systematically."
      }
    ],
    "stop_reason": "end_turn",
    "stop_sequence": null,
    "stop_details": null,
    "usage": {
      "input_tokens": 6,
      "output_tokens": 220,
      "cache_creation_input_tokens": 21423,
      "cache_read_input_tokens": 17327,
      "service_tier": "standard",
      "cache_creation": {
        "ephemeral_5m_input_tokens": 0,
        "ephemeral_1h_input_tokens": 21423
      },
      "inference_geo": ""
    }
  },
  "requestId": "req_011Ca2HsHhNfRwq3e2kNeeiv",
  "type": "assistant",
  "uuid": "e95c885f-0d53-4c0e-8134-6d1b5b4f3c62",
  "timestamp": "2026-04-13T19:05:26.442Z",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "/Users/azasorin/Repos/pipes",
  "sessionId": "89e25e74-d0bf-4eed-9a01-b9c877fb1972",
  "version": "2.1.104",
  "gitBranch": "trunk"
}
```

**Content block types**:
- `thinking` — extended thinking. `thinking` field is non-empty, `signature` is a ~380-char base64 string.
- `text` — prose response.
- `tool_use` — tool invocation. Has `id` (`toolu_011…`), `name`, `input` dict, `caller: {"type": "direct"}`.

**Stop reasons**: `"end_turn"` (text or thinking response), `"tool_use"` (tool invocation).

**Full `usage` shape**:

| Field | Notes |
|-------|-------|
| `input_tokens` | Tokens not in cache |
| `output_tokens` | Generated tokens |
| `cache_creation_input_tokens` | Tokens written to cache |
| `cache_read_input_tokens` | Tokens read from cache |
| `service_tier` | `"standard"` |
| `cache_creation` | Nested object: `{"ephemeral_5m_input_tokens": N, "ephemeral_1h_input_tokens": N}` |
| `inference_geo` | String, often `""` or `"not_available"` |

`stop_details` is always `null` in observed data.

---

## 8. `system` (subtype: turn_duration)

Emitted at the end of a multi-turn exchange to summarize elapsed time.

```json
{
  "parentUuid": "d29ab14c-87cc-4aa5-a9c4-c4af7d21308f",
  "isSidechain": false,
  "type": "system",
  "subtype": "turn_duration",
  "durationMs": 211284,
  "messageCount": 54,
  "timestamp": "2026-04-13T19:13:33.069Z",
  "uuid": "9ac23cec-7bba-4403-a021-7c353639ea4c",
  "isMeta": false,
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "/Users/azasorin/Repos/pipes",
  "sessionId": "89e25e74-d0bf-4eed-9a01-b9c877fb1972",
  "version": "2.1.104",
  "gitBranch": "trunk",
  "slug": "hidden-spinning-turtle"
}
```

`isMeta: false` is present on this record type.

---

## 9. `permission-mode`

Flat record, typically the first record in a session file.

```json
{
  "type": "permission-mode",
  "permissionMode": "default",
  "sessionId": "89e25e74-d0bf-4eed-9a01-b9c877fb1972"
}
```

No `uuid`, no `timestamp`, no envelope fields.

---

## 10. `attachment`

Carries caller-supplied metadata injected by the harness (hooks, skill listings, deferred tool deltas, etc.). When the envelope fields (`uuid`, `timestamp`, etc.) are present, the record matches the standard envelope shape. Earlier attachment records (e.g. hook_success at session start) may omit them.

```json
{
  "parentUuid": "5de0d00a-15ab-4206-ad2c-413fb1a08ba6",
  "isSidechain": false,
  "attachment": {
    "type": "command_permissions",
    "allowedTools": []
  },
  "type": "attachment",
  "uuid": "68259df3-880f-4710-a02e-4dd3addb6a6f",
  "timestamp": "2026-04-13T19:05:26.590Z",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "/Users/azasorin/Repos/pipes",
  "sessionId": "89e25e74-d0bf-4eed-9a01-b9c877fb1972",
  "version": "2.1.104",
  "gitBranch": "trunk"
}
```

The `attachment` field is a caller-supplied dict. Common `attachment.type` values observed: `hook_success`, `hook_additional_context`, `deferred_tools_delta`, `skill_listing`, `ultrathink_effort`, `command_permissions`, `mcp_instructions_delta`.

---

## 11. `last-prompt`

Flat record echoing the most recent user prompt text. No envelope fields.

```json
{
  "type": "last-prompt",
  "lastPrompt": "Why doesn't the @generate-report.sh script work...",
  "sessionId": "9cb8e1d8-f0b7-48cc-a399-fdc5fd2fbef7"
}
```

---

## 12. `queue-operation`, `custom-title`, `agent-name`, `ai-title`

Flat metadata records. No `uuid`, no `timestamp`, no envelope fields beyond `sessionId`.

```json
{ "type": "queue-operation", "operation": "enqueue", "timestamp": "2026-03-31T21:10:02.159Z", "sessionId": "...", "content": "..." }
{ "type": "queue-operation", "operation": "dequeue", "timestamp": "...", "sessionId": "..." }
{ "type": "queue-operation", "operation": "remove",  "timestamp": "...", "sessionId": "..." }
{ "type": "custom-title",    "customTitle": "test-folder-deletion-task-unassign", "sessionId": "..." }
{ "type": "agent-name",      "agentName":   "test-folder-deletion-task-unassign", "sessionId": "..." }
{ "type": "ai-title",        "aiTitle":     "Review completed Jira tickets from past year", "sessionId": "..." }
```

---

## 13. Subagent file structure

Subagent sessions are stored in sibling files relative to their parent session:

```
<project-slug>/<sessionId>.jsonl                          ← parent session
<project-slug>/<sessionId>/subagents/agent-<agentId>.jsonl ← subagent file
```

**Subagent file characteristics**:
- First record has `parentUuid: null`
- All records have `isSidechain: true`
- All records share the parent's `sessionId`
- `agentId` is present on every record
- **No** `entrypoint` on any record (sidechain omits it)
- **No** `promptId` or `permissionMode` on user records (fix F8)
- Records use `slug` from the parent session context

`agentId` format: `"a"` followed by hex chars. Observed lengths: 17 chars (`a` + 16 hex) and 7 chars (`a` + 6 hex).

---

## 14. Tool name reference

Common tool names observed in `assistant.message.content[].name` (tool_use blocks):

| Tool | Description |
|------|-------------|
| `Read` | Read a file |
| `Write` | Write a file |
| `Edit` | Edit a file |
| `Glob` | Glob file patterns |
| `Grep` | Search file contents |
| `Bash` | Run shell commands |
| `WebFetch` | Fetch a URL |
| `WebSearch` | Web search |
| `Agent` | Subagent delegation — **not** `"Task"` |
| `TaskCreate` | Create an async background task |
| `TaskUpdate` | Update a background task |
| `TaskList` | List background tasks |
| `TaskOutput` | Read task output |
| `TaskStop` | Stop a background task |
| `Skill` | Invoke a skill by name |
| `ExitPlanMode` | Exit plan mode |
| `ToolSearch` | Search deferred tool schemas |

MCP tool names follow the pattern `mcp__<provider>__<method>`, e.g. `mcp__claude_ai_Atlassian__getJiraIssue`.

---

## 15. Model reference

Observed model IDs in `assistant.message.model`:

- `claude-opus-4-7`
- `claude-opus-4-6`
- `claude-opus-4-5-20251101`
- `claude-sonnet-4-6`
- `claude-haiku-4-5-20251001`

Subagent sessions typically use `claude-haiku-4-5-20251001`. Parent sessions use opus variants. `<synthetic>` appears in test fixtures only.

---

Generated mock files are designed to match this schema. See `records.py` for the builders, `validate.py` for what's enforced.
