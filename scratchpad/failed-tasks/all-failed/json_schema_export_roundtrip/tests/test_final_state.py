import json
import os
import re
import subprocess

PROJECT_DIR = "/home/user/myproject"
SCHEMA_MODULE = os.path.join(PROJECT_DIR, "src", "schema.ts")
CLI_PATH = os.path.join(PROJECT_DIR, "cli.ts")
EXPORTED_JSON_PATH = os.path.join(PROJECT_DIR, "out", "user.schema.json")

DRAFT_2020_12_URI = "https://json-schema.org/draft/2020-12/schema"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _valid_user_depth3() -> dict:
    return {
        "id": "11111111-1111-4111-8111-111111111111",
        "username": "alice123",
        "email": "alice@example.com",
        "score": "42",
        "address": {
            "street": "1 Main",
            "city": "Springfield",
            "zip": "10001-1234",
        },
        "posts": [
            {
                "title": "Hello",
                "tags": ["intro", "news"],
                "comments": [
                    {
                        "id": "22222222-2222-4222-8222-222222222222",
                        "body": "first",
                        "replies": [
                            {
                                "id": "33333333-3333-4333-8333-333333333333",
                                "body": "second",
                                "replies": [
                                    {
                                        "id": "44444444-4444-4444-8444-444444444444",
                                        "body": "third",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }


def _valid_user_minimal() -> dict:
    return {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "username": "bob42",
        "email": "bob@example.org",
        "score": "7",
        "address": {
            "street": "5 Side",
            "city": "Townsville",
            "zip": "94110",
        },
        "posts": [
            {
                "title": "Short",
                "tags": ["x"],
                "comments": [],
            }
        ],
    }


def _run_cli(payload) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["npx", "--no-install", "tsx", "cli.ts"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=180,
    )


def _stdout_lines(stdout: str) -> list[str]:
    return [line for line in stdout.splitlines() if line.strip() != ""]


def _assert_cli_output(
    result: subprocess.CompletedProcess,
    expected_first_line: str,
    expected_original: bool,
    expected_roundtrip: bool,
    label: str,
) -> None:
    assert result.returncode == 0, (
        f"[{label}] CLI exited non-zero: "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines, (
        f"[{label}] CLI produced no stdout output. "
        f"stderr={result.stderr!r}"
    )
    assert lines[0] == expected_first_line, (
        f"[{label}] Expected first line {expected_first_line!r} but got "
        f"{lines[0]!r}. Full stdout: {result.stdout!r}"
    )
    assert len(lines) >= 2, (
        f"[{label}] Expected a second JSON line after {expected_first_line!r}, "
        f"got: {lines!r} (stderr={result.stderr!r})"
    )
    try:
        flags = json.loads(lines[1])
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"[{label}] Second stdout line is not valid JSON: "
            f"{lines[1]!r} (error: {exc})"
        )
    assert isinstance(flags, dict), (
        f"[{label}] Second line must be a JSON object, got: {flags!r}"
    )
    assert "original" in flags and "roundtrip" in flags, (
        f"[{label}] Second-line JSON must contain keys 'original' and "
        f"'roundtrip'. Got: {flags!r}"
    )
    assert isinstance(flags["original"], bool) and isinstance(
        flags["roundtrip"], bool
    ), (
        f"[{label}] 'original' and 'roundtrip' must be booleans. "
        f"Got: {flags!r}"
    )
    assert flags["original"] is expected_original, (
        f"[{label}] Expected original={expected_original} but got "
        f"{flags['original']}. Full stdout: {result.stdout!r}"
    )
    assert flags["roundtrip"] is expected_roundtrip, (
        f"[{label}] Expected roundtrip={expected_roundtrip} but got "
        f"{flags['roundtrip']}. Full stdout: {result.stdout!r}"
    )


# ---------------------------------------------------------------------------
# Test Criteria 1–2: valid fixtures accepted by both schemas
# ---------------------------------------------------------------------------


def test_valid_user_depth3_accepted_by_both_schemas():
    """Criterion 1: depth-3 recursive comment chain validates in both schemas."""
    result = _run_cli(_valid_user_depth3())
    _assert_cli_output(
        result,
        expected_first_line="VALID",
        expected_original=True,
        expected_roundtrip=True,
        label="valid depth-3 user",
    )


def test_valid_user_minimal_accepted_by_both_schemas():
    """Criterion 2: minimal payload validates in both schemas."""
    result = _run_cli(_valid_user_minimal())
    _assert_cli_output(
        result,
        expected_first_line="VALID",
        expected_original=True,
        expected_roundtrip=True,
        label="valid minimal user",
    )


# ---------------------------------------------------------------------------
# Test Criteria 3–7: invalid fixtures rejected by both schemas
# ---------------------------------------------------------------------------


def test_invalid_email_rejected_by_both_schemas():
    """Criterion 3: bad email rejected by both schemas."""
    payload = _valid_user_depth3()
    payload["email"] = "not-an-email"
    result = _run_cli(payload)
    _assert_cli_output(
        result,
        expected_first_line="INVALID",
        expected_original=False,
        expected_roundtrip=False,
        label="invalid email",
    )


def test_invalid_zip_pattern_rejected_by_both_schemas():
    """Criterion 4: bad zip pattern rejected by both schemas."""
    payload = _valid_user_depth3()
    payload["address"]["zip"] = "abcde"
    result = _run_cli(payload)
    _assert_cli_output(
        result,
        expected_first_line="INVALID",
        expected_original=False,
        expected_roundtrip=False,
        label="invalid zip pattern",
    )


def test_invalid_username_too_short_rejected_by_both_schemas():
    """Criterion 5: username shorter than 3 rejected by both schemas."""
    payload = _valid_user_depth3()
    payload["username"] = "ab"
    result = _run_cli(payload)
    _assert_cli_output(
        result,
        expected_first_line="INVALID",
        expected_original=False,
        expected_roundtrip=False,
        label="invalid username (too short)",
    )


def test_invalid_post_title_too_long_rejected_by_both_schemas():
    """Criterion 6: post title length > 120 rejected by both schemas."""
    payload = _valid_user_depth3()
    payload["posts"][0]["title"] = "x" * 200
    result = _run_cli(payload)
    _assert_cli_output(
        result,
        expected_first_line="INVALID",
        expected_original=False,
        expected_roundtrip=False,
        label="invalid post title length",
    )


def test_invalid_post_tags_too_many_rejected_by_both_schemas():
    """Criterion 7: post tags array exceeding 10 entries rejected by both schemas."""
    payload = _valid_user_depth3()
    payload["posts"][0]["tags"] = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
    ]
    result = _run_cli(payload)
    _assert_cli_output(
        result,
        expected_first_line="INVALID",
        expected_original=False,
        expected_roundtrip=False,
        label="invalid post tags count",
    )


# ---------------------------------------------------------------------------
# Test Criterion 8: exported JSON Schema artifact
# ---------------------------------------------------------------------------


def test_exported_json_schema_file_exists():
    """Criterion 8 (part 1): out/user.schema.json must exist after CLI ran."""
    assert os.path.isfile(EXPORTED_JSON_PATH), (
        f"Expected exported JSON Schema at {EXPORTED_JSON_PATH} after the "
        f"CLI has been invoked, but the file is missing."
    )


def test_exported_json_schema_dialect_is_draft_2020_12():
    """Criterion 8 (part 2): exported JSON Schema must declare draft-2020-12."""
    assert os.path.isfile(EXPORTED_JSON_PATH), (
        f"Cannot read JSON Schema at {EXPORTED_JSON_PATH}; file missing."
    )
    with open(EXPORTED_JSON_PATH, encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"{EXPORTED_JSON_PATH} is not valid JSON: {exc}"
            )
    assert isinstance(doc, dict), (
        f"{EXPORTED_JSON_PATH} must contain a JSON object at the root, "
        f"got: {type(doc).__name__}"
    )
    assert doc.get("$schema") == DRAFT_2020_12_URI, (
        f"$schema in {EXPORTED_JSON_PATH} must equal {DRAFT_2020_12_URI!r}, "
        f"got: {doc.get('$schema')!r}"
    )


# ---------------------------------------------------------------------------
# Test Criterion 9: implementation shape
# ---------------------------------------------------------------------------


def _read_schema_source() -> str:
    assert os.path.isfile(SCHEMA_MODULE), (
        f"Expected schema module at {SCHEMA_MODULE}."
    )
    with open(SCHEMA_MODULE, encoding="utf-8") as f:
        return f.read()


def test_schema_module_exports_required_symbols():
    """Criterion 9 (part 1): src/schema.ts exports the three required symbols."""
    source = _read_schema_source()
    for symbol in ("userSchema", "roundTrippedUserSchema", "exportUserJsonSchema"):
        named_declaration = re.search(
            r"export\s+(?:async\s+)?(?:function|const|let|var)\s+"
            + re.escape(symbol)
            + r"\b",
            source,
        )
        named_re_export = re.search(
            r"export\s*(?:type\s*)?\{[^}]*\b"
            + re.escape(symbol)
            + r"\b[^}]*\}",
            source,
        )
        assert named_declaration or named_re_export, (
            f"src/schema.ts must export `{symbol}` (as a named declaration "
            f"or re-export)."
        )


def test_schema_module_uses_scope_export():
    """Criterion 9 (part 2): schema is built via `scope({...}).export()`."""
    source = _read_schema_source()
    assert re.search(r"from\s+['\"]arktype['\"]", source), (
        "src/schema.ts must import from 'arktype'."
    )
    assert re.search(r"\bscope\s*\(", source), (
        "src/schema.ts must use ArkType's `scope` to build the schema."
    )
    assert re.search(r"scope\s*\([\s\S]+?\)\s*\.\s*export\s*\(\s*\)", source), (
        "src/schema.ts must build the schema via `scope({...}).export()`."
    )


def test_schema_module_imports_ark_json_schema():
    """Criterion 9 (part 3): src/schema.ts imports from @ark/json-schema."""
    source = _read_schema_source()
    assert re.search(r"from\s+['\"]@ark/json-schema['\"]", source), (
        "src/schema.ts must import from '@ark/json-schema'."
    )


def test_cli_entrypoint_exists():
    """Sanity: the CLI entrypoint required by Acceptance Criteria exists."""
    assert os.path.isfile(CLI_PATH), (
        f"Expected CLI entrypoint at {CLI_PATH}."
    )
