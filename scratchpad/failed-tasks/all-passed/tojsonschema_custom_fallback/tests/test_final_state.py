import json
import os
import re
import shutil
import subprocess
from typing import Any

import pytest

PROJECT_DIR = "/home/user/myproject"
OUT_DIR = os.path.join(PROJECT_DIR, "out")
SCHEMA_PATH = os.path.join(OUT_DIR, "user.schema.json")
SRC_DIR = os.path.join(PROJECT_DIR, "src")
CLI_PATH = os.path.join(PROJECT_DIR, "cli.ts")


@pytest.fixture(scope="module")
def cli_result() -> subprocess.CompletedProcess[str]:
    """Run the CLI exactly once for the whole module after wiping the artifact."""
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    return subprocess.run(
        ["npx", "--no-install", "tsx", "cli.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )


@pytest.fixture(scope="module")
def schema_document(cli_result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    """Parse the produced JSON Schema file once for shared inspection."""
    assert cli_result.returncode == 0, (
        f"CLI exited with non-zero code {cli_result.returncode}: "
        f"stdout={cli_result.stdout!r}, stderr={cli_result.stderr!r}"
    )
    assert os.path.isfile(SCHEMA_PATH), (
        f"Expected JSON Schema artifact at {SCHEMA_PATH} after running the CLI."
    )
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        content = f.read()
    assert content.strip(), f"{SCHEMA_PATH} exists but is empty."
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{SCHEMA_PATH} does not contain valid JSON: {exc}; content={content!r}"
        )


def _walk(node: Any):
    """Yield every dict node anywhere inside the JSON document."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk(item)


# ---------------------------------------------------------------------------
# Criterion 1: CLI runs, writes the schema file, prints WROTE <path>, exit 0
# ---------------------------------------------------------------------------


def test_cli_exits_successfully(cli_result: subprocess.CompletedProcess[str]):
    assert cli_result.returncode == 0, (
        f"CLI must exit with code 0; got {cli_result.returncode}. "
        f"stdout={cli_result.stdout!r} stderr={cli_result.stderr!r}"
    )


def test_cli_prints_wrote_line(cli_result: subprocess.CompletedProcess[str]):
    """stdout must contain exactly one line of the form `WROTE <abs-path>`."""
    lines = [ln for ln in cli_result.stdout.splitlines() if ln.strip()]
    matches = [ln for ln in lines if ln.startswith("WROTE ")]
    assert matches, (
        "Expected stdout to contain a line starting with 'WROTE ' followed by "
        f"the absolute schema path; got stdout={cli_result.stdout!r}"
    )
    # Take the first WROTE line and ensure the printed path matches the actual artifact.
    _, _, printed_path = matches[0].partition(" ")
    printed_path = printed_path.strip()
    assert os.path.isabs(printed_path), (
        f"Path printed after 'WROTE' must be absolute; got {printed_path!r}."
    )
    assert os.path.realpath(printed_path) == os.path.realpath(SCHEMA_PATH), (
        f"Path printed after 'WROTE' ({printed_path!r}) must resolve to the "
        f"expected schema artifact ({SCHEMA_PATH!r})."
    )


def test_schema_file_written(cli_result: subprocess.CompletedProcess[str]):
    assert os.path.isfile(SCHEMA_PATH), (
        f"Expected the CLI to write {SCHEMA_PATH}; file is missing. "
        f"stdout={cli_result.stdout!r} stderr={cli_result.stderr!r}"
    )
    assert os.path.getsize(SCHEMA_PATH) > 0, (
        f"{SCHEMA_PATH} was created but is empty."
    )


# ---------------------------------------------------------------------------
# Criterion 2: $schema must be draft-07
# ---------------------------------------------------------------------------


def test_schema_uses_draft_07_dialect(schema_document: dict[str, Any]):
    expected = "http://json-schema.org/draft-07/schema#"
    actual = schema_document.get("$schema")
    assert actual == expected, (
        f"Top-level $schema must be exactly {expected!r}; got {actual!r}."
    )


# ---------------------------------------------------------------------------
# Criterion 3: morph fallback marker present (format: "morph-redacted")
# ---------------------------------------------------------------------------


def test_morph_fallback_marker_present(schema_document: dict[str, Any]):
    found = any(
        isinstance(node.get("format"), str) and node["format"] == "morph-redacted"
        for node in _walk(schema_document)
    )
    assert found, (
        "Expected at least one node in the JSON Schema to carry "
        '`"format": "morph-redacted"` from the morph fallback handler. '
        f"Schema document was: {json.dumps(schema_document)[:1500]}"
    )


# ---------------------------------------------------------------------------
# Criterion 4: predicate fallback marker present (x-arktype-fallback: predicate)
# ---------------------------------------------------------------------------


def test_predicate_fallback_marker_present(schema_document: dict[str, Any]):
    found = any(
        node.get("x-arktype-fallback") == "predicate"
        for node in _walk(schema_document)
    )
    assert found, (
        "Expected at least one node in the JSON Schema to carry "
        '`"x-arktype-fallback": "predicate"` from the predicate fallback '
        f"handler. Schema document was: {json.dumps(schema_document)[:1500]}"
    )


# ---------------------------------------------------------------------------
# Criterion 5: recursive friends use $ref
# ---------------------------------------------------------------------------


def test_recursive_friends_use_ref(schema_document: dict[str, Any]):
    refs = [
        node["$ref"]
        for node in _walk(schema_document)
        if isinstance(node.get("$ref"), str)
    ]
    assert refs, (
        "Expected at least one `$ref` string in the JSON Schema to encode "
        "the recursive `friends: User[]` self-reference. None were found. "
        f"Schema document was: {json.dumps(schema_document)[:1500]}"
    )


# ---------------------------------------------------------------------------
# Criterion 6: validator source contains toJsonSchema( and fallback
# ---------------------------------------------------------------------------


def _collect_src_source() -> str:
    assert os.path.isdir(SRC_DIR), (
        f"Expected a source directory at {SRC_DIR}; it is missing."
    )
    combined: list[str] = []
    for root, _dirs, files in os.walk(SRC_DIR):
        for name in files:
            if name.endswith((".ts", ".mts", ".cts", ".tsx")):
                with open(os.path.join(root, name), encoding="utf-8") as f:
                    combined.append(f.read())
    assert combined, (
        f"Expected at least one TypeScript source file under {SRC_DIR}; "
        "found none."
    )
    return "\n".join(combined)


def test_validator_source_uses_tojsonschema_and_fallback():
    source = _collect_src_source()
    assert "toJsonSchema(" in source, (
        "Expected the source under src/ to contain the literal substring "
        "`toJsonSchema(`."
    )
    assert re.search(r"\bfallback\b", source), (
        "Expected the source under src/ to reference `fallback` (the option "
        "name passed to toJsonSchema)."
    )


def test_cli_entrypoint_exists():
    assert os.path.isfile(CLI_PATH), (
        f"Expected the CLI entrypoint at {CLI_PATH}."
    )
