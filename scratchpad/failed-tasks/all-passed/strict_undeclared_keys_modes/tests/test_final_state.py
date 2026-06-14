import json
import os
import re
import subprocess

PROJECT_DIR = "/home/user/myproject"
CLI_PATH = os.path.join(PROJECT_DIR, "cli.ts")

VALID_USER = {
    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "name": "Alice",
    "email": "alice@example.com",
}


def _run_cli(payload: dict) -> subprocess.CompletedProcess[str]:
    """Invoke the CLI by piping a JSON envelope through stdin."""
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
# Behavioural tests (Criteria 1-4)
# ---------------------------------------------------------------------------


def test_ignore_mode_preserves_extra_key():
    """Criterion 1: ignore mode validates and PRESERVES the extra key."""
    payload = {
        "mode": "ignore",
        "payload": {**VALID_USER, "role": "admin"},
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
        f"Expected validated JSON on the line after VALID, got: {lines!r}"
    )
    try:
        validated = json.loads(lines[1])
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Second stdout line is not valid JSON: {lines[1]!r} (error: {exc})"
        )
    assert validated.get("id") == VALID_USER["id"], (
        f"Validated id mismatch: {validated!r}"
    )
    assert validated.get("name") == VALID_USER["name"], (
        f"Validated name mismatch: {validated!r}"
    )
    assert validated.get("email") == VALID_USER["email"], (
        f"Validated email mismatch: {validated!r}"
    )
    assert validated.get("role") == "admin", (
        f"Extra key 'role' must be preserved in ignore mode, got: {validated!r}"
    )


def test_reject_mode_rejects_extra_key_and_names_it():
    """Criterion 2: reject mode produces INVALID containing the extra key name."""
    payload = {
        "mode": "reject",
        "payload": {**VALID_USER, "role": "admin"},
    }
    result = _run_cli(payload)
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines and lines[0].startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for reject mode, got: "
        f"{result.stdout!r}"
    )
    assert "role" in lines[0], (
        f"Expected the INVALID message to mention the undeclared key 'role', "
        f"got: {lines[0]!r}"
    )


def test_delete_mode_strips_extra_keys():
    """Criterion 3: delete mode validates with the extra keys STRIPPED."""
    payload = {
        "mode": "delete",
        "payload": {**VALID_USER, "role": "admin", "debug": True},
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
        f"Expected validated JSON on the line after VALID, got: {lines!r}"
    )
    try:
        validated = json.loads(lines[1])
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Second stdout line is not valid JSON: {lines[1]!r} (error: {exc})"
        )
    assert validated.get("id") == VALID_USER["id"], (
        f"Validated id mismatch: {validated!r}"
    )
    assert validated.get("name") == VALID_USER["name"], (
        f"Validated name mismatch: {validated!r}"
    )
    assert validated.get("email") == VALID_USER["email"], (
        f"Validated email mismatch: {validated!r}"
    )
    assert "role" not in validated, (
        f"Extra key 'role' must be stripped in delete mode, got: {validated!r}"
    )
    assert "debug" not in validated, (
        f"Extra key 'debug' must be stripped in delete mode, got: {validated!r}"
    )


def test_missing_required_field_is_rejected_in_every_mode():
    """Criterion 4: missing required field is rejected in any mode."""
    incomplete = {"id": VALID_USER["id"], "name": VALID_USER["name"]}
    for mode in ("ignore", "reject", "delete"):
        payload = {"mode": mode, "payload": incomplete}
        result = _run_cli(payload)
        assert result.returncode == 0, (
            f"[mode={mode}] CLI exited with non-zero code: "
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
        lines = _stdout_lines(result.stdout)
        assert lines and lines[0].startswith("INVALID:"), (
            f"[mode={mode}] Expected stdout to start with 'INVALID:' when "
            f"required field 'email' is missing, got: {result.stdout!r}"
        )


# ---------------------------------------------------------------------------
# Implementation-shape tests (Criterion 5)
# ---------------------------------------------------------------------------


def _collect_project_ts_sources() -> str:
    """Concatenate all .ts files under PROJECT_DIR (excluding node_modules)."""
    chunks: list[str] = []
    for root, dirs, files in os.walk(PROJECT_DIR):
        # Skip dependency directories.
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".git")]
        for name in files:
            if name.endswith(".ts"):
                path = os.path.join(root, name)
                try:
                    with open(path, encoding="utf-8") as f:
                        chunks.append(f.read())
                except OSError:
                    continue
    return "\n".join(chunks)


def test_validator_uses_plus_reject_and_plus_delete_syntax():
    """Criterion 5: source contains both `"+": "reject"` and `"+": "delete"`."""
    source = _collect_project_ts_sources()
    assert source.strip(), (
        f"No .ts source files found under {PROJECT_DIR} (excluding node_modules)."
    )

    # Accept either double- or single-quoted forms produced by common formatters.
    reject_pattern = re.compile(r"""['\"]\+['\"]\s*:\s*['\"]reject['\"]""")
    delete_pattern = re.compile(r"""['\"]\+['\"]\s*:\s*['\"]delete['\"]""")

    assert reject_pattern.search(source), (
        "Project sources must define the reject schema using the `+` operator "
        "(expected a literal like `\"+\": \"reject\"` inside an object "
        "definition)."
    )
    assert delete_pattern.search(source), (
        "Project sources must define the delete schema using the `+` operator "
        "(expected a literal like `\"+\": \"delete\"` inside an object "
        "definition)."
    )


def test_cli_entrypoint_exists():
    """Sanity: the CLI entrypoint required by the acceptance criteria exists."""
    assert os.path.isfile(CLI_PATH), (
        f"Expected CLI entrypoint at {CLI_PATH}."
    )
