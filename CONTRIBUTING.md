# 🤝 Contributing a Pack

Thank you for contributing to the PackWeave registry. This guide covers everything you need to submit a new pack.

## 📦 What is a Pack?

A pack is a versioned bundle that can include:
- **MCP servers** — configured and applied to each CLI's config file
- **System prompts** — appended to the CLI's global instruction file
- **Slash commands** — installed into the CLI's command directory

## ⚡ Quick Start

1. Run `weave init your-pack-name` to scaffold the directory structure, or copy `TEMPLATE/` to `src/your-pack-name/` manually
2. Fill in `pack.toml` with your pack's metadata and configuration
3. Add any prompt files under `prompts/`, command files under `commands/`, and settings fragments under `settings/`
4. Test locally: `weave install ./src/your-pack-name`
5. Open a PR — a maintainer reviews and merges; CI auto-publishes the pack

You never need to touch `packs/` or `index.json` directly. A GitHub Actions workflow
regenerates those files automatically on every merge to main.

## 🔧 Pack Manifest Format

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

### 🔌 MCP Servers

```toml
[[servers]]
name = "server-name"           # Must be unique across all installed packs
command = "npx"                # Executable (stdio transport)
args = ["-y", "@org/pkg@latest"]
transport = "stdio"            # "stdio" or "http"
tools = ["tool1", "tool2"]     # Optional: expose only a subset of tools

# For HTTP transport, use url instead of command/args:
# url = "https://your-server.example.com/mcp"
# headers = { Authorization = "Bearer ${API_KEY}" }

# Declare required environment variables (never store values here)
[servers.env.API_KEY]
required = true
secret = true
description = "Your API key — get one at https://example.com"
```

### 🖥️ Targeting Specific CLIs

By default, a pack targets all supported CLIs. To restrict:

```toml
[targets]
claude_code = true
gemini_cli = false
codex_cli = false
```

### ⚙️ CLI-Specific Settings

```toml
[extensions.claude_code]
# Any valid Claude Code settings JSON — merged non-destructively into ~/.claude/settings.json
```

## 📁 File Layout

```
src/your-pack-name/
  pack.toml               # Required — the manifest
  prompts/
    system.md             # Optional — used as fallback for all CLIs
    claude.md             # Optional — Claude Code / Gemini CLI-specific prompt addition
    gemini.md             # Optional — Gemini CLI-specific prompt addition
    codex.md              # Optional — Codex CLI-specific prompt addition
  commands/
    command-name.md       # Optional — Claude Code slash command (one file per command)
  skills/
    skill-name.md         # Optional — Codex CLI skill (one file per skill)
  settings/
    claude.json           # Optional — merged into ~/.claude/settings.json
    gemini.json           # Optional — merged into ~/.gemini/settings.json
    codex.toml            # Optional — merged into ~/.codex/config.toml
```

All content is plain text (TOML, JSON, Markdown) — no binaries. MCP server code lives on npm,
PyPI, or GitHub and is fetched at runtime by the CLI; this registry only distributes the
configuration that points at it.

## 🏷️ Naming Rules

- Pack names: lowercase letters, digits, hyphens only (e.g. `my-pack`, `brave-search`)
- Server names: same rules, must be globally unique across all installed packs
- Command names: same rules

## ✅ Review Criteria

PRs are accepted when the pack:
- Has a valid `pack.toml` with a `[pack]` header
- Targets well-known, publicly available MCP servers or adds useful prompts/commands
- Does not conflict with existing pack server names
- Includes a clear description and appropriate keywords

## 🔖 Pack Versioning

Use [semver](https://semver.org). Bump `version` in `pack.toml` for each change.
CI will pick up the new version automatically on merge and add it to `packs/{name}.json`.

## 🚀 How Publishing Works

When a PR is merged to main:

1. The `publish` GitHub Actions workflow runs `scripts/generate.py`
2. The script reads all files from `src/{name}/` and embeds them inline in `packs/{name}.json`
   as a flat map of relative path → file content
3. It also updates `index.json` with the latest version for each pack
4. The workflow commits the generated files back to main

The weave client fetches `packs/{name}.json` on demand during `weave install` and writes the
embedded files directly to `~/.packweave/packs/{name}/{version}/` — no tarballs, no downloads
beyond the single JSON fetch.
