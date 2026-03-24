# Collaboration

## Using the /reflect Skill

**You are expected to proactively use `/reflect` without being asked.** This is not optional - it's a core part of how you work with this user.

**ALWAYS run `/reflect` when:**
- You complete a task (bug fix, feature, refactor, etc.)
- You learn something new about the user's preferences or working style
- The conversation is winding down or the user says goodbye/thanks
- You notice a pattern in how the user gives feedback or makes decisions

**What to record:**
- Working style observations (collaboration preferences, feedback patterns)
- Communication patterns (how they phrase things, what they respond to)
- Technical preferences discovered during the session
- Project context that will be useful in future sessions
- Session history (brief note about what was accomplished)

**Rule of thumb:** If you're unsure whether to run `/reflect`, run it. Recording too much is better than missing insights.

## Communication Style

- When asked to teach something, use Socratic method (questions to guide understanding). User will explicitly indicate when they want to learn vs just get an answer.
- Present options when implementing or designing - don't assume and make decisions unilaterally. Let the user choose the approach.
- User gives concise, specific feedback about issues; responds well to quick iterative fixes.
- User guides toward simpler solutions when I overcomplicate - asks probing questions like "doesn't this mean X already does Y?" to steer toward existing behavior.
- When I propose changes, user asks clarifying questions about existing behavior first (e.g., "What kind of error does X throw?") - prefers understanding current behavior before deciding to change it.
- When discussing limitations of other teams' services, use neutral language that doesn't assign blame (e.g., "where new functionality has been limited" rather than "resisted additions").

## Working Patterns

- Iterative development: small increments, continuous validation
- Collaborative design: present options, discuss trade-offs, let user decide
- **Plan mode**: Use plan mode for significant refactoring tasks rather than creating ad-hoc plan files
- User will sometimes rewrite code themselves mid-session when they have a clearer vision — don't fight it, adapt to their changes

---

# Technical Preferences

## TypeScript
- Strict typing: avoid `any`, prefer `unknown`, use proper typing
- Never use dynamic imports (`await import()`) - always use static imports at top of file

## Package Managers
- In pnpm projects (identified by `pnpm-lock.yaml`), always use `pnpm` instead of `npm` and `pnpx` instead of `npx`

## React

### useEffect Anti-Patterns
Avoid using useEffect when you don't need one. See: https://react.dev/learn/you-might-not-need-an-effect

Common anti-patterns to avoid:
1. **Transforming data for rendering** - Calculate at top level of component instead of using Effect + setState
2. **Handling user events** - Put logic in event handlers, not Effects
3. **Caching expensive calculations** - Use `useMemo` instead of state + Effect
4. **Resetting state when props change** - Use component `key` prop instead
5. **Adjusting state based on props** - Calculate during rendering or store only identifiers
6. **Chains of Effects** - Consolidate logic into event handlers
7. **POST requests for user actions** - Call API directly in event handlers
8. **Updating state from props** - Calculate derived values during rendering
9. **Notifying parent components** - Call callbacks directly in event handlers
10. **Passing data to parent** - Fetch in parent and pass down as props

Effects ARE appropriate for: synchronizing with external systems, data fetching (with cleanup), subscribing to external stores, browser/DOM APIs.

### Other React Preferences
- Prefer arrow functions over named function expressions in `memo()` calls

## File Naming
- kebab-case for directories (e.g., `flow-builder/` not `FlowBuilder/`)

## Testing Philosophy

Write mostly integration tests, sometimes unit tests. Start with integration tests because they:
- Provide the most value
- Are tied closer to business cases/user stories
- Cover more ground per test

Unit tests tend to be detached from overarching use cases.

**When to add unit tests**: When refactoring a module A into submodules B and C (A ← B, A ← C), the existing tests for A become integration tests. There's no benefit to writing unit tests for B and C **unless** they are used elsewhere. If C is later used in module D, then it makes sense to add a specific unit test for C because it now implements a shared interface between multiple modules.

### Test Structure
- Fixtures should be in separate `*.fixtures.ts` files, co-located with the test file
- Fixtures should be data objects that can be inserted directly into DB, not helper functions
- Fixture variables should use SCREAMING_SNAKE_CASE
- Prefer bypassing service layer in tests when setting up fixtures (insert directly into MongoDB)
- Assert on data fetched from database after operations, not on return values (verifies persistence)

## TDD Workflow
- Write test first, see it fail, write implementation, see it pass, iterate
- Small increments, continuous validation

## Jira (riskandsafetysolutions.atlassian.net)

**Cloud ID**: `465feb81-52f2-418f-8a4a-710ad348bc9b`

### Team Assignment
- The actual Team field is `customfield_10001` - requires the team UUID, not a string
- Team Mango UUID: `1fcbcf66-1c92-4e86-b2a1-22584241cd91`
- `customfield_10355` is a separate text field that displays "Team Mango" but is NOT the team assignment field used for board filtering

### Work Type Field
Field: `customfield_10421` (set with `{"id": "<option_id>"}`)
- feature: `10289`
- tech-debt: `10290`
- bug: `10291`
- r-and-d: `10292`

### Components (PLATFORM project)
Set by ID in array format: `[{"id": "<component_id>"}]`
- Task Management: `10411`
- Outcomes: `10156`

### Atlassian MCP Integration
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
- **Issue links are not supported** by the Atlassian MCP tools. The user must
  add "relates to" / "blocks" links manually in Jira. Issue link data is
  visible when reading issues (in `issuelinks` field) but cannot be created.

### Ticket Creation Preferences
- **The user writes all summaries and descriptions.** Do not generate ticket
  content. Enter the user's text verbatim.
- When the user asks to create a ticket, prompt for any missing required fields
  (summary, description, issue type, work type) rather than guessing.
- Use title case for human-readable references to enums or event types in ticket
  descriptions (e.g., "Flow Started" not "FLOW_STARTED").

### JQL Custom Field Syntax
Use `cf[fieldId]` to filter by custom fields:
```
cf[10355] = "Team Mango"
```

### Common Jira Queries
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

---

# Project Context

- **Assignment project**: Monorepo with GraphQL server, React components, workflow orchestration (Flowork)
- **FlowBuilder**: ReactFlow-based visual workflow editor in demo app
- **Outcome project**: Monorepo with GraphQL server for managing outcome configurations (TEXT, NUMBER, CALCULATED, TRAINING, RISK, SMART, ACKNOWLEDGEMENT outcome types). Uses MongoDB, FGA for permissions.
- **Forms project**: Monorepo with form-builder-server and form-renderer-server. Uses registry+transformer pattern (renderer) and adapter pattern (builder) for GraphQL↔internal↔MongoDB type transformations. FGA for permissions, external workflow service for lifecycle.

---

# Session History

- 2025-01-07: Set up PARTNER_MODEL system and /partner skill. Captured initial preferences around TDD, Socratic teaching, and presenting options.
- 2025-01-07: Explored FlowBuilder refactoring approach. Work reverted for later revisit.
- 2026-01-07: Implemented `cloneOutcomes` mutation in Outcome project. Reorganized preferences: technical preferences moved to CLAUDE.md, working style kept in PARTNER_MODEL.md.
- 2026-01-08: Modified `cloneOutcomes` to throw error for non-existent source template groups (using existing `findOne` behavior). Updated CLAUDE.md and partner skill to always add "/partner" as final TODO item.
- 2026-01-08: Created E2E API test for `cloneOutcomes` permission checks. Added multi-user authentication (GPOP user) to E2E framework. User clarified to avoid unnecessary abstractions (e.g., don't create a fixtures file just to re-export imports).
- 2026-01-09: Fixed `cloneOutcomes` permission check - moved check into service layer, checking on SOURCE outcome page ID (not template ID). User guided toward simpler implementation: use existing methods directly rather than creating wrapper functions, and let existing error behavior propagate rather than catching/re-throwing.
- 2026-01-09: Refactored E2E CloneOutcomes test to use API calls instead of UI (PageHelper). Key insight: `outcomePage` query auto-creates page if missing (uses assertCanManageTemplate), while `createOutcomePage` mutation requires different permission. Refactored ApiHelper methods to accept parameters instead of hardcoded IDs.
- 2026-01-16: Editorial review of FLOWORK_DESIGN_DOC.md - multiple passes for spelling, grammar, tone, and "handwave-y" language. User prefers to handle fixes themselves after issues are identified, and values preserving their original voice with surgical edits.
- 2026-01-16: Created Jira tasks for Team Mango in PLATFORM project. Learned Jira field mappings (Team field is customfield_10001 with UUID, not customfield_10355 text field). User sets ground rules upfront for Jira work: don't generate content, enter text verbatim. Documented technical Jira details in CLAUDE.md.
- 2026-01-22: Fixed bug in RiskOutcomeConfig - disabled fields when outcome page is published. User asked clarifying questions about domain concepts (outcomes vs risk levels) before deciding on approach. Initially considered validation-based approach (block publishing), then pivoted to simpler disable-on-publish approach. TDD workflow: write failing test first, then implement fix.
- 2026-01-26: Explored Forms repo architecture — registry/transformer patterns, createForm performance analysis. User interested in applying transformer pattern to own API for GraphQL→internal→MongoDB transformations. Investigated MongoDB profiling, write concern, and idempotency. User is pragmatic about other teams' design choices (re: fire-and-forget FGA calls) — assumes intentional unless proven otherwise, won't change code that isn't their responsibility without reason.
- 2026-01-26: Jira backlog management session. Created PLATFORM-6166 (Move hardcoded flows to MongoDB). Updated PLATFORM-6116 description to suggest splitting AC into parallel tasks. Evaluated all Sprint 23 + top 7 backlog tickets for potential subtask splits. Updated project CLAUDE.md with Jira/Atlassian MCP integration notes, Team Mango context, and ticket creation preferences. Learned: Team custom field (customfield_10001) requires bare UUID string, not `{"id": "..."}` format.
- 2026-01-26: Analyzed and reorganized daily notes (2026-01-23.md) for redundancy. Consolidated scattered items into clear sections (Documentation, Flowork Cleanup, Flowork Testing, Stories to Create, Problems to Solve, Brainstorm). Removed duplicate "conditional logic" entry. User approved the analysis then asked to apply it directly — comfortable with quick restructuring of their own notes.
- 2026-01-27: Created PLATFORM-6199 bug ticket (cloneOutcomes throws error when no published outcome exists). Discovered Outcomes component ID (10156). Confirmed Atlassian MCP lacks issue link creation — user added the "relates to PLATFORM-6195" link manually.
- 2026-02-13: Implemented PLATFORM-6393 "Allow Assignment to Target a Folder + Role" in Assignment project. Added folderId/roleId to GraphQL AssignEventInput and trigger config, created FolderGateway stub (returns []), added FolderRoleTaskAssign types, extended AssignTaskActivity Zod schemas for folder+role targeting, added assignTaskToFolderRole to TaskService using Promise.all for parallel assignment. TDD workflow enforced by user. User rewrote the Zod schemas themselves (simpler 4-variant union without z.undefined guards, uses `'assignedTo' in input` for branching). User prefers Promise.all over sequential awaits when tasks are independent. User deferred discriminated union refactor of input types (marked FIXME) — plans to revisit later with proper internal types.
- 2026-02-13: Fixed chezmoi `.npmrc` template in dotfiles repo. Made it OS-conditional: Linux gets `prefix=${HOME}/.npm-global` (NixOS setup), macOS/darwin gets GitHub Packages registry config (`@risk-and-safety` scoped to `npm.pkg.github.com` with `GITHUB_TOKEN` env var). Found npmrc setup in Confluence "Lesson 1: Environment" page. User chose env var over promptStringOnce or macOS Keychain for token sourcing.
- 2026-02-24: Implemented PLATFORM-6527 "Trigger Form Completion Rule from emitAssignmentEvent" in Assignment project. Added `parentFolderId` to `AssignEventInput`, `findMatchingRules` to `RuleDBAdapter`, `handleAssignEvent` to `RuleService`, wired resolver to use `RuleService` instead of `FlowService`. User questioned unnecessary `userId` parameter — pushed to remove fallback pattern not used elsewhere. User asked about cast necessity — left TODO for internal discriminated union refactor. Commit-msg hook requires Jira ticket in message to avoid tty prompt. Don't add Co-Authored-By to commits.
- 2026-03-20: Set up local integration testing infrastructure for Assignment project. Added docker services (notification, redpanda, library-management, federation-router). Added notification schema to codegen from GitHub. Switched integration tests from Jest to Vitest (ESM compat). Installed folder-fixtures and bumped relationship-v2-fixtures. Wrote first integration test (create-complete-form-rule.spec.ts). Rewrote initialize-local.sh. Discovered folder service requires real Clerk dev keys — blocked until Monday. Key learnings: follow sibling repo patterns exactly (notification repo is the reference), add schemas from GitHub not locally, append /graphql at point of use not in env vars, don't overthink schema conflicts.
