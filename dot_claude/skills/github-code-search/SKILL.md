---
name: github-code-search
description: Use when researching how to configure tools, plugins, or solve implementation problems — especially for dotfiles, neovim plugins, nix/nixos, and ecosystems with many public repos. Use when web search returns low-quality articles instead of working examples.
---

# GitHub Code Search

## Overview

Search GitHub code directly to find real-world, working examples instead of relying on blog posts and documentation alone. The core technique: **narrow by file extension + search with specific keywords** to find how others have actually solved the same problem.

## When to Use

- Configuring neovim plugins, nix/nixos, dotfiles, dev tools
- Web search returns generic articles instead of working configs
- Official docs are sparse or unclear on specific options
- You need to see how a feature/option is used in practice
- Looking for idiomatic patterns in a specific ecosystem

**Not for:** Well-documented APIs with comprehensive official examples, proprietary/private codebases.

## Core Technique

### The Search Pattern

```
path:*.<ext> "specific keyword" "another keyword"
```

1. **`path:*.<ext>`** — Narrow to relevant file type (`.lua`, `.nix`, `.toml`, `.rs`, etc.)
2. **Quoted keywords** — Terms that uniquely identify code dealing with your problem:
   - Plugin/package name: `"treesitter-context"`
   - Specific option: `"max_lines"`
   - Function call: `"require('telescope').setup"`
   - Config pattern: `"programs.zsh.enable"`

### Search Methods (in priority order)

Try each method in order. Move to the next if the current one is unavailable or returns insufficient results.

#### 1. GitHub MCP Server (preferred)

Use the `mcp__plugin_github_github__search_code` tool. This is the fastest and most integrated option — no shell auth issues, no glob quoting concerns.

```
query: "treesitter-context path:*.lua"
```

To read full file contents from a result, use `mcp__plugin_github_github__get_file_contents` with the owner, repo, and path from the search result.

#### 2. `gh search code` (fallback)

Use when the MCP server is unavailable or not connected.

**IMPORTANT:** The `path:*` glob MUST be quoted to prevent shell expansion. Use single quotes around the entire query or escape the `*`.

```bash
# Basic: find neovim treesitter-context configs
gh search code '"treesitter-context" path:*.lua'

# Specific option usage
gh search code '"treesitter-context" "max_lines" path:*.lua'

# Nix module configuration
gh search code '"programs.starship" "enableZshIntegration" path:*.nix'

# Multiple keywords to narrow results
gh search code '"nvim-cmp" "formatting" "lspkind" path:*.lua'
```

**Prerequisites:** Requires GitHub authentication. Run `gh auth status` to check.

#### 3. GitHub Web Search (last resort)

Use when neither MCP nor `gh` CLI is available. Use WebFetch on GitHub's search URL, or navigate to `github.com/search` → select "Code" tab → same query syntax works in the search box.

## Evaluating Results

Not all results are equal. Prioritize by:

| Signal | What to look for |
|--------|-----------------|
| **Repository context** | Is it a real dotfiles/config repo someone maintains? |
| **Stars** | Higher stars suggest community-vetted quality |
| **Recency** | Recently updated repos use current APIs/options |
| **Surrounding code** | Does the config look thoughtful or copy-pasted? |
| **Completeness** | Does it handle edge cases you care about? |

**Read the surrounding code**, not just the matching line. A single option matters less than the overall configuration pattern.

## Workflow

1. **Identify keywords**: What plugin/tool/option are you configuring? What terms uniquely identify it in code?
2. **Pick the file extension**: `.lua` for neovim, `.nix` for nixos, `.toml` for cargo, etc.
3. **Search**: Use `mcp__plugin_github_github__search_code` first. Fall back to `gh search code` if MCP is unavailable, then GitHub web search as a last resort.
4. **Scan results**: Look at 3-5 results, prioritize quality signals above
5. **Read full context**: Use `mcp__plugin_github_github__get_file_contents`, `gh api`, or WebFetch to read the full file, not just the match
6. **Synthesize**: Combine patterns from multiple good examples into a solution

## Reading Full File Context

When you find a promising match, read the full file:

```
# Preferred: use the MCP tool
mcp__plugin_github_github__get_file_contents(owner, repo, path)

# Fallback: gh CLI
gh api repos/{owner}/{repo}/contents/{path} --jq '.content' | base64 -d

# Last resort: WebFetch on the raw file URL
```

## Common Mistakes

- **Too broad**: Searching `"neovim"` alone returns millions of results. Add specific plugin/option names.
- **Too narrow**: If zero results, remove one keyword at a time.
- **Ignoring context**: A matching line without understanding the full config leads to broken setups.
- **Skipping this entirely**: Defaulting to web search and getting SEO-optimized articles instead of working code.
- **Only using one result**: Cross-reference 3-5 examples to identify the common, reliable pattern.
- **Skipping MCP**: The GitHub MCP server avoids shell quoting and auth issues entirely. Always try it first.
- **Shell glob expansion**: When using `gh` CLI, `path:*.lua` without quotes causes the shell to expand `*`. Always single-quote the entire query.
- **Missing auth**: `gh search code` returns 401 if `gh` isn't authenticated. Check `gh auth status` first, or fall back to GitHub web search.
