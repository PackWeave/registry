# PackWeave Registry

The official pack registry for [weave](https://github.com/PackWeave/weave) — a CLI tool that manages MCP server configurations, slash commands, and system prompts across AI CLIs (Claude Code, Gemini CLI, Codex CLI).

## Available Packs

| Pack | Description |
|------|-------------|
| [brave-search](src/brave-search/pack.toml) | Web and local search via the Brave Search API through MCP |
| [docs-writer](src/docs-writer/pack.toml) | System prompt and slash commands for technical writing |
| [fetch](src/fetch/pack.toml) | HTTP fetch tool via MCP — retrieve web pages as markdown or raw text |
| [filesystem](src/filesystem/pack.toml) | Read and write local files via the MCP filesystem server |
| [git-tools](src/git-tools/pack.toml) | Git operations via MCP plus a structured code review slash command |
| [github](src/github/pack.toml) | GitHub repos, issues, pull requests, and code search via MCP |
| [memory](src/memory/pack.toml) | Persistent key-value memory store across sessions via MCP knowledge graph |
| [postgres](src/postgres/pack.toml) | PostgreSQL database query access via MCP |
| [python-dev](src/python-dev/pack.toml) | System prompt and slash commands for Python development |
| [rust-dev](src/rust-dev/pack.toml) | System prompt and slash commands for Rust development |
| [sequential-thinking](src/sequential-thinking/pack.toml) | Structured chain-of-thought reasoning via MCP |
| [sqlite](src/sqlite/pack.toml) | SQLite database access via MCP |
| [web-dev](src/web-dev/pack.toml) | Browser automation via Puppeteer MCP plus a web development system prompt |

## Installing Packs

```sh
# Install weave
cargo install packweave

# Install a pack (applies to all installed CLIs automatically)
weave install filesystem

# Search available packs
weave search mcp

# List installed packs
weave list

# See full usage
weave --help
```

## Repository Structure

```
index.json          Lightweight search catalog (name, description, latest version per pack)
packs/              Per-pack metadata — fetched on demand during install
  {name}.json       Full metadata: all versions with inline file content
src/                Pack source files — the only files contributors need to touch
  {name}/
    pack.toml       Pack manifest in canonical [pack] format
    prompts/        System prompt and CLI-specific instruction files
    commands/       Slash command definitions (.md files)
    skills/         Skill files for Codex CLI (.md files)
    settings/       CLI-specific settings fragments (.json / .toml)
scripts/
  generate.py       Regenerates packs/*.json and index.json from src/
TEMPLATE/           Starter template for contributors
```

A GitHub Actions workflow automatically regenerates `packs/{name}.json` and `index.json`
from `src/` on every merge to main. **Contributors only ever touch files under `src/`.**

## Registry Protocol

The weave client uses a two-tier sparse index so clients never download more than they need:

1. **`index.json`** — a lightweight catalog fetched once for `weave search` and `weave list`.
   Contains only pack names, descriptions, and latest versions. Never contains version history
   or file content.

2. **`packs/{name}.json`** — full pack metadata fetched on demand only when installing or
   updating that specific pack. Contains all versions with their complete file content embedded
   inline as a flat map of relative path → file content. No tarballs, no release artifacts,
   no SHA256 ceremony.

This design keeps `weave install` fast regardless of how many packs the registry contains.

See [`docs/REGISTRY.md`](https://github.com/PackWeave/weave/blob/main/docs/REGISTRY.md) in the weave repo for the full protocol specification and JSON schemas.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
