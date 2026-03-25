#!/usr/bin/env python3
"""
Regenerate packs/*.json and index.json from src/.

Run from the repository root:
    python3 scripts/generate.py

For each pack under src/{name}/, this script:
  1. Reads all files and builds an inline `files` map (relative path -> content).
  2. Parses pack.toml to extract metadata (version, description, authors, etc.).
  3. Writes packs/{name}.json — creating it or updating the version entry in place.

Then regenerates index.json as a flat catalog of all packs with latest_version
set to the highest semver version present in each packs/{name}.json.
"""

import json
import sys
import tomllib
from pathlib import Path

# Schema version for all generated registry files (index.json, packs/*.json).
# Bump this when the registry format changes in a way that older clients cannot
# safely ignore.  Clients compare this against their own supported version and
# surface a clear "please upgrade weave" error when the registry is newer.
REGISTRY_SCHEMA_VERSION = 1


def parse_pack_toml(pack_toml_path: Path) -> dict:
    """Parse a pack.toml file and extract metadata from the [pack] section."""
    with open(pack_toml_path, "rb") as f:
        data = tomllib.load(f)

    if "pack" not in data:
        raise ValueError("No [pack] section found in pack.toml")

    pack = data["pack"]
    return {
        "name": pack.get("name"),
        "version": pack.get("version"),
        "description": pack.get("description"),
        "authors": pack.get("authors", []),
        "license": pack.get("license"),
        "repository": pack.get("repository"),
        "keywords": pack.get("keywords", []),
    }


def semver_key(version_str: str) -> tuple[int, ...]:
    """Return a sortable tuple for semver comparison."""
    try:
        return tuple(int(x) for x in version_str.split("."))
    except ValueError:
        return (0, 0, 0)


def build_files_map(pack_src_dir: Path) -> dict[str, str]:
    """Walk src/{name}/ and return a flat map of relative-path -> file content."""
    files: dict[str, str] = {}
    for file_path in sorted(pack_src_dir.rglob("*")):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(pack_src_dir).as_posix()
        files[rel] = file_path.read_text(encoding="utf-8")
    return files


def process_pack(src_dir: Path, packs_dir: Path, pack_name: str) -> dict:
    """Regenerate packs/{name}.json for one pack. Returns the index entry."""
    pack_src = src_dir / pack_name
    pack_toml_path = pack_src / "pack.toml"
    if not pack_toml_path.exists():
        print(f"  SKIP {pack_name}: no pack.toml found", file=sys.stderr)
        return {}

    meta = parse_pack_toml(pack_toml_path)

    # Ensure pack.toml name matches the directory name to prevent registry inconsistencies.
    if meta["name"] and meta["name"] != pack_name:
        print(
            f"  SKIP {pack_name}: pack.toml name '{meta['name']}' does not match directory name",
            file=sys.stderr,
        )
        return {}

    version = meta["version"]
    if not version:
        print(f"  SKIP {pack_name}: version not found in pack.toml", file=sys.stderr)
        return {}

    files_map = build_files_map(pack_src)

    new_release = {
        "version": version,
        "files": files_map,
        "dependencies": {},
    }

    pack_json_path = packs_dir / f"{pack_name}.json"

    # Load existing pack metadata (preserves older versions)
    if pack_json_path.exists():
        with open(pack_json_path, encoding="utf-8") as f:
            existing = json.load(f)

        # Version immutability: refuse to change the content of an already-published
        # version. A different files map means the pack author forgot to bump the
        # version in pack.toml.
        existing_by_version = {v["version"]: v for v in existing.get("versions", [])}
        if version in existing_by_version:
            old_files = existing_by_version[version].get("files", {})
            if old_files != files_map:
                print(
                    f"Error: {pack_name} version {version} is already published with "
                    f"different content. Bump the version in pack.toml.",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Replace or insert the version entry for the current version
        versions = [v for v in existing.get("versions", []) if v["version"] != version]
        versions.append(new_release)
    else:
        versions = [new_release]

    # Sort versions descending so latest is first
    versions.sort(key=lambda v: semver_key(v["version"]), reverse=True)

    pack_metadata = {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "name": meta["name"] or pack_name,
        "description": meta["description"] or "",
        "authors": meta["authors"],
        "license": meta["license"],
        "repository": meta["repository"],
        "keywords": meta["keywords"],
        "versions": versions,
    }

    with open(pack_json_path, "w", encoding="utf-8") as f:
        json.dump(pack_metadata, f, indent=2, ensure_ascii=False)
        f.write("\n")

    latest = max(versions, key=lambda v: semver_key(v["version"]))["version"]
    print(f"  {pack_name} -> {version} (latest: {latest})")

    return {
        "name": pack_metadata["name"],
        "description": pack_metadata["description"],
        "keywords": pack_metadata["keywords"],
        "latest_version": latest,
    }


def regenerate_index(packs_dir: Path) -> dict:
    """Build index.json from all packs/*.json files.

    Returns the full envelope: ``{"schema_version": N, "packs": {…}}``.
    """
    packs: dict[str, dict] = {}
    for pack_json in sorted(packs_dir.glob("*.json")):
        with open(pack_json, encoding="utf-8") as f:
            meta = json.load(f)
        name = pack_json.stem
        versions = meta.get("versions", [])
        if not versions:
            continue
        latest = max(versions, key=lambda v: semver_key(v["version"]))["version"]
        packs[name] = {
            "name": meta.get("name", name),
            "description": meta.get("description", ""),
            "keywords": meta.get("keywords", []),
            "latest_version": latest,
        }
    return {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "packs": packs,
    }


def main() -> None:
    repo_root = Path(__file__).parent.parent
    src_dir = repo_root / "src"
    packs_dir = repo_root / "packs"
    index_path = repo_root / "index.json"

    packs_dir.mkdir(exist_ok=True)

    pack_names = sorted(
        p.name for p in src_dir.iterdir() if p.is_dir() and (p / "pack.toml").exists()
    )

    print(f"Processing {len(pack_names)} pack(s):")
    for name in pack_names:
        process_pack(src_dir, packs_dir, name)

    print("\nRegenerating index.json ...")
    index = regenerate_index(packs_dir)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  index.json — {len(index['packs'])} pack(s), schema_version={index['schema_version']}")
    print("\nDone.")


if __name__ == "__main__":
    main()
