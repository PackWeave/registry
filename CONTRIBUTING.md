# Contributing a Pack

Thank you for contributing to the PackWeave registry. This guide covers everything you need to submit a new pack.

## What is a Pack?

A pack is a versioned bundle that can include:
- **MCP servers** — configured and applied to each CLI's config file
- **System prompts** — appended to the CLI's global instruction file
- **Slash commands** — installed into the CLI's command directory

## Quick Start

1. Copy `TEMPLATE/` to `src/your-pack-name/`
2. Fill in `pack.toml` with your pack's metadata and configuration
3. Add any prompt files under `prompts/` and command files under `commands/`
4. Open a PR — a maintainer will review, build the tarball, and publish it

## Pack Manifest Format

`pack.toml` must start with a `[pack]` section header:

```toml
[pack]
name = "your-pack-name"
version = "0.1.0"
description = "One-sentence description"
authors = ["Your Name <you@example.com>"]
license = "MIT"
repository = "https://github.com/you/your-pack"
keywords = ["keyword1", "keyword2"]
```

### MCP Servers

```toml
[[servers]]
name = "server-name"           # Must be unique across all installed packs
command = "npx"                # Executable (stdio transport)
args = ["-y", "@org/pkg@latest"]
transport = "stdio"            # "stdio" or "sse"
tools = ["tool1", "tool2"]     # Optional: expose only a subset of tools

# For HTTP/SSE transport, use url instead of command/args:
# url = "https://your-server.example.com/mcp"
# headers = { Authorization = "Bearer ${API_KEY}" }

# Declare required environment variables (never store values here)
[servers.env.API_KEY]
required = true
secret = true
description = "Your API key — get one at https://example.com"
```

### Targeting Specific CLIs

By default, a pack targets all supported CLIs. To restrict:

```toml
[targets]
claude_code = true
gemini_cli = false
codex_cli = false
```

### CLI-Specific Settings

```toml
[extensions.claude_code]
# Any valid Claude Code settings JSON — merged non-destructively into ~/.claude/settings.json
```

## File Layout

```
src/your-pack-name/
  pack.toml               # Required — the manifest
  prompts/
    claude.md             # Optional — Claude Code / Gemini CLI system prompt addition
  commands/
    command-name.md       # Optional — slash command (one file per command)
```

## Naming Rules

- Pack names: lowercase letters, digits, hyphens only (e.g. `my-pack`, `brave-search`)
- Server names: same rules, must be globally unique across all installed packs
- Command names: same rules

## Review Criteria

PRs are accepted when the pack:
- Has a valid `pack.toml` with a `[pack]` header
- Targets well-known, publicly available MCP servers or adds useful prompts/commands
- Does not conflict with existing pack server names
- Includes a clear description and appropriate keywords

## Pack Versioning

Use [semver](https://semver.org). Bump `version` in `pack.toml` for each change. A maintainer will create new release artifacts and update `packs/{name}.json` with the new version entry.
