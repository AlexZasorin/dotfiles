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
- Avoid user-defined type-predicate guards (`(x): x is T`) — a predicate is an unchecked assertion TS trusts without verifying the body, so a wrong one silently lies. Prefer a plain inline `if` (truthiness/discriminant) check; it gives the same control-flow narrowing AND TS actually verifies it. Reach for a predicate only when it's genuinely reused across many sites, or when the check is complex enough that naming it meaningfully improves readability.

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

**Static safety is the first line of defense — before any test runs.** TypeScript's type system and Zod schema validation at boundaries (API inputs, external service responses, message payloads) catch a large class of bugs before code ever executes. A well-placed `z.parse()` at a boundary turns silent data corruption into a loud, localized error, often eliminating the need for a unit test that would have caught the same thing. Reach for stricter types and boundary validation before reaching for tests.

Above that static base, this follows Kent C. Dodds' [Testing Trophy](https://kentcdodds.com/blog/write-tests): integration tests are the sweet spot between confidence and cost. E2E tests are heavy but valuable; unit tests are cheap but tied to implementation details. Integration tests at the service/API level give the best return on investment.

**Start high, then fill in below:**

1. **Start with a high-level test** — either an E2E test (a vertical feature slice for backend work, or a browser interaction for frontend) or an integration test at the service level. Pick based on what the feature touches.
2. **E2E tests cover user flows** — generally one happy path and one unhappy path. Don't try to cover every branch at this level.
3. **Most coverage lives in integration tests** — the level below E2E. This is where branches, edge cases, and contract details get exercised.
4. **Unit tests are the exception, not the rule.** Write one only when one of the two triggers below applies.

**Why this ordering:** E2E tests give the most confidence but are slow and brittle. Unit tests are fast and free but easily drift into testing implementation rather than behavior. Integration tests sit in the middle — tied to business cases, cover a lot of ground per test, and survive refactors of internal structure.

**API/contract tests:** For backend-only work, API tests aren't expensive in this codebase. Lean into them — write more contract-level tests than you might in a heavier stack. **Playwright is being deprecated** for this project; don't reach for new Playwright tests, prefer API/integration tests instead.

**When to add a unit test — two triggers:**

1. **Reuse.** Module B has 2+ consumers (e.g., modules A and C both depend on it). At that point B sits at a shared interface, and its unit tests document the contract every caller relies on. Until that second consumer exists, B is covered transitively by A's tests; a unit test on B would be documentation for an audience of one.
2. **Internal complexity that's hard to localize from above.** A unit has internal complexity that an integration test can't cheaply diagnose when it breaks. Signals: 3+ internal branches producing categorically different outputs, pure transformations where wrong output doesn't throw (silent failure), or N fixtures needed to exercise N branches from a level above. In these cases an integration failure tells you "something is wrong" without telling you which branch — the unit test pays for itself in diagnostic speed.

Treat tests as documentation of a module's API. The reuse trigger says "wait for a second reader before writing documentation"; the complexity trigger says "write documentation when the code is hard enough that future-you will struggle to read it without help."

**Disciplines when you do write a unit test:**

- **Scope it to the gnarly part, not the whole module.** If a service has one complex method and ten boring ones, only the complex one gets a unit test. The rest stays covered by integration.
- **Prefer loud failures over unit tests.** A typed error, a Zod `.parse()` at a boundary, or an exhaustive switch will often pin down the source of an integration failure better than a unit test does — and won't ossify the module's internal shape. Reach for these first.
- **Delete the unit test when its trigger goes away.** If a second consumer is removed, or the complexity that justified the test was refactored away, the test is no longer documentation of anything — it's overhead.

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
- 2026-05-06: Rebuilt extract-session-templates skill from scratch (lost in laptop migration) using TDD. 77 tests, stdlib-only Python 3. Key session format facts: `file-history-snapshot` has no top-level timestamp (use `snapshot.timestamp`); subagent sessions have `isSidechain: true`, no `promptId`; delegation tool is `"Agent"` not `"Task"`. Featurize ran cleanly against 627 real session files. Skill lives at `dot_claude/skills/extract-session-templates/` in chezmoi dotfiles repo.
- 2026-05-06: Rebuilt records.py (Phase 2 of generate-mock-sessions skill). Pure record-building primitives with all schema-realism fixes (F1–F10, R1–R5): base62 IDs, v4 UUID fix, thinking signatures, full usage shape, event-driven hooks, sidechain-aware fields, agent_progress stripping, delegation ID consistency, None-safe parentUuid, tool-result cleanup. 52 tests, all passing. User provides exhaustive specs with exact API surfaces and named fixes — no design decisions needed from Claude on these rebuild tasks.
- 2026-05-06: Built validate.py (Phase 3 of generate-mock-sessions skill). Structural validator enforcing V1–V5 rules. Key real-file discoveries that required spec deviations: (1) ~40% of real files have non-monotonic timestamps — dropped strict ordering check, validate parsability only; (2) file-history-snapshot.messageId anchors to both user AND assistant uuids, not just user; (3) 2/632 non-sidechain files have orphan tool_result records (session resumption from previous file) — these are valid. T1 real-file roundtrip passed after these adjustments. 25 validate tests + 52 records tests = 77 total.
- 2026-05-06: Built scaffolder.py (Phase 4 of generate-mock-sessions skill). CLI + skeleton/assemble/checkpoint orchestration. 35 new tests, 112 total. Key bugs fixed: F2 two-pass UUID pre-allocation for file_snapshot anchors; F3 FIFO tool-use queue (not single last_id); F4 recursive usage recompute into agent_progress inner records; F6 stable delegation_msg_id across all agent_progress wrappers; F11 first-user parentUuid=None even after hook; F12 path-traversal guards at all 3 sinks; F13 atomic checkpoint via os.replace + corrupt-file recovery. Implementation note: _expand_subagent_event must PEEK (not pop) the parent pending_tool_use_ids — the subsequent tool_result in the parent template must consume it. Note: secrets._b62 IDs bypass random.seed(), so exact hash reproducibility is impossible; T3 golden snapshot tests seeded fields (UUIDs, timestamps, types) instead.
- 2026-05-22 → 2026-05-27: Multi-session test-rename pass across Assignment project. Renamed ~500 test cases across 30+ files (integration, services, adapters, kafka, gateway, utils, components, demo) to a consistent "given X, Y" / "Xs Y" spec voice. Workflow and migrations layers intentionally skipped. Convention established: no `should X` prefix, full word `acknowledgement` (never `ack`), users are "members of" folders (never "owners"), Assigned/Unassigned/Completed in TitleCase. Established workflow: detail-then-approve per-block with markdown tables (Current | Proposed | Change columns). User pushed back when names were stale/inaccurate vs body assertions — added several feedback memories (research-before-renaming, full-cycle-test-names, table-format-for-renames). Bonus: deleted 5 trivial pass-through tests from NotificationGateway.spec.ts per "tests above adapter" philosophy. Resolved one merge conflict in TaskService.spec.ts where upstream restructured the Review-manual-assignment tests.
