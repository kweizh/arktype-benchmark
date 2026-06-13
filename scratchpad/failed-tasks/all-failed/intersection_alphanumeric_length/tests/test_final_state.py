import json
import os
import re
import subprocess

PROJECT_DIR = "/home/user/myproject"
VALIDATE_TS = os.path.join(PROJECT_DIR, "src", "validate.ts")
PACKAGE_JSON = os.path.join(PROJECT_DIR, "package.json")


def _run_validator(arg: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        ["npx", "tsx", "src/validate.ts", arg],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )


def test_package_json_pins_arktype_2_2_0():
    assert os.path.isfile(PACKAGE_JSON), f"{PACKAGE_JSON} not found."
    with open(PACKAGE_JSON) as f:
        data = json.load(f)
    deps = data.get("dependencies", {}) or {}
    assert deps.get("arktype") == "2.2.0", (
        f"Expected dependencies.arktype to be exactly \"2.2.0\" in package.json, got: {deps.get('arktype')!r}"
    )


def test_validate_script_exists():
    assert os.path.isfile(VALIDATE_TS), f"Expected validator source file at {VALIDATE_TS}."


def test_validate_script_uses_single_arktype_chain():
    with open(VALIDATE_TS) as f:
        source = f.read()
    assert re.search(r"""from\s+['"]arktype['"]""", source), (
        "validate.ts must import from 'arktype'."
    )
    assert ".narrow(" in source, (
        "The first-letter rule must be expressed inside an ArkType '.narrow(...)' call."
    )
    assert "string.alphanumeric" in source, (
        "The schema must reference the built-in keyword 'string.alphanumeric'."
    )
    assert "length" in source, (
        "The schema must use the ArkType 'length' range constraint."
    )
    assert ".test(" not in source, (
        "validate.ts must not call '.test(' (no manual JS regex check outside the ArkType chain)."
    )


def test_valid_username_alice123():
    result = _run_validator("alice123")
    assert result.returncode == 0, (
        f"Expected exit code 0 for 'alice123', got {result.returncode}. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == "valid", (
        f"Expected stdout 'valid' for 'alice123', got: {result.stdout!r}"
    )


def test_invalid_too_short_al():
    result = _run_validator("al")
    assert result.returncode == 1, (
        f"Expected exit code 1 for 'al' (too short), got {result.returncode}. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == "invalid", (
        f"Expected stdout 'invalid' for 'al', got: {result.stdout!r}"
    )


def test_invalid_too_long():
    too_long = "a" * 20
    result = _run_validator(too_long)
    assert result.returncode == 1, (
        f"Expected exit code 1 for 20-character input, got {result.returncode}. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == "invalid", (
        f"Expected stdout 'invalid' for 20-character input, got: {result.stdout!r}"
    )


def test_invalid_non_alphanumeric():
    result = _run_validator("alice!")
    assert result.returncode == 1, (
        f"Expected exit code 1 for 'alice!' (non-alphanumeric), got {result.returncode}. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == "invalid", (
        f"Expected stdout 'invalid' for 'alice!', got: {result.stdout!r}"
    )


def test_invalid_starts_with_digit():
    result = _run_validator("1alice")
    assert result.returncode == 1, (
        f"Expected exit code 1 for '1alice' (does not start with a letter), got {result.returncode}. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == "invalid", (
        f"Expected stdout 'invalid' for '1alice', got: {result.stdout!r}"
    )
