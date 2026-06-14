import json
import os
import re
import subprocess

PROJECT_DIR = "/home/user/myproject"
VALIDATOR_PATH = os.path.join(PROJECT_DIR, "src", "validator.ts")
CLI_PATH = os.path.join(PROJECT_DIR, "cli.ts")


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


# ---------------------------------------------------------------------------
# Behavioural tests (Criteria 1-6)
# ---------------------------------------------------------------------------


def test_valid_page_of_users_is_accepted():
    """Criterion 1: a well-formed Page<User> validates and is echoed back."""
    payload = {
        "kind": "User",
        "page": {
            "items": [
                {"id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d", "name": "Alice"},
                {"id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6", "name": "Bob"},
            ],
            "total": 42,
            "page": 1,
            "perPage": 25,
            "hasNext": True,
        },
    }

    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code for a valid Page<User>: "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )

    lines = _stdout_lines(result.stdout)
    assert lines and lines[0] == "VALID", (
        f"Expected first non-empty stdout line to be 'VALID', got: {lines!r} "
        f"(stderr={result.stderr!r})"
    )
    assert len(lines) >= 2, (
        f"Expected validated JSON on the line after VALID, got: {lines!r}"
    )

    try:
        validated = json.loads(lines[1])
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Second stdout line is not valid JSON: {lines[1]!r} (error: {exc})"
        )

    assert validated.get("total") == 42, (
        f"Validated total mismatch: {validated!r}"
    )
    assert validated.get("perPage") == 25, (
        f"Validated perPage mismatch: {validated!r}"
    )
    assert validated.get("hasNext") is True, (
        f"Validated hasNext mismatch: {validated!r}"
    )
    items = validated.get("items") or []
    assert len(items) == 2, f"Expected 2 items, got: {items!r}"
    assert items[0].get("name") == "Alice", (
        f"Validated first user name mismatch: {items[0]!r}"
    )


def test_valid_page_of_posts_is_accepted():
    """Criterion 2: a well-formed Page<Post> validates and is echoed back."""
    payload = {
        "kind": "Post",
        "page": {
            "items": [
                {
                    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                    "title": "Hello, world",
                    "authorId": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
                }
            ],
            "total": 1,
            "page": 1,
            "perPage": 10,
            "hasNext": False,
        },
    }

    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code for a valid Page<Post>: "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )

    lines = _stdout_lines(result.stdout)
    assert lines and lines[0] == "VALID", (
        f"Expected first non-empty stdout line to be 'VALID', got: {lines!r} "
        f"(stderr={result.stderr!r})"
    )
    assert len(lines) >= 2, (
        f"Expected validated JSON on the line after VALID, got: {lines!r}"
    )

    try:
        validated = json.loads(lines[1])
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Second stdout line is not valid JSON: {lines[1]!r} (error: {exc})"
        )

    items = validated.get("items") or []
    assert len(items) == 1, f"Expected 1 item, got: {items!r}"
    assert items[0].get("title") == "Hello, world", (
        f"Validated post title mismatch: {items[0]!r}"
    )
    assert items[0].get("authorId") == "f81d4fae-7dec-11d0-a765-00a0c91e6bf6", (
        f"Validated post authorId mismatch: {items[0]!r}"
    )


def test_malformed_user_in_page_is_rejected():
    """Criterion 3: a Page<User> with malformed first user is rejected."""
    payload = {
        "kind": "User",
        "page": {
            "items": [{"id": "not-a-uuid", "name": ""}],
            "total": 1,
            "page": 1,
            "perPage": 10,
            "hasNext": False,
        },
    }
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for malformed user, got: "
        f"{result.stdout!r}"
    )


def test_per_page_out_of_range_is_rejected():
    """Criterion 4: perPage above the [1, 100] range is rejected."""
    payload = {
        "kind": "User",
        "page": {
            "items": [],
            "total": 0,
            "page": 1,
            "perPage": 500,
            "hasNext": False,
        },
    }
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for perPage out of range, "
        f"got: {result.stdout!r}"
    )


def test_has_next_non_boolean_is_rejected():
    """Criterion 5: hasNext as a non-boolean value is rejected."""
    payload = {
        "kind": "Post",
        "page": {
            "items": [],
            "total": 0,
            "page": 1,
            "perPage": 10,
            "hasNext": "true",
        },
    }
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for non-boolean hasNext, "
        f"got: {result.stdout!r}"
    )


def test_negative_total_is_rejected():
    """Criterion 6: total < 0 is rejected."""
    payload = {
        "kind": "User",
        "page": {
            "items": [],
            "total": -3,
            "page": 1,
            "perPage": 10,
            "hasNext": False,
        },
    }
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for negative total, "
        f"got: {result.stdout!r}"
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


def test_validator_imports_arktype_and_uses_scope():
    """Criterion 7 (part 1): the validator imports `scope` from arktype."""
    source = _read_validator_source()
    assert re.search(r"from\s+['\"]arktype['\"]", source), (
        "src/validator.ts must import from 'arktype'."
    )
    assert re.search(r"\bscope\s*\(", source), (
        "src/validator.ts must call ArkType's `scope(...)`."
    )
    assert re.search(r"\.\s*export\s*\(\s*\)", source), (
        "src/validator.ts must call `.export()` on the scope."
    )


def test_validator_declares_generic_page_alias():
    """Criterion 7 (part 2): the scope contains a generic Page<...> alias.

    A generic declaration is required (e.g. `"Page<T>": { items: "T[]", ... }`).
    Duplicating the page envelope per kind is NOT acceptable.
    """
    source = _read_validator_source()
    # Look for an alias key that contains a generic parameter list, e.g.
    #   "Page<T>": { ... }   or   "Page<t, u>": { ... }
    generic_alias = re.search(
        r"['\"]Page\s*<\s*[A-Za-z_][A-Za-z0-9_]*"
        r"(?:\s+extends\s+[^,>]+)?"
        r"(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*(?:\s+extends\s+[^,>]+)?)*"
        r"\s*>['\"]\s*:",
        source,
    )
    assert generic_alias, (
        "src/validator.ts must declare a generic alias of the form "
        "`\"Page<T>\": { ... }` inside the scope."
    )


def test_validator_exports_validate_page():
    """The validator must export a `validatePage` symbol used by cli.ts."""
    source = _read_validator_source()
    pattern = re.compile(
        r"export\s+(?:async\s+)?(?:function|const|let|var)\s+validatePage\b"
    )
    assert pattern.search(source), (
        "src/validator.ts must export a `validatePage` symbol "
        "(e.g. `export function validatePage` or "
        "`export const validatePage`)."
    )


def test_cli_entrypoint_exists():
    """Sanity: the CLI entrypoint required by the acceptance criteria exists."""
    assert os.path.isfile(CLI_PATH), (
        f"Expected CLI entrypoint at {CLI_PATH}."
    )
