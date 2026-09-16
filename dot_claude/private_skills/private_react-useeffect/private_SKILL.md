---
name: react-useeffect
description: Use when writing or reviewing React code that involves useEffect, derived state, data fetching in components, or syncing state between parent and child. Lists the ten common useEffect anti-patterns and what to do instead.
---

# useEffect Anti-Patterns

Avoid using useEffect when you don't need one. See: <https://react.dev/learn/you-might-not-need-an-effect>

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
