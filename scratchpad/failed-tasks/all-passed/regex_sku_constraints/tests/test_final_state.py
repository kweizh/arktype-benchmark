import json
import os
import re
import subprocess

PROJECT_DIR = "/home/user/myproject"
VALIDATOR_PATH = os.path.join(PROJECT_DIR, "src", "validator.ts")
CLI_PATH = os.path.join(PROJECT_DIR, "cli.ts")

VENDOR_ID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"


def _run_cli(payload: dict | list) -> subprocess.CompletedProcess[str]:
    """Invoke the CLI by piping a JSON payload through stdin."""
    return subprocess.run(
        ["npx", "--no-install", "tsx", "cli.ts"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )


def _stdout_lines(stdout: str) -> list[str]:
    return [line for line in stdout.splitlines() if line.strip() != ""]


def _make_sku(index: int) -> str:
    """Generate a deterministic SKU matching ^[A-Z]{2}-\\d{4}-[a-z]{3}$ for index 0..675."""
    # Letters cycle through AA..ZZ giving 26*26 = 676 distinct two-letter combos.
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lower = "abcdefghijklmnopqrstuvwxyz"
    first = alpha[(index // 26) % 26]
    second = alpha[index % 26]
    number = f"{index % 10000:04d}"
    suffix = (
        lower[index % 26]
        + lower[(index // 26) % 26]
        + lower[(index // (26 * 26)) % 26]
    )
    return f"{first}{second}-{number}-{suffix}"


# ---------------------------------------------------------------------------
# Behavioural tests (Criteria 1-6)
# ---------------------------------------------------------------------------


def test_valid_catalog_with_three_distinct_skus_is_accepted():
    """Criterion 1: a catalog with 3 distinct, well-formed SKUs validates."""
    payload = {
        "vendorId": VENDOR_ID,
        "skus": ["AB-1234-xyz", "CD-5678-abc", "EF-9012-def"],
    }
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0] == "VALID", (
        f"Expected first non-empty stdout line to be 'VALID', got: {lines!r} "
        f"(stderr={result.stderr!r})"
    )
    assert len(lines) >= 2, (
        f"Expected validated JSON catalog on the line after VALID, got: {lines!r}"
    )

    try:
        validated = json.loads(lines[1])
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Second stdout line is not valid JSON: {lines[1]!r} (error: {exc})"
        )

    assert validated.get("vendorId") == VENDOR_ID, (
        f"Validated vendorId mismatch: {validated!r}"
    )
    assert validated.get("skus") == [
        "AB-1234-xyz",
        "CD-5678-abc",
        "EF-9012-def",
    ], f"Validated skus mismatch: {validated!r}"


def test_lowercase_first_segment_is_rejected():
    """Criterion 2: a SKU whose first segment is lowercase fails the regex."""
    payload = {"vendorId": VENDOR_ID, "skus": ["ab-1234-xyz"]}
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for lowercase prefix, "
        f"got: {result.stdout!r}"
    )


def test_duplicated_sku_is_rejected_with_skus_path():
    """Criterion 3: duplicated SKUs are rejected with an error mentioning `skus`."""
    payload = {
        "vendorId": VENDOR_ID,
        "skus": ["AB-1234-xyz", "AB-1234-xyz"],
    }
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for duplicates, got: "
        f"{result.stdout!r}"
    )
    assert "skus" in lines[0], (
        f"Expected the INVALID error line to reference the 'skus' path "
        f"(structured uniqueness error), got: {lines[0]!r}"
    )


def test_more_than_200_skus_is_rejected():
    """Criterion 4: a catalog with 201 distinct SKUs exceeds the length bound."""
    skus = [_make_sku(i) for i in range(201)]
    # Sanity-check uniqueness of the generated SKUs so this case truly exercises
    # the length bound and not the uniqueness predicate.
    assert len(set(skus)) == 201, (
        "Verifier bug: generated SKUs must be distinct so the length bound "
        "is what triggers the rejection."
    )
    payload = {"vendorId": VENDOR_ID, "skus": skus}
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for >200 SKUs, got: "
        f"{result.stdout!r}"
    )


def test_missing_vendor_id_is_rejected():
    """Criterion 5: a catalog without `vendorId` is rejected."""
    payload = {"skus": ["AB-1234-xyz"]}
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for missing vendorId, got: "
        f"{result.stdout!r}"
    )


def test_empty_sku_list_is_rejected():
    """Criterion 6: a catalog with an empty `skus` array is rejected."""
    payload = {"vendorId": VENDOR_ID, "skus": []}
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for empty skus, got: "
        f"{result.stdout!r}"
    )


# ---------------------------------------------------------------------------
# Implementation-shape tests (Criterion 7)
# ---------------------------------------------------------------------------


def _read_validator_source() -> str:
    assert os.path.isfile(VALIDATOR_PATH), (
        f"Expected validator module at {VALIDATOR_PATH}."
    )
    with open(VALIDATOR_PATH, encoding="utf-8") as f:
        return f.read()


def test_validator_uses_schema_level_regex():
    """Criterion 7 (part 1): SKU pattern is expressed inside the ArkType schema."""
    source = _read_validator_source()
    assert re.search(r"from\s+['\"]arktype['\"]", source), (
        "src/validator.ts must import from 'arktype'."
    )
    # Accept either a literal regex anchored on the SKU pattern shape or a
    # reference to ArkType's `matching` / `string.regex` built-in keyword.
    has_regex_literal = re.search(r"/\^?\[A-Z\]\{2\}-", source) is not None
    has_matching_keyword = re.search(r"\bmatching\b", source) is not None
    has_string_regex_keyword = re.search(r"string\.regex", source) is not None
    assert has_regex_literal or has_matching_keyword or has_string_regex_keyword, (
        "src/validator.ts must encode the SKU pattern at the schema level via "
        "a regex literal (e.g. `/^[A-Z]{2}-\\d{4}-[a-z]{3}$/`) or the built-in "
        "`matching` / `string.regex` keyword."
    )


def test_validator_uses_narrow_predicate_for_uniqueness():
    """Criterion 7 (part 2): uniqueness is enforced via an ArkType narrow predicate."""
    source = _read_validator_source()
    assert ".narrow(" in source, (
        "src/validator.ts must use ArkType's `.narrow(...)` API to enforce SKU "
        "uniqueness with a structured error path."
    )


def test_cli_entrypoint_exists():
    """Sanity: the CLI entrypoint required by the acceptance criteria exists."""
    assert os.path.isfile(CLI_PATH), f"Expected CLI entrypoint at {CLI_PATH}."
