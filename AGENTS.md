# AGENTS.md

This is the PackWeave registry — the community pack store for the [weave](https://github.com/PackWeave/weave) CLI tool.

## What lives here

- `src/{name}/` — pack source files. **This is the only directory contributors touch.**
- `packs/{name}.json` — generated per-pack metadata (do not edit manually)
- `index.json` — generated search catalog (do not edit manually)
- `scripts/generate.py` — the generation script run by CI

## How to contribute a pack

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide. Short version:

1. Run `weave init your-pack-name` to scaffold, or copy `TEMPLATE/` to `src/your-pack-name/`
2. Edit `src/your-pack-name/pack.toml` — must have a `[pack]` section header
3. Test locally: `weave install ./src/your-pack-name`
4. Open a PR — CI regenerates `packs/` and `index.json` automatically on merge

## Key rules

- Never edit `packs/` or `index.json` directly — they are generated
- Pack names: lowercase, digits, hyphens only (`my-pack`, not `MyPack`)
- Server names must be globally unique across all installed packs
- Never store secret values — use `[servers.env.KEY]` declarations only
- Transport is `"stdio"` or `"http"`, not `"sse"`

## Registry protocol

The weave client uses a two-tier sparse index. See [`docs/REGISTRY.md`](https://github.com/PackWeave/weave/blob/main/docs/REGISTRY.md) in the weave repo for the full spec.
