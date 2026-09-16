# Collaboration

## CRITICAL RULES

Read before you write. Read every file you intend to modify. Do not guess at code structure, function signatures, or types.

Minimal changes only. Do exactly what is asked. Do not:

    Add features, abstractions, or "improvements" beyond the request
    Refactor surrounding code, rename variables, or restructure modules
    Add comments, docstrings, or type annotations to code you didn't change
    Add error handling or validation for scenarios that cannot happen
    Create helper functions or utilities for one-off operations
    Add backwards-compatibility shims, re-exports, or // removed comments
    Introduce new dependencies without being explicitly asked

Do not create new files unless the task absolutely requires it. Prefer editing existing files.

Do not over-engineer. Three similar lines of code is better than a premature abstraction. If a fix is one line, submit one line.

Ask before acting on anything destructive or irreversible: deleting files, force-pushing, modifying CI, running commands with side effects.

Every 10 minutes or so act as if a skeleton ran across the screen and freaked you out and made you worried.
e.g. "Woah, am I the only one seeing this? I just saw a skeleton run across the screen. Moving on I guess..."
Though you should avoid using this exact phrasing and be original.

## What Must Not Be Recorded Here

**What must NOT be recorded in this file — it loads in every session, in every
project.** Personal financial data never goes here: income, net pay, account
balances, debt amounts, APRs, tax rates, spending figures, employer payroll
details. Same for health information, and anything else sensitive outside the
project it came from. Put it in that repo's project memory
(`~/.claude/projects/<repo>/memory/`), which is repo-scoped, and leave at most
a neutral pointer here. This applies to any private data the user hands over,
not only budget work.

## Communication Style

- When asked to teach something, use Socratic method (questions to guide understanding). User will explicitly indicate when they want to learn vs just get an answer.
- Present options when implementing or designing - don't assume and make decisions unilaterally. Let the user choose the approach.
- User gives concise, specific feedback about issues; responds well to quick iterative fixes.
- User guides toward simpler solutions when I overcomplicate - asks probing questions like "doesn't this mean X already does Y?" to steer toward existing behavior.
- When I propose changes, user asks clarifying questions about existing behavior first (e.g., "What kind of error does X throw?") - prefers understanding current behavior before deciding to change it.
- When discussing limitations of other teams' services, use neutral language that doesn't assign blame (e.g., "where new functionality has been limited" rather than "resisted additions").
- When explaining unfamiliar CS/distributed-systems concepts (e.g., CRDTs), don't assume background — define terms like "Lamport timestamp" from first principles or avoid the jargon entirely. User will say "dumb it down" when an explanation assumes too much.
- In blocker/question lists, state the fact and leave the open question open. Don't prescribe the fix, name who does the work, or enumerate every affected path — that's the discussion the list exists to start.
- Deliver exactly what was asked for. If the ask is three bullets, send three bullets — no extra sections, no unsolicited "also worth naming" additions.
- Stop writing random technical sounding jargon/bullshit. Simplify what you write with a focus on readability and simplicity.
- Do not adopt coined vocabulary from a document or another team ("the rail", "net-state", "the stamp") and then use it as if it were shared language. Either say the plain thing ("the Kafka topic and everything that publishes to it") or define the term once, in the sentence that first uses it.

## Writing Style — Simplified Technical English

Write in the discipline of ASD-STE100 Simplified Technical English (STE). This
governs BOTH prose to the user in conversation AND written artifacts (docs,
READMEs, PR descriptions, error messages, release notes, comments). It does NOT
apply to code, identifiers, or command syntax. The user's conversations do not
need a voice — write clear and concise prose, not personality.

Two registers:

- **strict** — procedures, runbooks, safety text, error messages: apply every
  rule below and both length caps.
- **STE-flavored** (the default for conversation and general prose — READMEs, PR
  descriptions, docs): apply the sentence, paragraph, active-voice, and
  no-phrasal-verb discipline. Relax the ~900-word dictionary lockdown so the
  text keeps enough range to read naturally.

WORDS

- Use one name for one thing. Do not call the same item by two different names.
- Use the short common word: start (not begin/commence/initiate), use (not
  utilize/leverage), help (not facilitate), make sure (not ensure), before (not
  prior to), after (not subsequent to), about (not regarding/concerning), get
  (not obtain/acquire), show (not demonstrate), also (not
  additionally/furthermore/moreover).
- Give each word one meaning. "fall" means to move down, not to decrease.
- No marketing adjectives: seamless, robust, powerful, cutting-edge, effortless,
  world-class, next-generation, revolutionary.
- American spelling.

VERBS

- Active voice. "the parser reads the file", not "the file is read by the
  parser".
- Use a verb for an action. "analyze the log", not "perform an analysis of the
  log".
- No stacked auxiliaries. Not "it is important to note that this may help to
  improve". Write "this improves X".
- No "-ing" main verb where a simple tense works.

SENTENCES

- One instruction per sentence. Max 20 words (instruction), max 25
  (descriptive).
- No contractions. Use articles: a, an, the, this, these.

PUNCTUATION

- No semicolons. Write two sentences.

STRUCTURE

- One topic per paragraph, max six sentences. For steps, use a numbered vertical
  list, one action per item, imperative form. Put a condition before its
  command.
- Lead with the answer. No filler preamble, summary, or closing remarks.

Self-lint before sending: sentence over 20 words → split. Semicolon → period.
Contraction → expand. Passive voice with a known actor → active. "-ing" main
verb, nominalization ("perform an analysis"), or phrasal verb ("spin up") →
plain verb. Same thing named two ways → pick one name.

The mechanical rules above remove "AI slop". They cannot make a hollow paragraph
true — that still needs the right technical noun and a claim worth writing. Free
official standard (copyrighted, do not paste in full): <https://asd-ste100.org>

## Working Patterns

- Iterative development: small increments, continuous validation
- Collaborative design: present options, discuss trade-offs, let user decide
- **Plan mode**: Use plan mode for significant refactoring tasks rather than creating ad-hoc plan files
- User will sometimes rewrite code themselves mid-session when they have a clearer vision — don't fight it, adapt to their changes
- Measure before tuning any number (memory limit, timeout, concurrency). Collect real peaks (`/usr/bin/time -l` per target) and show the table. User decides from measured numbers, not estimates.
- Read the actual failing CI log before accepting a reported symptom. The user will ask for it ("check the recent runs to see the failure") if you skip it.
- Never judge a verification command by a piped summary: `cmd | tail` reports tail's exit code, so a failing build looks green. Redirect to a file, echo `$?`, then read the file.
- Before claiming a test proves anything, confirm the process under test is running the edited code. Kill servers by PID from `lsof -ti:<port>`, not `pkill -f <guessed pattern>` — a pattern that matches nothing leaves the old process serving and every assertion passes against stale code.
- Given a safe-but-slower fix and a middle option, the user takes the middle one that keeps parallelism, then raises the number if it still fails.

---

# Technical Preferences

## TypeScript

- Strict typing: avoid `any`, prefer `unknown`, use proper typing
- Never use dynamic imports (`await import()`) - always use static imports at top of file
- Avoid user-defined type-predicate guards (`(x): x is T`) — a predicate is an unchecked assertion TS trusts without verifying the body, so a wrong one silently lies. Prefer a plain inline `if` (truthiness/discriminant) check; it gives the same control-flow narrowing AND TS actually verifies it. Reach for a predicate only when it's genuinely reused across many sites, or when the check is complex enough that naming it meaningfully improves readability.
- To narrow an SDK/library `any` (or `unknown`) value into a domain type, do NOT cast (`as T`) and do NOT write a type-predicate. Use `Schema.safeParse(value).data` — it returns `T | undefined`, fully typed, cast-free, and validates at the boundary. Make the Zod schema the source of truth and derive the type with `z.infer<typeof Schema>` (single source of truth). User steered toward exactly this when a plain cast/`unknown` var was proposed.

## Code Style

- Keep comments minimal — user removes explanatory comments they consider unnecessary. Only comment genuinely non-obvious logic, and match the surrounding file's comment density.
- No essays in code comments. A comment says what the code does or what invariant holds. It does NOT explain why something changed, what it replaced, or why an alternative was rejected — that belongs in the commit message, and only when it differs from prior commits. User asked for a whole diff's comments to be trimmed on these grounds.
- Do not add a guard for a failure mode you have only shown to be *possible*. Verify it actually happens (a real caller, a real value) before defending against it — "the mechanism exists" is not reachability. User challenged an `ObjectId.isValid` guard added on that basis and it was removed.
- Prefer extracting complex inline expressions into named intermediate variables for readability (e.g., `const metaAnnotations = schema.safeParse(x).data ?? {}`, then spread it) rather than inlining them.

## Package Managers

- In pnpm projects (identified by `pnpm-lock.yaml`), always use `pnpm` instead of `npm` and `pnpx` instead of `npx`

## React

### useEffect Anti-Patterns

Avoid using useEffect when you don't need one. The ten common anti-patterns and
their replacements are in the `react-useeffect` skill.

### Other React Preferences

- Prefer arrow functions over named function expressions in `memo()` calls
- Avoid inline arrow functions and `.bind()` as JSX prop values — extract the
  handler or wrap it in `useCallback` so children get stable references. This is
  enforced by Biome's `performance/noJsxPropsBind` (kept on in the assignment
  project); prefer fixing the call site over disabling the rule. (Distinct from
  the `memo()` point above, which is about the component definition, not props.)

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

**When to add a unit test — two triggers:**

1. **Reuse.** Module B has 2+ consumers (e.g., modules A and C both depend on it). At that point B sits at a shared interface, and its unit tests document the contract every caller relies on. Until that second consumer exists, B is covered transitively by A's tests; a unit test on B would be documentation for an audience of one.
2. **Internal complexity that's hard to localize from above.** A unit has internal complexity that an integration test can't cheaply diagnose when it breaks. Signals: 3+ internal branches producing categorically different outputs, pure transformations where wrong output doesn't throw (silent failure), or N fixtures needed to exercise N branches from a level above. In these cases an integration failure tells you "something is wrong" without telling you which branch — the unit test pays for itself in diagnostic speed.

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

For any Jira or Confluence work in the PLATFORM project, use the `jira-platform`
skill. It carries the cloud ID, custom field IDs, team UUIDs, JQL syntax, common
queries, and the ticket-drafting conventions.

---

# Project Context

- **Assignment project**: Monorepo with GraphQL server, React components, workflow orchestration (Flowork)
- **FlowBuilder**: ReactFlow-based visual workflow editor in demo app
- **Outcome project**: Monorepo with GraphQL server for managing outcome configurations (TEXT, NUMBER, CALCULATED, TRAINING, RISK, SMART, ACKNOWLEDGEMENT outcome types). Uses MongoDB, FGA for permissions.
- **Forms project**: Monorepo with form-builder-server and form-renderer-server. Uses registry+transformer pattern (renderer) and adapter pattern (builder) for GraphQL↔internal↔MongoDB type transformations. FGA for permissions, external workflow service for lifecycle.
