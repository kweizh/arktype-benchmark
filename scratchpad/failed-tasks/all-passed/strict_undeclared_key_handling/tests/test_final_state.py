import json
import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCHEMAS_PATH = os.path.join(PROJECT_DIR, "src", "schemas.ts")
PACKAGE_JSON_PATH = os.path.join(PROJECT_DIR, "package.json")
VERIFIER_TS_PATH = os.path.join(PROJECT_DIR, ".verify.ts")

VERIFIER_SCRIPT = r"""
import { type } from "arktype";
import { LooseUser, RejectUser, DeleteUser } from "./src/schemas";

const results: Record<string, boolean> = {
  a: false,
  b: false,
  c: false,
  d: false,
  e: false,
  f: false,
};

try {
  const r = (LooseUser as any)({ name: "a", extra: 1 });
  results.a = !(r instanceof (type as any).errors) && r && (r as any).extra === 1;
} catch (_e) {
  results.a = false;
}

try {
  const r = (RejectUser as any)({ name: "a", extra: 1 });
  results.b = r instanceof (type as any).errors;
} catch (_e) {
  results.b = false;
}

try {
  const r = (DeleteUser as any)({ name: "a", extra: 1 });
  results.c =
    !(r instanceof (type as any).errors) &&
    r &&
    typeof r === "object" &&
    !("extra" in (r as any));
} catch (_e) {
  results.c = false;
}

try {
  const r = (LooseUser as any)({ name: "a" });
  results.d = !(r instanceof (type as any).errors);
} catch (_e) {
  results.d = false;
}

try {
  const r = (RejectUser as any)({ name: "a" });
  results.e = !(r instanceof (type as any).errors);
} catch (_e) {
  results.e = false;
}

try {
  const r = (DeleteUser as any)({ name: "a" });
  results.f = !(r instanceof (type as any).errors);
} catch (_e) {
  results.f = false;
}

process.stdout.write(JSON.stringify(results));
"""


@pytest.fixture(scope="session")
def verifier_output():
    # 1. Pinned version check on package.json
    assert os.path.isfile(PACKAGE_JSON_PATH), (
        f"package.json not found at {PACKAGE_JSON_PATH}."
    )
    with open(PACKAGE_JSON_PATH) as f:
        pkg = json.load(f)
    deps = pkg.get("dependencies", {})
    assert deps.get("arktype") == "2.2.0", (
        f"Expected dependencies.arktype to be pinned to '2.2.0' in package.json, "
        f"got {deps.get('arktype')!r}."
    )

    # 2. Module exists
    assert os.path.isfile(SCHEMAS_PATH), (
        f"Expected schemas module at {SCHEMAS_PATH} but it does not exist."
    )

    # 3. Write the verifier TS script
    with open(VERIFIER_TS_PATH, "w") as f:
        f.write(VERIFIER_SCRIPT)

    try:
        # 4. Run via npx tsx
        result = subprocess.run(
            ["npx", "tsx", ".verify.ts"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR,
            timeout=180,
        )
        assert result.returncode == 0, (
            f"`npx tsx .verify.ts` failed with exit code {result.returncode}.\n"
            f"stdout: {result.stdout!r}\n"
            f"stderr: {result.stderr!r}"
        )

        # 5. Parse the JSON document on stdout
        stdout = result.stdout.strip()
        # Tolerate any trailing/leading non-JSON noise by locating the first '{' ... '}' block.
        start = stdout.find("{")
        end = stdout.rfind("}")
        assert start != -1 and end != -1 and end > start, (
            f"Could not find JSON object in verifier stdout: {result.stdout!r}"
        )
        try:
            data = json.loads(stdout[start : end + 1])
        except json.JSONDecodeError as e:
            raise AssertionError(
                f"Failed to parse JSON from verifier stdout {stdout!r}: {e}"
            )

        yield data
    finally:
        if os.path.isfile(VERIFIER_TS_PATH):
            os.remove(VERIFIER_TS_PATH)


def test_arktype_version_pinned():
    """package.json must pin arktype to exactly '2.2.0' (no caret/tilde)."""
    with open(PACKAGE_JSON_PATH) as f:
        pkg = json.load(f)
    deps = pkg.get("dependencies", {})
    assert deps.get("arktype") == "2.2.0", (
        f"Expected dependencies.arktype to be pinned to '2.2.0', got {deps.get('arktype')!r}."
    )


def test_schemas_module_exists():
    """src/schemas.ts must exist and export the three named schemas."""
    assert os.path.isfile(SCHEMAS_PATH), (
        f"Expected schemas module at {SCHEMAS_PATH}, but it does not exist."
    )
    with open(SCHEMAS_PATH) as f:
        source = f.read()
    for export_name in ("LooseUser", "RejectUser", "DeleteUser"):
        assert export_name in source, (
            f"Expected named export `{export_name}` to be defined in {SCHEMAS_PATH}, "
            "but it was not found in the source."
        )


def test_loose_user_preserves_extra_keys(verifier_output):
    """LooseUser({ name: 'a', extra: 1 }) must return an object where extra === 1."""
    assert verifier_output.get("a") is True, (
        "Expected LooseUser({ name: 'a', extra: 1 }) to return an object with extra === 1 "
        "(using ArkType's default 'ignore' undeclared-key strategy)."
    )


def test_reject_user_rejects_extra_keys(verifier_output):
    """RejectUser({ name: 'a', extra: 1 }) must return a type.errors instance."""
    assert verifier_output.get("b") is True, (
        "Expected RejectUser({ name: 'a', extra: 1 }) to return a `type.errors` instance "
        "(must be configured with `+`: 'reject' so that undeclared keys cause validation failure)."
    )


def test_delete_user_strips_extra_keys(verifier_output):
    """DeleteUser({ name: 'a', extra: 1 }) must return an object where 'extra' in result === false."""
    assert verifier_output.get("c") is True, (
        "Expected DeleteUser({ name: 'a', extra: 1 }) to return an object that does NOT contain "
        "the `extra` key (must be configured with `+`: 'delete' so that undeclared keys are stripped)."
    )


def test_loose_user_accepts_only_declared(verifier_output):
    """LooseUser({ name: 'a' }) must succeed (no error)."""
    assert verifier_output.get("d") is True, (
        "Expected LooseUser({ name: 'a' }) to succeed without returning a `type.errors` instance."
    )


def test_reject_user_accepts_only_declared(verifier_output):
    """RejectUser({ name: 'a' }) must succeed (no error)."""
    assert verifier_output.get("e") is True, (
        "Expected RejectUser({ name: 'a' }) to succeed without returning a `type.errors` instance."
    )


def test_delete_user_accepts_only_declared(verifier_output):
    """DeleteUser({ name: 'a' }) must succeed (no error)."""
    assert verifier_output.get("f") is True, (
        "Expected DeleteUser({ name: 'a' }) to succeed without returning a `type.errors` instance."
    )
