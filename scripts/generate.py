#!/usr/bin/env python3
"""
Regenerate packs/*.json and index.json from src/.

Run from the repository root:
    python3 scripts/generate.py

For each pack under src/{name}/, this script:
  1. Reads all files and builds an inline `files` map (relative path → content).
  2. Parses pack.toml to extract metadata (version, description, authors, etc.).
  3. Writes packs/{name}.json — creating it or updating the version entry in place.

Then regenerates index.json as a flat catalog of all packs with latest_version
set to the highest semver version present in each packs/{name}.json.
"""

import json
import os
import re
import sys
from pathlib import Path


def parse_pack_toml(text: str) -> dict:
    """Extract scalar fields from the [pack] section of a pack.toml.

    Uses simple regex — a full TOML parser is not needed here because pack.toml
    fields are always plain strings, booleans, or inline arrays.
    """
    # Find the [pack] section (everything up to the next [] section or EOF)
    pack_section_match = re.search(
        r"^\[pack\](.*?)(?=^\[[^\[]|\Z)", text, re.DOTALL | re.MULTILINE
    )
    if not pack_section_match:
        raise ValueError("No [pack] section found in pack.toml")
    section = pack_section_match.group(1)

    def get(key: str):
        m = re.search(rf'^{key}\s*=\s*"([^"]*)"', section, re.MULTILINE)
        return m.group(1) if m else None

    def get_array(key: str) -> list[str]:
        m = re.search(rf"^{key}\s*=\s*\[([^\]]*)\]", section, re.MULTILINE)
        if not m:
            return []
        return [v.strip().strip('"') for v in m.group(1).split(",") if v.strip().strip('"')]

    return {
        "name": get("name"),
        "version": get("version"),
        "description": get("description"),
        "authors": get_array("authors"),
        "license": get("license"),
        "repository": get("repository"),
        "keywords": get_array("keywords"),
    }


def semver_key(version_str: str) -> tuple[int, ...]:
    """Return a sortable tuple for semver comparison."""
    try:
        return tuple(int(x) for x in version_str.split("."))
    except ValueError:
        return (0, 0, 0)


def build_files_map(pack_src_dir: Path) -> dict[str, str]:
    """Walk src/{name}/ and return a flat map of relative-path → file content."""
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

    meta = parse_pack_toml(pack_toml_path.read_text(encoding="utf-8"))
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
        # Replace or insert the version entry for the current version
        versions = [v for v in existing.get("versions", []) if v["version"] != version]
        versions.append(new_release)
    else:
        versions = [new_release]

    # Sort versions descending so latest is first
    versions.sort(key=lambda v: semver_key(v["version"]), reverse=True)

    pack_metadata = {
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
    print(f"  {pack_name} → {version} (latest: {latest})")

    return {
        "name": pack_metadata["name"],
        "description": pack_metadata["description"],
        "keywords": pack_metadata["keywords"],
        "latest_version": latest,
    }


def regenerate_index(packs_dir: Path) -> dict:
    """Build index.json from all packs/*.json files."""
    index: dict[str, dict] = {}
    for pack_json in sorted(packs_dir.glob("*.json")):
        with open(pack_json, encoding="utf-8") as f:
            meta = json.load(f)
        name = pack_json.stem
        versions = meta.get("versions", [])
        if not versions:
            continue
        latest = max(versions, key=lambda v: semver_key(v["version"]))["version"]
        index[name] = {
            "name": meta.get("name", name),
            "description": meta.get("description", ""),
            "keywords": meta.get("keywords", []),
            "latest_version": latest,
        }
    return index


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
    print(f"  index.json — {len(index)} pack(s)")
    print("\nDone.")


if __name__ == "__main__":
    main()
