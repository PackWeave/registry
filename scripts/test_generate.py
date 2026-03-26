"""Tests for generate.py — pack registry generation and validation."""

import json
import sys
from pathlib import Path

import pytest

# Ensure scripts/ is importable
sys.path.insert(0, str(Path(__file__).parent))

from generate import (
    build_files_map,
    parse_pack_toml,
    process_pack,
    regenerate_index,
    semver_key,
    validate_pack,
    validate_unique_server_names,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_PACK_TOML = """\
[pack]
name = "my-pack"
version = "0.1.0"
description = "A test pack"
authors = ["Test Author"]
license = "MIT"
repository = "https://github.com/test/test"
keywords = ["test", "example"]
"""

VALID_PACK_WITH_SERVER = """\
[pack]
name = "server-pack"
version = "1.0.0"
description = "A pack with a server"
authors = ["Test"]
license = "MIT"
keywords = ["mcp"]

[[servers]]
name = "my-server"
command = "npx"
args = ["-y", "@org/pkg@latest"]
transport = "stdio"
"""


def _write_pack(tmp_path: Path, name: str, toml_content: str) -> Path:
    """Create a pack directory with a pack.toml and return the pack dir."""
    pack_dir = tmp_path / name
    pack_dir.mkdir(parents=True)
    (pack_dir / "pack.toml").write_text(toml_content, encoding="utf-8")
    return pack_dir


# ---------------------------------------------------------------------------
# parse_pack_toml
# ---------------------------------------------------------------------------


class TestParsePackToml:
    def test_valid(self, tmp_path: Path):
        pack_dir = _write_pack(tmp_path, "my-pack", VALID_PACK_TOML)
        meta = parse_pack_toml(pack_dir / "pack.toml")
        assert meta["name"] == "my-pack"
        assert meta["version"] == "0.1.0"
        assert meta["description"] == "A test pack"
        assert meta["authors"] == ["Test Author"]
        assert meta["license"] == "MIT"
        assert meta["keywords"] == ["test", "example"]

    def test_missing_pack_section(self, tmp_path: Path):
        pack_dir = _write_pack(tmp_path, "bad", "[other]\nfoo = 1\n")
        with pytest.raises(ValueError, match="No \\[pack\\] section"):
            parse_pack_toml(pack_dir / "pack.toml")

    def test_missing_optional_fields(self, tmp_path: Path):
        minimal = '[pack]\nname = "x"\nversion = "0.1.0"\ndescription = "d"\n'
        pack_dir = _write_pack(tmp_path, "x", minimal)
        meta = parse_pack_toml(pack_dir / "pack.toml")
        assert meta["name"] == "x"
        assert meta["license"] is None
        assert meta["repository"] is None
        assert meta["authors"] == []
        assert meta["keywords"] == []


# ---------------------------------------------------------------------------
# semver_key
# ---------------------------------------------------------------------------


class TestSemverKey:
    def test_basic(self):
        assert semver_key("1.2.3") == (1, 2, 3)

    def test_sorting(self):
        versions = ["0.1.0", "1.0.0", "0.2.0", "0.1.1", "2.0.0"]
        sorted_versions = sorted(versions, key=semver_key, reverse=True)
        assert sorted_versions == ["2.0.0", "1.0.0", "0.2.0", "0.1.1", "0.1.0"]

    def test_invalid_fallback(self):
        assert semver_key("not-a-version") == (0, 0, 0)


# ---------------------------------------------------------------------------
# build_files_map
# ---------------------------------------------------------------------------


class TestBuildFilesMap:
    def test_basic(self, tmp_path: Path):
        pack_dir = tmp_path / "my-pack"
        pack_dir.mkdir()
        (pack_dir / "pack.toml").write_text("content", encoding="utf-8")
        prompts = pack_dir / "prompts"
        prompts.mkdir()
        (prompts / "claude.md").write_text("prompt", encoding="utf-8")

        files = build_files_map(pack_dir)
        assert "pack.toml" in files
        assert "prompts/claude.md" in files
        assert files["pack.toml"] == "content"
        assert files["prompts/claude.md"] == "prompt"

    def test_skips_directories(self, tmp_path: Path):
        pack_dir = tmp_path / "my-pack"
        pack_dir.mkdir()
        (pack_dir / "subdir").mkdir()
        (pack_dir / "file.txt").write_text("hi", encoding="utf-8")

        files = build_files_map(pack_dir)
        assert len(files) == 1
        assert "file.txt" in files


# ---------------------------------------------------------------------------
# validate_pack
# ---------------------------------------------------------------------------


class TestValidatePack:
    def test_valid_pack(self, tmp_path: Path):
        _write_pack(tmp_path, "my-pack", VALID_PACK_TOML)
        errors = validate_pack(tmp_path / "my-pack" / "pack.toml", "my-pack")
        assert errors == []

    def test_valid_pack_with_server(self, tmp_path: Path):
        _write_pack(tmp_path, "server-pack", VALID_PACK_WITH_SERVER)
        errors = validate_pack(tmp_path / "server-pack" / "pack.toml", "server-pack")
        assert errors == []

    def test_missing_required_field(self, tmp_path: Path):
        toml = '[pack]\nname = "x"\nversion = "0.1.0"\n'
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("description" in e for e in errors)

    def test_invalid_name_format(self, tmp_path: Path):
        toml = '[pack]\nname = "My_Pack"\nversion = "0.1.0"\ndescription = "d"\n'
        _write_pack(tmp_path, "My_Pack", toml)
        errors = validate_pack(tmp_path / "My_Pack" / "pack.toml", "My_Pack")
        assert any("invalid pack name" in e for e in errors)

    def test_trailing_hyphen_rejected(self, tmp_path: Path):
        toml = '[pack]\nname = "bad-"\nversion = "0.1.0"\ndescription = "d"\n'
        _write_pack(tmp_path, "bad-", toml)
        errors = validate_pack(tmp_path / "bad-" / "pack.toml", "bad-")
        assert any("invalid pack name" in e for e in errors)

    def test_name_dir_mismatch(self, tmp_path: Path):
        toml = '[pack]\nname = "foo"\nversion = "0.1.0"\ndescription = "d"\n'
        _write_pack(tmp_path, "bar", toml)
        errors = validate_pack(tmp_path / "bar" / "pack.toml", "bar")
        assert any("does not match directory" in e for e in errors)

    def test_invalid_version(self, tmp_path: Path):
        toml = '[pack]\nname = "x"\nversion = "abc"\ndescription = "d"\n'
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("invalid version" in e for e in errors)

    def test_keywords_not_list(self, tmp_path: Path):
        toml = '[pack]\nname = "x"\nversion = "0.1.0"\ndescription = "d"\nkeywords = "bad"\n'
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("keywords" in e and "list of strings" in e for e in errors)

    def test_server_missing_name(self, tmp_path: Path):
        toml = (
            '[pack]\nname = "x"\nversion = "0.1.0"\ndescription = "d"\n\n'
            '[[servers]]\ncommand = "npx"\ntransport = "stdio"\n'
        )
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("missing 'name'" in e for e in errors)

    def test_server_invalid_transport(self, tmp_path: Path):
        toml = (
            '[pack]\nname = "x"\nversion = "0.1.0"\ndescription = "d"\n\n'
            '[[servers]]\nname = "s"\ncommand = "npx"\ntransport = "sse"\n'
        )
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("invalid transport" in e for e in errors)

    def test_server_stdio_missing_command(self, tmp_path: Path):
        toml = (
            '[pack]\nname = "x"\nversion = "0.1.0"\ndescription = "d"\n\n'
            '[[servers]]\nname = "s"\ntransport = "stdio"\n'
        )
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("missing 'command'" in e for e in errors)

    def test_server_http_missing_url(self, tmp_path: Path):
        toml = (
            '[pack]\nname = "x"\nversion = "0.1.0"\ndescription = "d"\n\n'
            '[[servers]]\nname = "s"\ntransport = "http"\n'
        )
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("missing 'url'" in e for e in errors)

    def test_duplicate_server_names_within_pack(self, tmp_path: Path):
        toml = (
            '[pack]\nname = "x"\nversion = "0.1.0"\ndescription = "d"\n\n'
            '[[servers]]\nname = "dup"\ncommand = "a"\ntransport = "stdio"\n\n'
            '[[servers]]\nname = "dup"\ncommand = "b"\ntransport = "stdio"\n'
        )
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("duplicate server name" in e for e in errors)

    def test_servers_table_not_array(self, tmp_path: Path):
        toml = (
            '[pack]\nname = "x"\nversion = "0.1.0"\ndescription = "d"\n\n'
            '[servers]\nname = "s"\ncommand = "npx"\n'
        )
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("[[servers]]" in e for e in errors)

    def test_server_invalid_name_format(self, tmp_path: Path):
        toml = (
            '[pack]\nname = "x"\nversion = "0.1.0"\ndescription = "d"\n\n'
            '[[servers]]\nname = "My_Server"\ncommand = "npx"\ntransport = "stdio"\n'
        )
        _write_pack(tmp_path, "x", toml)
        errors = validate_pack(tmp_path / "x" / "pack.toml", "x")
        assert any("invalid server name" in e for e in errors)

    def test_malformed_toml(self, tmp_path: Path):
        _write_pack(tmp_path, "bad", "this is not valid TOML [[[")
        errors = validate_pack(tmp_path / "bad" / "pack.toml", "bad")
        assert len(errors) == 1
        assert "bad" in errors[0]


# ---------------------------------------------------------------------------
# validate_unique_server_names
# ---------------------------------------------------------------------------


class TestValidateUniqueServerNames:
    def test_no_conflicts(self, tmp_path: Path):
        _write_pack(tmp_path, "a", VALID_PACK_WITH_SERVER)
        toml_b = VALID_PACK_WITH_SERVER.replace("server-pack", "b").replace(
            "my-server", "other-server"
        )
        _write_pack(tmp_path, "b", toml_b)
        errors = validate_unique_server_names(tmp_path)
        assert errors == []

    def test_conflict_detected(self, tmp_path: Path):
        _write_pack(tmp_path, "a", VALID_PACK_WITH_SERVER)
        toml_b = VALID_PACK_WITH_SERVER.replace("server-pack", "b")
        # Keep same server name "my-server"
        _write_pack(tmp_path, "b", toml_b)
        errors = validate_unique_server_names(tmp_path)
        assert len(errors) == 1
        assert "my-server" in errors[0]
        assert "conflicts" in errors[0]


# ---------------------------------------------------------------------------
# version immutability (process_pack)
# ---------------------------------------------------------------------------


class TestVersionImmutability:
    def test_same_content_ok(self, tmp_path: Path):
        src = tmp_path / "src"
        packs = tmp_path / "packs"
        packs.mkdir()
        _write_pack(src, "my-pack", VALID_PACK_TOML)

        # First generation
        result1 = process_pack(src, packs, "my-pack")
        assert result1["latest_version"] == "0.1.0"

        # Second generation with same content — should not fail
        result2 = process_pack(src, packs, "my-pack")
        assert result2["latest_version"] == "0.1.0"

    def test_different_content_fails(self, tmp_path: Path):
        src = tmp_path / "src"
        packs = tmp_path / "packs"
        packs.mkdir()
        _write_pack(src, "my-pack", VALID_PACK_TOML)

        # First generation
        process_pack(src, packs, "my-pack")

        # Modify a file without bumping version
        (src / "my-pack" / "extra.txt").write_text("new file", encoding="utf-8")

        with pytest.raises(SystemExit) as exc_info:
            process_pack(src, packs, "my-pack")
        assert exc_info.value.code == 1

    def test_no_pack_toml_skipped(self, tmp_path: Path):
        src = tmp_path / "src"
        packs = tmp_path / "packs"
        packs.mkdir()
        (src / "empty-pack").mkdir(parents=True)

        result = process_pack(src, packs, "empty-pack")
        assert result == {}
        assert not (packs / "empty-pack.json").exists()

    def test_name_mismatch_skipped(self, tmp_path: Path):
        src = tmp_path / "src"
        packs = tmp_path / "packs"
        packs.mkdir()
        toml = VALID_PACK_TOML.replace('name = "my-pack"', 'name = "other-name"')
        _write_pack(src, "my-pack", toml)

        result = process_pack(src, packs, "my-pack")
        assert result == {}


# ---------------------------------------------------------------------------
# Full end-to-end generation
# ---------------------------------------------------------------------------


class TestRegenerateIndex:
    def test_empty_packs_dir(self, tmp_path: Path):
        packs = tmp_path / "packs"
        packs.mkdir()
        index = regenerate_index(packs)
        assert index["schema_version"] == 1
        assert index["packs"] == {}

    def test_pack_with_no_versions_skipped(self, tmp_path: Path):
        packs = tmp_path / "packs"
        packs.mkdir()
        # Write a pack JSON with empty versions
        (packs / "empty.json").write_text(
            json.dumps({"name": "empty", "versions": []}), encoding="utf-8"
        )
        index = regenerate_index(packs)
        assert "empty" not in index["packs"]


class TestFullGeneration:
    def test_end_to_end(self, tmp_path: Path):
        src = tmp_path / "src"
        packs = tmp_path / "packs"
        packs.mkdir()

        _write_pack(src, "alpha", VALID_PACK_TOML.replace("my-pack", "alpha"))
        toml_beta = (
            VALID_PACK_TOML.replace("my-pack", "beta")
            .replace("0.1.0", "0.2.0")
        )
        _write_pack(src, "beta", toml_beta)

        # Generate both packs
        for name in ["alpha", "beta"]:
            process_pack(src, packs, name)

        # Verify pack JSONs
        alpha_json = json.loads((packs / "alpha.json").read_text(encoding="utf-8"))
        assert alpha_json["name"] == "alpha"
        assert alpha_json["schema_version"] == 1
        assert len(alpha_json["versions"]) == 1
        assert alpha_json["versions"][0]["version"] == "0.1.0"
        assert "pack.toml" in alpha_json["versions"][0]["files"]

        beta_json = json.loads((packs / "beta.json").read_text(encoding="utf-8"))
        assert beta_json["versions"][0]["version"] == "0.2.0"

        # Regenerate index
        index = regenerate_index(packs)
        assert index["schema_version"] == 1
        assert "alpha" in index["packs"]
        assert "beta" in index["packs"]
        assert index["packs"]["alpha"]["latest_version"] == "0.1.0"
        assert index["packs"]["beta"]["latest_version"] == "0.2.0"

    def test_multi_version(self, tmp_path: Path):
        """Verify that bumping the version adds a new entry without removing the old."""
        src = tmp_path / "src"
        packs = tmp_path / "packs"
        packs.mkdir()

        _write_pack(src, "my-pack", VALID_PACK_TOML)
        process_pack(src, packs, "my-pack")

        # Bump version
        toml_v2 = VALID_PACK_TOML.replace("0.1.0", "0.2.0")
        (src / "my-pack" / "pack.toml").write_text(toml_v2, encoding="utf-8")
        process_pack(src, packs, "my-pack")

        pack_json = json.loads((packs / "my-pack.json").read_text(encoding="utf-8"))
        versions = [v["version"] for v in pack_json["versions"]]
        assert versions == ["0.2.0", "0.1.0"]  # sorted descending
