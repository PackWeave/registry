# PackWeave Registry

The official pack registry index for [weave](https://github.com/PackWeave/weave).

## Format

`index.json` is a flat JSON object mapping pack names to their metadata. The schema mirrors the `RegistryIndex` struct in [`src/core/registry.rs`](https://github.com/PackWeave/weave/blob/main/src/core/registry.rs).

```json
{
  "<pack-name>": {
    "name": "<pack-name>",
    "description": "Human-readable description",
    "authors": ["author"],
    "license": "MIT",
    "repository": "https://github.com/...",
    "versions": [
      {
        "version": "0.1.0",
        "url": "https://github.com/.../releases/download/.../pack-0.1.0.tar.gz",
        "sha256": "<64-char hex>",
        "size_bytes": 12345
      }
    ]
  }
}
```

## Seed packs

| Pack | Description |
|------|-------------|
| `web-dev` | Browser automation, HTML/CSS tools, and HTTP inspection |
| `rust-dev` | cargo integration, crates.io search, and compiler error explanations |
| `python-dev` | Package management, virtual environments, and debugging tools |
| `git-tools` | Branch management, commit message generation, and conflict resolution |
| `docs-writer` | README generation, API docs, and changelog formatting |

> **Note:** The v0.1.0 entries above are placeholders. Archive URLs and sha256 hashes will be updated when real pack archives are published.

## Contributing a pack

Open an issue or PR with your pack's metadata. Packs must include a publicly accessible `tar.gz` archive and a valid SHA256 checksum.
