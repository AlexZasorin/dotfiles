---
name: jira-platform
description: Use for any Jira or Confluence work on riskandsafetysolutions.atlassian.net — creating, editing, querying, or drafting tickets in the PLATFORM project. Carries the cloud ID, custom field IDs (Team, Work Type, Components), team UUIDs, JQL syntax, common queries, and the user's ticket-drafting conventions.
---

# Jira (riskandsafetysolutions.atlassian.net)

**Cloud ID**: `465feb81-52f2-418f-8a4a-710ad348bc9b`

## Team Assignment

- The actual Team field is `customfield_10001` - requires the team UUID, not a string
- Team Mango UUID: `1fcbcf66-1c92-4e86-b2a1-22584241cd91`
- Team Jupiter UUID: `f6ce57b1-47f7-4ae4-9f99-f2d7a264180f` (forms / form-builder / form-renderer)
- `customfield_10355` is a separate text field that displays the team name but is NOT the team assignment field used for board filtering. Setting `customfield_10001` populates it.
- To find another team's UUID: JQL `project = PLATFORM AND cf[10355] = "<Team Name>"` requesting the `customfield_10001` field, and read the `id` off any result.

## Work Type Field

Field: `customfield_10421` (set with `{"id": "<option_id>"}`)

- feature: `10289`
- tech-debt: `10290`
- bug: `10291`
- r-and-d: `10292`

## Components (PLATFORM project)

Set by ID in array format: `[{"id": "<component_id>"}]`

- Task Management: `10411`
- Outcomes: `10156`

## Atlassian MCP Integration

- Use the `search` tool for general queries across Jira and Confluence. Only use
  `searchJiraIssuesUsingJql` or `searchConfluenceUsingCql` when JQL/CQL syntax
  is specifically needed (e.g., filtering by custom fields, ordering, complex
  conditions).
- Use `fetch` to get full details on items returned by `search` (pass the ARI
  directly).
- Use `getJiraIssue` when you already have an issue key (e.g., `PLATFORM-6075`).
- Pass descriptions as **markdown**, not ADF. The tool handles conversion.
- When setting `customfield_10001` (Team), pass the UUID as a bare string, not
  as `{"id": "..."}`. Example: `"customfield_10001": "1fcbcf66-..."`.
- When setting `customfield_10421` (Work Type), use the `{"id": "..."}` format.
- **Issue links ARE supported** (corrected 2026-09-10; they were not before).
  Use `createIssueLink`, and `getIssueLinkTypes` when the type name is unknown.
  Direction is the confusing part: `inwardIssue` is the issue that blocks,
  `outwardIssue` is the one that is blocked. So "A blocks B" is
  `inwardIssue: A, outwardIssue: B`. Read `issuelinks` back afterward to confirm
  the direction rendered the way you meant.
- The HTTP+SSE endpoint is deprecated after 2026-06-30 in favor of Streamable
  HTTP. Tool results carry a notice asking that it be passed on to the user.

## Ticket Creation Preferences

- **Draft, then let the user edit, then create.** The user's standing workflow:
  put the draft in an untracked repo-root MD file, wait for them to edit it,
  re-read the file, and create from their edited text verbatim. Never create a
  ticket straight from your own draft.
- Enter the user's text verbatim, and keep out anything they cut. Do not
  reinstate a paragraph they deleted.
- When the user asks to create a ticket, prompt for any missing required fields
  (issue type, work type, component, team) rather than guessing.
- Use title case for human-readable references to enums or event types in ticket
  descriptions (e.g., "Flow Started" not "FLOW_STARTED").
- Strip markdown hard-wrap newlines from paragraphs before sending to Jira.

**When explicitly asked to draft a ticket**, match this style — the user cut
roughly 60% of a draft to reach it:

- A ticket states the problem, the fix, and how to tell it worked. Nothing else.
- No implementation plan: no file lists, no per-seam scope maps, no "which
  function changes". Code TODOs carry that; the ticket does not.
- No investigative findings or evidence (line numbers, what a runtime does, risks
  I discovered). That is conversation content, not ticket content.
- No rejected alternatives. State what to do, not what was ruled out and why.
- Acceptance criteria hold the precision, and state the purpose where it is not
  obvious ("...to allow for safe migration for consumers").
- Give non-functional requirements their own AC line rather than burying them in
  prose (e.g. "Backfill script is idempotent").
- One name per thing throughout. Do not alternate synonyms for the same artifact.
- Plain declarative sentences. Few em-dash asides.

## JQL Custom Field Syntax

Use `cf[fieldId]` to filter by custom fields:

```
cf[10355] = "Team Mango"
```

## Common Jira Queries

```
# Team Mango backlog (ordered by rank)
project = PLATFORM AND cf[10355] = "Team Mango" AND sprint is EMPTY AND status != Done ORDER BY rank ASC

# Current sprint tickets
project = PLATFORM AND cf[10355] = "Team Mango" AND sprint in openSprints()

# Future sprint tickets
project = PLATFORM AND cf[10355] = "Team Mango" AND sprint in futureSprints()

# All open Team Mango tickets
project = PLATFORM AND cf[10355] = "Team Mango" AND status != Done
```
