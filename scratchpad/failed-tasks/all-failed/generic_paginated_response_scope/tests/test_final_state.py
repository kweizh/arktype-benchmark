import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/arktype-pagination"

VALID_USER = {
    "id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
    "name": "Alice",
    "email": "alice@example.com",
}

INVALID_USER = {
    "id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
    "name": "Alice",
    "email": "not-an-email",
}

VALID_PRODUCT = {
    "sku": "ABC123",
    "name": "Widget",
    "price": 9.99,
}


def _run_validate(schema_name: str, payload: dict) -> subprocess.CompletedProcess:
    """Invoke `npx tsx validate.ts <schema_name>` with the given JSON payload on stdin."""
    return subprocess.run(
        ["npx", "tsx", "validate.ts", schema_name],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )


def test_validate_script_exists():
    validate_path = os.path.join(PROJECT_DIR, "validate.ts")
    assert os.path.isfile(validate_path), (
        f"Required CLI entrypoint not found at {validate_path}."
    )


# ---------------------------------------------------------------------------
# Verbatim criteria from instruction.md
# ---------------------------------------------------------------------------


def test_criterion_1_page_of_user_accepts_valid_user():
    """PageOfUser.assert({ items: [{...valid user}], total: 1, cursor: null }) MUST succeed."""
    payload = {"items": [VALID_USER], "total": 1, "cursor": None}
    result = _run_validate("PageOfUser", payload)
    assert result.returncode == 0, (
        "PageOfUser MUST accept a page containing a valid User. "
        f"exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    assert "OK" in result.stdout, (
        f"Expected success marker 'OK' on stdout, got stdout={result.stdout!r}"
    )


def test_criterion_2_page_of_user_rejects_invalid_user():
    """PageOfUser.assert({ items: [{...invalid user}], total: 1, cursor: null }) MUST throw."""
    payload = {"items": [INVALID_USER], "total": 1, "cursor": None}
    result = _run_validate("PageOfUser", payload)
    assert result.returncode != 0, (
        "PageOfUser MUST reject a page whose items contain an invalid User "
        "(email is not a valid email). "
        f"exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    assert result.stderr.strip() != "", (
        "Expected the ArkType assertion error to be written to stderr, "
        f"but stderr was empty. stdout={result.stdout!r}"
    )


def test_criterion_3_page_of_product_validates_product_items():
    """PageOfProduct.assert(...) MUST validate Product items."""
    payload = {"items": [VALID_PRODUCT], "total": 1, "cursor": None}
    result = _run_validate("PageOfProduct", payload)
    assert result.returncode == 0, (
        "PageOfProduct MUST accept a page containing a valid Product. "
        f"exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    assert "OK" in result.stdout, (
        f"Expected success marker 'OK' on stdout, got stdout={result.stdout!r}"
    )

    # And it must reject an obviously invalid product (missing required fields).
    bad_product = {"sku": "ABC123"}  # missing name/price
    bad_result = _run_validate(
        "PageOfProduct",
        {"items": [bad_product], "total": 1, "cursor": None},
    )
    assert bad_result.returncode != 0, (
        "PageOfProduct must reject items that don't match the Product shape. "
        f"exit={bad_result.returncode}, stdout={bad_result.stdout!r}, "
        f"stderr={bad_result.stderr!r}"
    )


def test_criterion_4_page_of_product_rejects_user_object():
    """Passing a User object into PageOfProduct MUST be rejected."""
    payload = {"items": [VALID_USER], "total": 1, "cursor": None}
    result = _run_validate("PageOfProduct", payload)
    assert result.returncode != 0, (
        "PageOfProduct MUST reject a User-shaped item (the generic Page<T> "
        "must bind T separately for User vs Product). "
        f"exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    assert result.stderr.strip() != "", (
        "Expected the ArkType assertion error to be written to stderr, "
        f"but stderr was empty. stdout={result.stdout!r}"
    )

    # Cross-check: PageOfUser must reject a Product-shaped item too.
    cross = _run_validate(
        "PageOfUser",
        {"items": [VALID_PRODUCT], "total": 1, "cursor": None},
    )
    assert cross.returncode != 0, (
        "PageOfUser MUST reject a Product-shaped item — the bindings are not "
        "interchangeable. "
        f"exit={cross.returncode}, stdout={cross.stdout!r}, stderr={cross.stderr!r}"
    )


def test_criterion_5_generic_defined_with_scoped_syntax():
    """The generic MUST be defined as `\"Page<T>\": {...}` inside the scope({...}) definition."""
    # Search the project source tree (excluding node_modules) for a TS/JS file that
    # contains a `scope({...})` call whose object literal uses the scoped-generic
    # key syntax for Page.
    matches: list[str] = []
    scoped_generic_re = re.compile(r'["\']Page\s*<[^>]+>["\']\s*:')
    standalone_re = re.compile(r"\btype\s*\(\s*['\"]<[^>]+>['\"]")
    scope_call_re = re.compile(r"\bscope\s*\(")

    for root, dirs, files in os.walk(PROJECT_DIR):
        # Skip vendor / build dirs
        dirs[:] = [d for d in dirs if d not in {"node_modules", "dist", "build", ".git"}]
        for fname in files:
            if not fname.endswith((".ts", ".tsx", ".mts", ".cts", ".js", ".mjs", ".cjs")):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            if scoped_generic_re.search(content) and scope_call_re.search(content):
                matches.append(fpath)

            # Forbidden: standalone-generic form for Page
            if standalone_re.search(content):
                # Only fail if it's used to declare Page (e.g., variable named Page)
                # Heuristic: presence of `type("<...>"` together with `Page` near it.
                forbidden_re = re.compile(
                    r"(?:const|let|var)\s+Page\b[^=]*=\s*type\s*\(\s*['\"]<",
                    re.MULTILINE,
                )
                assert not forbidden_re.search(content), (
                    f"In {fpath}: Page must NOT be declared with the standalone "
                    "`type(\"<t>\", {...})` form. It MUST be declared inside the "
                    "`scope({...})` definition using the `\"Page<T>\": {...}` key syntax."
                )

    assert matches, (
        "Could not find any source file containing a `scope({...})` call whose "
        "object literal declares the generic with the scoped key syntax "
        "(expected something like `\"Page<T>\": { items: \"T[]\", total: ..., "
        "cursor: ... }`)."
    )

    # The same file should also resolve PageOfUser and PageOfProduct via the scope.
    resolves_user = False
    resolves_product = False
    for fpath in matches:
        with open(fpath, encoding="utf-8") as f:
            content = f.read()
        if re.search(r"PageOfUser\s*:\s*['\"]Page\s*<\s*User\s*>['\"]", content):
            resolves_user = True
        if re.search(r"PageOfProduct\s*:\s*['\"]Page\s*<\s*Product\s*>['\"]", content):
            resolves_product = True

    assert resolves_user, (
        "Expected the scope definition to include an alias resolving "
        "`PageOfUser` via `\"Page<User>\"`."
    )
    assert resolves_product, (
        "Expected the scope definition to include an alias resolving "
        "`PageOfProduct` via `\"Page<Product>\"`."
    )


# ---------------------------------------------------------------------------
# Additional behavioural checks derived from `truth`
# ---------------------------------------------------------------------------


def test_cursor_accepts_string():
    payload = {"items": [VALID_USER], "total": 1, "cursor": "abc123"}
    result = _run_validate("PageOfUser", payload)
    assert result.returncode == 0, (
        "cursor field should accept a string value. "
        f"exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def test_cursor_rejects_number():
    payload = {"items": [VALID_USER], "total": 1, "cursor": 42}
    result = _run_validate("PageOfUser", payload)
    assert result.returncode != 0, (
        "cursor field must be `string | null`; a number should be rejected. "
        f"exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def test_arktype_version_pinned():
    """The installed arktype version reported by node must be exactly 2.2.0."""
    result = subprocess.run(
        [
            "node",
            "-e",
            "process.stdout.write(require('arktype/package.json').version)",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"Failed to read arktype's installed version: stderr={result.stderr!r}"
    )
    assert result.stdout.strip() == "2.2.0", (
        f"arktype must be installed at exactly 2.2.0, got {result.stdout.strip()!r}"
    )
