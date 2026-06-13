import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCHEMA_PATH = os.path.join(PROJECT_DIR, "src", "schema.ts")
HARNESS_PATH = "/tmp/verify-password.ts"

SHORT_PASSWORD = "weakpwd"  # 7 characters, < 8 -> must fail validation.
LONG_PASSWORD = "longenoughpw"  # 12 characters, >= 8 -> must validate successfully.

HARNESS_SOURCE = r"""
import { type } from "arktype";
import { PasswordSchema } from "__SCHEMA_PATH__";

function describe(value: unknown) {
    if (value instanceof (type as any).errors) {
        const errs = value as any;
        let summary = "";
        try {
            summary = String(errs.summary ?? "");
        } catch {
            summary = "";
        }
        if (!summary) {
            try {
                summary = String(errs);
            } catch {
                summary = "";
            }
        }
        return { isError: true, message: summary };
    }
    return { isError: false, message: "" };
}

const short = describe(PasswordSchema("__SHORT_PWD__"));
const long = describe(PasswordSchema("__LONG_PWD__"));

const out = {
    shortIsError: short.isError,
    shortMessage: short.message,
    longIsError: long.isError,
};

process.stdout.write("__ZEALT_VERIFY__" + JSON.stringify(out) + "\n");
"""


@pytest.fixture(scope="module")
def harness_output():
    assert os.path.isfile(SCHEMA_PATH), (
        f"Expected schema file at {SCHEMA_PATH}; agent must export PasswordSchema "
        f"from this path."
    )

    if os.path.exists(HARNESS_PATH):
        os.remove(HARNESS_PATH)

    schema_module = SCHEMA_PATH[:-3] if SCHEMA_PATH.endswith(".ts") else SCHEMA_PATH
    source = (
        HARNESS_SOURCE.replace("__SCHEMA_PATH__", schema_module)
        .replace("__SHORT_PWD__", SHORT_PASSWORD)
        .replace("__LONG_PWD__", LONG_PASSWORD)
    )

    with open(HARNESS_PATH, "w") as f:
        f.write(source)

    result = subprocess.run(
        ["npx", "--yes", "tsx", HARNESS_PATH],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=180,
    )
    assert result.returncode == 0, (
        f"Verifier harness failed to run (exit={result.returncode}). "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}."
    )

    marker = "__ZEALT_VERIFY__"
    json_line = None
    for line in result.stdout.splitlines():
        if marker in line:
            json_line = line.split(marker, 1)[1].strip()
            break
    assert json_line is not None, (
        f"Could not find verifier marker in stdout. stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}."
    )

    try:
        parsed = json.loads(json_line)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Verifier did not emit valid JSON: {json_line!r}; error={exc}"
        )
    return parsed


def test_short_password_triggers_validation_error(harness_output):
    assert harness_output.get("shortIsError") is True, (
        f"Expected a password of length 7 (\"{SHORT_PASSWORD}\") to produce a "
        f"validation error (ArkErrors), but PasswordSchema accepted it. "
        f"Harness output: {harness_output!r}."
    )


def test_short_password_error_contains_redacted_literal(harness_output):
    message = harness_output.get("shortMessage", "")
    assert "<redacted>" in message, (
        f"Expected the validation error message to contain the literal substring "
        f"'<redacted>'. Got message: {message!r}."
    )


def test_short_password_error_does_not_reveal_actual_value(harness_output):
    message = harness_output.get("shortMessage", "")
    assert SHORT_PASSWORD not in message, (
        f"Expected the validation error message to NOT contain the actual password "
        f"value {SHORT_PASSWORD!r}; the `actual` error config must redact it. "
        f"Got message: {message!r}."
    )
    # Also make sure no obvious leak of the raw characters appears wrapped in quotes.
    assert not re.search(re.escape(SHORT_PASSWORD), message), (
        f"Validation error leaks the actual password value. message={message!r}."
    )


def test_long_password_validates_successfully(harness_output):
    assert harness_output.get("longIsError") is False, (
        f"Expected a password of length >= 8 (\"{LONG_PASSWORD}\") to validate "
        f"successfully (no ArkErrors). Harness output: {harness_output!r}."
    )
