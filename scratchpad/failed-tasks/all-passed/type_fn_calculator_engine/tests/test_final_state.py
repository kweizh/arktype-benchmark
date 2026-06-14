import json
import os
import subprocess

PROJECT_DIR = "/home/user/myproject"
CLI_PATH = os.path.join(PROJECT_DIR, "cli.ts")


def _run_cli(payload: dict) -> subprocess.CompletedProcess[str]:
    """Invoke the calculator CLI by piping a JSON payload through stdin."""
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
# Sanity: CLI entrypoint exists
# ---------------------------------------------------------------------------


def test_cli_entrypoint_exists():
    """The CLI entrypoint required by the acceptance criteria exists."""
    assert os.path.isfile(CLI_PATH), (
        f"Expected CLI entrypoint at {CLI_PATH}."
    )


# ---------------------------------------------------------------------------
# Success-path tests (truth steps 1 & 2)
# ---------------------------------------------------------------------------


def test_valid_divide_produces_correct_result():
    """Truth step 1: divide(10, 2) -> 'OK 5'."""
    result = _run_cli({"op": "divide", "a": 10, "b": 2})
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines == ["OK 5"], (
        f"Expected stdout to be exactly ['OK 5'], got {lines!r} "
        f"(stderr={result.stderr!r})"
    )


def test_valid_add_produces_correct_result():
    """Truth step 2 (input A): add(2, 3) -> 'OK 5'."""
    result = _run_cli({"op": "add", "a": 2, "b": 3})
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines == ["OK 5"], (
        f"Expected stdout to be exactly ['OK 5'], got {lines!r} "
        f"(stderr={result.stderr!r})"
    )


def test_valid_multiply_produces_correct_result():
    """Truth step 2 (input B): multiply(-4, 2.5) -> 'OK -10'."""
    result = _run_cli({"op": "multiply", "a": -4, "b": 2.5})
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert lines == ["OK -10"], (
        f"Expected stdout to be exactly ['OK -10'], got {lines!r} "
        f"(stderr={result.stderr!r})"
    )


# ---------------------------------------------------------------------------
# type.fn rejection tests (truth steps 3-7)
# ---------------------------------------------------------------------------


def test_divide_by_zero_is_rejected_as_traversal_error():
    """Truth step 3: divide-by-zero is rejected at the type.fn boundary."""
    result = _run_cli({"op": "divide", "a": 10, "b": 0})
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert len(lines) == 1, (
        f"Expected exactly one stdout line for ERR case, got: {lines!r}"
    )
    line = lines[0]
    assert line.startswith("ERR "), (
        f"Expected stdout to start with 'ERR ' for divide-by-zero, got: {line!r}"
    )
    assert "must be" in line, (
        f"Expected ArkType TraversalError-style 'must be' phrasing in: {line!r}"
    )


def test_non_numeric_b_is_rejected_at_dispatcher_boundary():
    """Truth step 4: non-numeric `b` is rejected with a 'must be a number' message."""
    result = _run_cli({"op": "add", "a": 1, "b": "two"})
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert len(lines) == 1, (
        f"Expected exactly one stdout line for ERR case, got: {lines!r}"
    )
    line = lines[0]
    assert line.startswith("ERR "), (
        f"Expected stdout to start with 'ERR ' for non-numeric b, got: {line!r}"
    )
    assert "must be a number" in line, (
        f"Expected 'must be a number' in the TraversalError message, got: {line!r}"
    )


def test_unknown_op_is_rejected_at_dispatcher_boundary():
    """Truth step 5: an unknown op name is rejected at the dispatcher boundary."""
    result = _run_cli({"op": "power", "a": 2, "b": 3})
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert len(lines) == 1, (
        f"Expected exactly one stdout line for ERR case, got: {lines!r}"
    )
    line = lines[0]
    assert line.startswith("ERR "), (
        f"Expected stdout to start with 'ERR ' for unknown op, got: {line!r}"
    )
    assert "must be" in line, (
        f"Expected ArkType TraversalError-style 'must be' phrasing in: {line!r}"
    )


def test_modulo_by_non_integer_is_rejected():
    """Truth step 6: modulo by 2.5 is rejected at the modulo type.fn boundary."""
    result = _run_cli({"op": "modulo", "a": 10, "b": 2.5})
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert len(lines) == 1, (
        f"Expected exactly one stdout line for ERR case, got: {lines!r}"
    )
    line = lines[0]
    assert line.startswith("ERR "), (
        f"Expected stdout to start with 'ERR ' for modulo non-integer divisor, "
        f"got: {line!r}"
    )
    assert "must be" in line, (
        f"Expected ArkType TraversalError-style 'must be' phrasing in: {line!r}"
    )


def test_modulo_by_zero_is_rejected():
    """Truth step 7: modulo by 0 is rejected at the modulo type.fn boundary."""
    result = _run_cli({"op": "modulo", "a": 10, "b": 0})
    assert result.returncode == 0, (
        f"CLI exited with non-zero code: stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )
    lines = _stdout_lines(result.stdout)
    assert len(lines) == 1, (
        f"Expected exactly one stdout line for ERR case, got: {lines!r}"
    )
    line = lines[0]
    assert line.startswith("ERR "), (
        f"Expected stdout to start with 'ERR ' for modulo divisor 0, got: {line!r}"
    )
    assert "must be" in line, (
        f"Expected ArkType TraversalError-style 'must be' phrasing in: {line!r}"
    )


# ---------------------------------------------------------------------------
# Exact output-format guarantees (truth step 8)
# ---------------------------------------------------------------------------


def test_output_lines_match_strict_format_for_success_and_failure():
    """Truth step 8: every CLI invocation produces exactly one OK/ERR stdout line."""
    cases = [
        {"op": "divide", "a": 10, "b": 2},
        {"op": "add", "a": 2, "b": 3},
        {"op": "multiply", "a": -4, "b": 2.5},
        {"op": "divide", "a": 10, "b": 0},
        {"op": "add", "a": 1, "b": "two"},
        {"op": "power", "a": 2, "b": 3},
        {"op": "modulo", "a": 10, "b": 2.5},
        {"op": "modulo", "a": 10, "b": 0},
    ]
    for payload in cases:
        result = _run_cli(payload)
        assert result.returncode == 0, (
            f"CLI exited with non-zero code for {payload!r}: "
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
        lines = _stdout_lines(result.stdout)
        assert len(lines) == 1, (
            f"Expected exactly one stdout line for {payload!r}, got: {lines!r}"
        )
        line = lines[0]
        assert line.startswith("OK ") or line.startswith("ERR "), (
            f"Expected stdout line to start with 'OK ' or 'ERR ' for "
            f"{payload!r}, got: {line!r}"
        )
