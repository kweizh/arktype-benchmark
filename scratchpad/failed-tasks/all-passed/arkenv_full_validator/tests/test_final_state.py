import json
import os
import re
import subprocess

import pytest


PROJECT_DIR = "/home/user/myproject"
ENV_MODULE = os.path.join(PROJECT_DIR, "src", "env.ts")
PRINT_SCRIPT = os.path.join(PROJECT_DIR, "scripts", "print-env.ts")

VALID_ENV = {
    "HOST": "127.0.0.1",
    "PORT": "8080",
    "DEBUG": "true",
    "NODE_ENV": "production",
    "ALLOWED_ORIGINS": "https://a.com,https://b.com",
}


def _run_command(overrides: dict, *, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run the executor's print-env command with the supplied env overrides.

    Inherits PATH and node-related env vars from the host process but **does not**
    leak HOST/PORT/DEBUG/NODE_ENV/ALLOWED_ORIGINS from the host; only the ones
    explicitly supplied are passed.
    """
    env = {}
    # Keep only the bare minimum needed for node/npm/npx to function.
    for key in ("PATH", "HOME", "LANG", "LC_ALL", "NODE_PATH", "USER", "SHELL"):
        if key in os.environ:
            env[key] = os.environ[key]
    env.update(overrides)
    return subprocess.run(
        ["npx", "tsx", PRINT_SCRIPT],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=env,
        timeout=timeout,
    )


def _extract_env_json(stdout: str) -> dict:
    match = re.search(r"^ENV_JSON=(.+)$", stdout, flags=re.MULTILINE)
    assert match is not None, (
        f"Could not find a line beginning with 'ENV_JSON=' in stdout:\n{stdout}"
    )
    payload = match.group(1).strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        pytest.fail(f"ENV_JSON payload is not valid JSON: {exc}\nPayload: {payload!r}")


def test_env_module_file_exists():
    assert os.path.isfile(ENV_MODULE), (
        f"Expected the typed env module at {ENV_MODULE}."
    )


def test_print_script_file_exists():
    assert os.path.isfile(PRINT_SCRIPT), (
        f"Expected the print-env script at {PRINT_SCRIPT}."
    )


def test_package_json_has_pinned_dependencies():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), (
        f"Expected package.json at {package_json_path}."
    )
    with open(package_json_path) as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies") or {})
    deps.update(pkg.get("devDependencies") or {})

    arkenv_version = deps.get("arkenv")
    arktype_version = deps.get("arktype")
    assert arkenv_version is not None, "arkenv must be declared in package.json."
    assert arktype_version is not None, "arktype must be declared in package.json."
    assert "0.12.1" in arkenv_version, (
        f"arkenv must be pinned to 0.12.1, got {arkenv_version!r}."
    )
    assert "2.2.0" in arktype_version, (
        f"arktype must be pinned to 2.2.0, got {arktype_version!r}."
    )


# --- Behavioural tests (1-5 from instruction.md) ---------------------------------


def test_1_all_valid_env_loads_and_coerces_types():
    """Criterion 1: With all env vars set validly, env.PORT must be a real number,
    env.DEBUG a real boolean, and env.ALLOWED_ORIGINS a non-empty Array."""
    result = _run_command(dict(VALID_ENV))
    assert result.returncode == 0, (
        f"Expected exit code 0 with valid env, got {result.returncode}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    data = _extract_env_json(result.stdout)
    types = data.get("types") or {}

    assert types.get("PORT") == "number", (
        f"env.PORT must be a JavaScript number, got typeof = {types.get('PORT')!r}."
    )
    assert data.get("PORT") == 8080, (
        f"env.PORT must equal the integer 8080, got {data.get('PORT')!r}."
    )


def test_2_debug_is_real_boolean_when_true():
    """Criterion 2: env.DEBUG must be a real boolean when set to 'true'."""
    result = _run_command(dict(VALID_ENV))
    assert result.returncode == 0, (
        f"Expected exit code 0 with valid env, got {result.returncode}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    data = _extract_env_json(result.stdout)
    types = data.get("types") or {}

    assert types.get("DEBUG") == "boolean", (
        f"env.DEBUG must be a JavaScript boolean, got typeof = {types.get('DEBUG')!r}."
    )
    assert data.get("DEBUG") is True, (
        f"env.DEBUG must be the literal boolean true, got {data.get('DEBUG')!r}."
    )


def test_3_allowed_origins_is_non_empty_array():
    """Criterion 3: env.ALLOWED_ORIGINS must be an Array of length > 0 when set
    to 'https://a.com,https://b.com'."""
    result = _run_command(dict(VALID_ENV))
    assert result.returncode == 0, (
        f"Expected exit code 0 with valid env, got {result.returncode}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    data = _extract_env_json(result.stdout)
    types = data.get("types") or {}
    origins = data.get("ALLOWED_ORIGINS")

    assert types.get("ALLOWED_ORIGINS_IS_ARRAY") is True, (
        "env.ALLOWED_ORIGINS must be a real JavaScript Array "
        "(Array.isArray(env.ALLOWED_ORIGINS) must be true)."
    )
    assert isinstance(origins, list) and len(origins) > 0, (
        f"env.ALLOWED_ORIGINS must be a non-empty array, got {origins!r}."
    )


def test_4_invalid_port_throws_at_startup():
    """Criterion 4: With PORT='not-a-number', import MUST throw at startup."""
    overrides = dict(VALID_ENV)
    overrides["PORT"] = "not-a-number"
    result = _run_command(overrides)
    assert result.returncode != 0, (
        "Expected a non-zero exit code when PORT is not a number; "
        f"got exit code {result.returncode}.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert "ENV_JSON=" not in result.stdout, (
        "env module must not load when PORT is invalid; "
        f"unexpected ENV_JSON output:\n{result.stdout}"
    )
    combined = (result.stdout + "\n" + result.stderr).lower()
    assert "port" in combined, (
        f"Expected validation error mentioning PORT.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_5_invalid_node_env_throws_at_startup():
    """Criterion 5: With NODE_ENV='staging', import MUST throw at startup."""
    overrides = dict(VALID_ENV)
    overrides["NODE_ENV"] = "staging"
    result = _run_command(overrides)
    assert result.returncode != 0, (
        "Expected a non-zero exit code when NODE_ENV is not in the allowed enum; "
        f"got exit code {result.returncode}.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert "ENV_JSON=" not in result.stdout, (
        "env module must not load when NODE_ENV is invalid; "
        f"unexpected ENV_JSON output:\n{result.stdout}"
    )
    combined = (result.stdout + "\n" + result.stderr).lower()
    assert "node_env" in combined, (
        f"Expected validation error mentioning NODE_ENV.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_6_localhost_accepted_and_bad_ip_rejected():
    """Criterion 6: HOST='localhost' MUST be accepted; HOST='999.999.999.999' MUST be rejected."""
    # localhost accepted
    overrides = dict(VALID_ENV)
    overrides["HOST"] = "localhost"
    ok = _run_command(overrides)
    assert ok.returncode == 0, (
        "Expected exit code 0 when HOST=localhost; "
        f"got {ok.returncode}.\nSTDOUT:\n{ok.stdout}\nSTDERR:\n{ok.stderr}"
    )
    data = _extract_env_json(ok.stdout)
    assert data.get("HOST") == "localhost", (
        f"env.HOST must be the literal 'localhost', got {data.get('HOST')!r}."
    )

    # 999.999.999.999 rejected
    overrides = dict(VALID_ENV)
    overrides["HOST"] = "999.999.999.999"
    bad = _run_command(overrides)
    assert bad.returncode != 0, (
        "Expected a non-zero exit code when HOST is an invalid IP; "
        f"got exit code {bad.returncode}.\nSTDOUT:\n{bad.stdout}\nSTDERR:\n{bad.stderr}"
    )
    assert "ENV_JSON=" not in bad.stdout, (
        "env module must not load when HOST is an invalid IP; "
        f"unexpected ENV_JSON output:\n{bad.stdout}"
    )
    combined = (bad.stdout + "\n" + bad.stderr).lower()
    assert "host" in combined, (
        f"Expected validation error mentioning HOST.\nSTDOUT:\n{bad.stdout}\nSTDERR:\n{bad.stderr}"
    )
