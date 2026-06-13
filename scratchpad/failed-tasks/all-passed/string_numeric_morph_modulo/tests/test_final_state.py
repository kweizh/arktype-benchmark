import json
import os
import re
import subprocess

PROJECT_DIR = "/home/user/myproject"
VALIDATE_TS = os.path.join(PROJECT_DIR, "validate.ts")


def _run_validate(payload: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["npx", "--yes", "tsx", "validate.ts", payload],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_validate_ts_exists():
    assert os.path.isfile(VALIDATE_TS), (
        f"Expected the executor to create {VALIDATE_TS}, but it does not exist."
    )


def test_validate_ts_uses_required_tuple_expression():
    """The schema for `score` must use the documented tuple expression
    ["string.numeric.parse", "|>", "number % 2"].
    """
    with open(VALIDATE_TS) as f:
        source = f.read()
    # Normalize whitespace so different formatting still matches.
    normalized = re.sub(r"\s+", "", source)
    # Both single- and double-quoted variants are accepted.
    double_quoted = '["string.numeric.parse","|>","number%2"]'
    single_quoted = "['string.numeric.parse','|>','number%2']"
    assert double_quoted in normalized or single_quoted in normalized, (
        "validate.ts must define the `score` schema using the tuple expression "
        '["string.numeric.parse", "|>", "number % 2"] '
        "(the documented ArkType pipe + modulo divisor syntax)."
    )


def test_valid_even_numeric_string_parses_to_number():
    """Criterion 1: {\"score\":\"42\"} -> OK with score===42 (number, not string)."""
    result = _run_validate('{"score":"42"}')
    assert result.returncode == 0, (
        f"Expected exit code 0 for valid input, got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "OK:" in result.stdout, (
        f"Expected stdout to contain 'OK:' for valid input. stdout={result.stdout!r}"
    )

    # Extract the JSON payload that follows the OK: prefix on a single line.
    match = re.search(r"OK:\s*(\{.*\})", result.stdout)
    assert match is not None, (
        f"Could not locate 'OK: <json>' line in stdout. stdout={result.stdout!r}"
    )
    parsed = json.loads(match.group(1))
    assert parsed == {"score": 42}, (
        f"Expected validated output to equal {{'score': 42}}, got {parsed!r}."
    )
    assert isinstance(parsed["score"], int) and not isinstance(parsed["score"], bool), (
        f"`score` must be deserialized as a JSON number, got type {type(parsed['score']).__name__}."
    )
    # Guard against the morph leaving the value as a string.
    assert not re.search(r'"score"\s*:\s*"42"', result.stdout), (
        "`score` was emitted as a string (\"42\"); the morph must convert it to the number 42."
    )


def test_odd_numeric_string_is_rejected():
    """Criterion 2: {\"score\":\"43\"} -> rejected (not divisible by 2)."""
    result = _run_validate('{"score":"43"}')
    assert result.returncode == 1, (
        f"Expected exit code 1 for odd parsed value, got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert result.stdout.lstrip().startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for odd value. stdout={result.stdout!r}"
    )


def test_non_numeric_string_is_rejected():
    """Criterion 3: {\"score\":\"abc\"} -> rejected (not numeric)."""
    result = _run_validate('{"score":"abc"}')
    assert result.returncode == 1, (
        f"Expected exit code 1 for non-numeric input, got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert result.stdout.lstrip().startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' for non-numeric value. stdout={result.stdout!r}"
    )


def test_already_number_is_rejected():
    """Criterion 4: {\"score\":42} (already a number) -> rejected (the morph requires a string input)."""
    result = _run_validate('{"score":42}')
    assert result.returncode == 1, (
        f"Expected exit code 1 when input is already a number, got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert result.stdout.lstrip().startswith("INVALID:"), (
        f"Expected stdout to start with 'INVALID:' when input is already a number. stdout={result.stdout!r}"
    )
