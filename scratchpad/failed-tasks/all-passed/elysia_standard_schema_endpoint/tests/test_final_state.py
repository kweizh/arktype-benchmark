import os
import re
import socket
import subprocess

import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"
BASE_URL = "http://localhost:3000"


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Start the Elysia server in the background and wait for port 3000."""

    class Starter(ProcessStarter):
        name = "start_app"
        args = ["bun", "run", "start"]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 3000)) == 0

    xprocess.ensure(Starter.name, Starter)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _iter_source_files():
    """Yield paths of relevant server source files (.ts / .js) under PROJECT_DIR."""
    skip_dirs = {"node_modules", ".git", "dist", "build", ".next", ".turbo"}
    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in files:
            if name.endswith((".ts", ".tsx", ".js", ".mjs", ".cjs")):
                yield os.path.join(root, name)


def _read_all_source():
    chunks = []
    for path in _iter_source_files():
        try:
            with open(path, "r", encoding="utf-8") as f:
                chunks.append(f.read())
        except (OSError, UnicodeDecodeError):
            continue
    return "\n".join(chunks)


def test_server_reachable(start_app):
    """Criterion 6: The server MUST be reachable on http://localhost:3000."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(("localhost", 3000))
    assert result == 0, (
        "Expected the Elysia server to be reachable on http://localhost:3000 "
        f"during the test run (connect_ex returned {result})."
    )


def test_valid_body_returns_200_with_username(start_app):
    """Criterion 1: POST /user with valid body returns 200 and JSON containing the username."""
    payload = {
        "username": "alice123",
        "email": "alice@example.com",
        "age": 30,
    }
    response = requests.post(f"{BASE_URL}/user", json=payload, timeout=15)
    assert response.status_code == 200, (
        f"Expected HTTP 200 for a valid body, got {response.status_code}. "
        f"Body: {response.text!r}"
    )
    try:
        data = response.json()
    except ValueError as exc:
        raise AssertionError(
            f"Expected JSON response for a valid body, got non-JSON: {response.text!r}"
        ) from exc

    def _contains_username(obj, expected):
        if isinstance(obj, dict):
            if obj.get("username") == expected:
                return True
            return any(_contains_username(v, expected) for v in obj.values())
        if isinstance(obj, list):
            return any(_contains_username(v, expected) for v in obj)
        return False

    assert _contains_username(data, "alice123"), (
        "Expected the JSON response to contain the validated username 'alice123', "
        f"got: {data!r}"
    )


def test_underage_returns_422(start_app):
    """Criterion 2: POST /user with `age: 17` returns HTTP 422."""
    payload = {
        "username": "bob42",
        "email": "bob@example.com",
        "age": 17,
    }
    response = requests.post(f"{BASE_URL}/user", json=payload, timeout=15)
    assert response.status_code == 422, (
        f"Expected HTTP 422 when `age` is 17 (must be integer >= 18), "
        f"got {response.status_code}. Body: {response.text!r}"
    )


def test_invalid_email_returns_422(start_app):
    """Criterion 3: POST /user with `email: \"not-an-email\"` returns HTTP 422."""
    payload = {
        "username": "carol9",
        "email": "not-an-email",
        "age": 25,
    }
    response = requests.post(f"{BASE_URL}/user", json=payload, timeout=15)
    assert response.status_code == 422, (
        f"Expected HTTP 422 when `email` is 'not-an-email', "
        f"got {response.status_code}. Body: {response.text!r}"
    )


def test_extra_unknown_fields_succeed(start_app):
    """Criterion 4: POST /user with extra unknown fields MUST still succeed (ArkType ignores
    undeclared keys by default)."""
    payload = {
        "username": "dave77",
        "email": "dave@example.com",
        "age": 40,
        "role": "admin",
        "nickname": "d",
    }
    response = requests.post(f"{BASE_URL}/user", json=payload, timeout=15)
    assert response.status_code == 200, (
        "Expected HTTP 200 when extra unknown fields are present "
        "(ArkType ignores undeclared keys by default); "
        f"got {response.status_code}. Body: {response.text!r}"
    )
    try:
        data = response.json()
    except ValueError as exc:
        raise AssertionError(
            f"Expected JSON response for a valid body with extras, got non-JSON: {response.text!r}"
        ) from exc

    def _contains_username(obj, expected):
        if isinstance(obj, dict):
            if obj.get("username") == expected:
                return True
            return any(_contains_username(v, expected) for v in obj.values())
        if isinstance(obj, list):
            return any(_contains_username(v, expected) for v in obj)
        return False

    assert _contains_username(data, "dave77"), (
        "Expected the JSON response to contain the validated username 'dave77' "
        f"when extra fields are sent, got: {data!r}"
    )


def test_body_validator_is_arktype_type_not_t_object(start_app):
    """Criterion 5: The body validator MUST be a `type({...})` ArkType instance passed
    directly to Elysia's `body:` option (NOT wrapped in `t.Object`)."""
    source = _read_all_source()
    assert source.strip(), (
        f"No server source files (.ts/.js) found under {PROJECT_DIR} to inspect."
    )

    # Must import the ArkType `type` function from "arktype".
    arktype_import_pattern = re.compile(
        r"""from\s+['"]arktype['"]""", re.MULTILINE
    )
    assert arktype_import_pattern.search(source), (
        "Expected at least one import from \"arktype\" in the server source "
        "(the `type` function must come from the `arktype` package)."
    )

    # The `body:` option must be assigned a value that uses ArkType's `type({...})`
    # constructor — either directly inline or via a variable that was created with
    # `type({...})`. We accept both shapes.
    body_inline_pattern = re.compile(
        r"body\s*:\s*type\s*\(\s*\{", re.MULTILINE
    )
    body_var_pattern = re.compile(
        r"body\s*:\s*([A-Za-z_$][\w$]*)\b", re.MULTILINE
    )

    inline_match = body_inline_pattern.search(source)
    var_match = None
    if not inline_match:
        for candidate in body_var_pattern.finditer(source):
            name = candidate.group(1)
            # Skip the literal token `type` itself; that was handled above.
            if name == "type":
                continue
            decl_pattern = re.compile(
                rf"\b(?:const|let|var)\s+{re.escape(name)}\s*=\s*type\s*\(\s*\{{",
                re.MULTILINE,
            )
            if decl_pattern.search(source):
                var_match = (name, candidate)
                break

    assert inline_match or var_match, (
        "Expected the Elysia `body:` option to be a `type({...})` ArkType instance "
        "(either inline `body: type({ ... })` or `body: SomeSchema` where "
        "`SomeSchema = type({ ... })`). None was found in the server source."
    )

    # The `body:` option MUST NOT be wrapped in Elysia's `t.Object`.
    body_t_object_pattern = re.compile(
        r"body\s*:\s*t\s*\.\s*Object\s*\(", re.MULTILINE
    )
    forbidden = body_t_object_pattern.search(source)
    assert forbidden is None, (
        "The body validator MUST NOT be wrapped in Elysia's `t.Object`. "
        f"Found forbidden usage in source near: {source[max(0, forbidden.start()-40):forbidden.end()+40]!r}"
    )
