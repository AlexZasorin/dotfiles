---
name: pnpm-audit-fix
description: Use when running security audits on pnpm monorepos to find and fix vulnerabilities in dependencies at a user-specified severity threshold
---

# pnpm Audit Fix

## Overview
Systematically resolve vulnerabilities in pnpm monorepos through dependency updates, with compilation and test verification after each change. Severity scope is chosen by the user — not assumed.

## Workflow

### 1. Initial Audit
Run `pnpm audit` and summarize the counts by severity (critical / high / moderate / low / info).

Then **ask the user which severities to address** before doing any work. Do not assume a default. Offer concrete options based on what was found, e.g.:
- A specific severity only (e.g. just critical)
- A severity and above (e.g. high and above, moderate and above)
- All vulnerabilities
- A specific subset of advisories by name

Only proceed to step 2 after the user confirms scope. Apply the rest of the workflow only to vulnerabilities in the chosen scope.

### 2. For Each Vulnerability

**a) Try `pnpm update -r` walking down the dependency chain**
For a vulnerability path like `A > B > C` (where C is vulnerable), try each level in order:
1. `pnpm update -r A` — re-audit
2. If still vulnerable: `pnpm update -r B` — re-audit
3. If still vulnerable: `pnpm update -r C` — re-audit

**b) Verify after each dependency change**
- Run the project's compile command
- Run the project's isolated/unit test command
- If either fails, **stop and report the failure to the user** before continuing

**c) If `pnpm update -r` doesn't resolve it, check package.json files**
- Find the dependency in package.json files
- If the version string lacks a `^` prefix, manually update to the earliest fixed version listed in the audit output
- Run `pnpm install`, then repeat from (b)

**d) If still not resolved, use overrides**
- Add the dependency with its fix version to `pnpm.overrides` in the root package.json
- Add to the existing overrides section — do not replace it
- Run `pnpm install`, then repeat from (b)

### 3. Cleanup Overrides
Once `pnpm audit` is clean, review the `pnpm.overrides` section and simplify:

**a) Collapse redundant overrides for the same package**
- If multiple overrides target overlapping ranges of the same package, merge into one. Example:
  - `"js-yaml@>=4.0.0 <4.1.1": ">=4.1.1"` and `"js-yaml@<3.14.2": ">=3.14.2"` stay separate (different major lines).
  - `"qs@<6.14.2": ">=6.14.2"` and `"qs@<6.14.1": ">=6.14.1"` collapse to just `"qs@<6.14.2": ">=6.14.2"`.

**b) Simplify overly specific version predicates**
- If an override specifies a narrow range (e.g. `yaml@>=2.0.0 <2.8.3`) but no other major version of that package exists in the tree, drop the lower bound: `"yaml@<2.8.3": ">=2.8.3"`. Verify with `pnpm why <pkg>` that no other major version is present before simplifying.
- Prefer the simplest form that expresses "upgrade anything below the fixed version."

**c) Dedupe with pre-existing overrides**
- If the new override duplicates or is subsumed by an existing one, remove the redundant entry.

**d) Verify after cleanup**
- Run `pnpm install` to regenerate the lockfile.
- Re-run `pnpm audit` to confirm still clean.
- Run compile and isolated tests again.

### 4. Completion
After cleanup passes verification:
- Report the final `pnpm audit` summary
- Ask the user to set up server/docker dependencies to run full verification (`pnpm verify` or equivalent)

## Rules
- Always use `pnpm`, never `npm`
- Only modify package.json files and the lockfile — never source code
- Always run `pnpm install` after manual package.json edits before re-auditing
