import json
import os
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
VERIFY_DIR = os.path.join(PROJECT_DIR, ".verify")
DRAFT_URI = "https://json-schema.org/draft/2020-12/schema"

SCHEMA_DEFINITION = {
    "id": "string.uuid",
    "profile": {
        "email": "string.email",
        "age": "number.integer",
    },
}

VALID_PAYLOAD = {
    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "profile": {"email": "alice@example.com", "age": 30},
}

INVALID_EMAIL = {
    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "profile": {"email": "not-an-email", "age": 30},
}

INVALID_AGE = {
    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "profile": {"email": "alice@example.com", "age": 30.5},
}

INVALID_UUID = {
    "id": "not-a-uuid",
    "profile": {"email": "alice@example.com", "age": 30},
}

MISSING_AGE = {
    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "profile": {"email": "alice@example.com"},
}

CORPUS = [VALID_PAYLOAD, INVALID_EMAIL, INVALID_AGE, INVALID_UUID, MISSING_AGE]
EXPECTED_AGREEMENTS = [True, False, False, False, False]


HARNESS_SOURCE = r"""
import { type } from "arktype";
import { roundTrip, exportJsonSchema } from "../src/roundTrip.ts";

const schemaDefinition = {
  id: "string.uuid",
  profile: {
    email: "string.email",
    age: "number.integer",
  },
} as const;

const corpus: unknown[] = JSON.parse(process.env.HARNESS_CORPUS ?? "[]");

const original = type(schemaDefinition);
const reparsed = roundTrip(original);
const jsonSchema = exportJsonSchema(original);

const results = corpus.map((payload, index) => {
  const originalAccept = original.allows(payload);
  const roundTrippedAccept = reparsed.allows(payload);
  return {
    index,
    originalAccept,
    roundTrippedAccept,
    agree: originalAccept === roundTrippedAccept,
  };
});

const output = {
  typeofRoundTrip: typeof roundTrip,
  typeofExportJsonSchema: typeof exportJsonSchema,
  jsonSchema,
  results,
  allAgree: results.every((r) => r.agree),
};

process.stdout.write(JSON.stringify(output));
""".lstrip()


@pytest.fixture(scope="module", autouse=True)
def setup_verify_dir():
    if os.path.isdir(VERIFY_DIR):
        shutil.rmtree(VERIFY_DIR)
    os.makedirs(VERIFY_DIR, exist_ok=True)
    harness_path = os.path.join(VERIFY_DIR, "harness.ts")
    with open(harness_path, "w") as f:
        f.write(HARNESS_SOURCE)
    yield
    # leave directory intact for debugging


def _run_harness(corpus):
    env = os.environ.copy()
    env["HARNESS_CORPUS"] = json.dumps(corpus)
    result = subprocess.run(
        ["npx", "--no-install", "tsx", os.path.join(VERIFY_DIR, "harness.ts")],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=180,
    )
    assert result.returncode == 0, (
        "Harness execution failed.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"Harness stdout was not valid JSON: {exc}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )


@pytest.fixture(scope="module")
def harness_output():
    return _run_harness(CORPUS)


def test_round_trip_module_exports_required_symbols(harness_output):
    assert harness_output["typeofRoundTrip"] == "function", (
        "src/roundTrip.ts must export a named symbol `roundTrip` of type function."
    )
    assert harness_output["typeofExportJsonSchema"] == "function", (
        "src/roundTrip.ts must export a named symbol `exportJsonSchema` of type function."
    )


def test_exported_json_schema_contains_draft_2020_12(harness_output):
    json_schema = harness_output["jsonSchema"]
    assert isinstance(json_schema, dict), "exportJsonSchema must return an object."
    assert "$schema" in json_schema, (
        "Exported JSON Schema must contain the `$schema` field."
    )
    assert json_schema["$schema"] == DRAFT_URI, (
        f"`$schema` must equal `{DRAFT_URI}` (got {json_schema['$schema']!r})."
    )


def test_round_trip_agreement_on_nested_schema(harness_output):
    results = harness_output["results"]
    assert len(results) == len(CORPUS), (
        f"Harness must report agreement for every payload in the corpus "
        f"(expected {len(CORPUS)}, got {len(results)})."
    )
    for idx, expected_accept in enumerate(EXPECTED_AGREEMENTS):
        entry = results[idx]
        assert entry["originalAccept"] is expected_accept, (
            f"Original schema disagreed on payload index {idx}: "
            f"expected accept={expected_accept}, got {entry['originalAccept']}."
        )
        assert entry["roundTrippedAccept"] is expected_accept, (
            f"Round-tripped schema disagreed on payload index {idx}: "
            f"expected accept={expected_accept}, got {entry['roundTrippedAccept']}."
        )
        assert entry["agree"] is True, (
            f"Original and round-tripped schemas disagreed on payload index {idx}."
        )
    assert harness_output["allAgree"] is True, (
        "Round-trip must agree on every payload in the corpus."
    )


def test_npm_run_check_round_trips_corpus():
    stdin_payload = json.dumps({"schema": SCHEMA_DEFINITION, "corpus": CORPUS})
    result = subprocess.run(
        ["npm", "run", "--silent", "check"],
        cwd=PROJECT_DIR,
        input=stdin_payload,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        "`npm run check` must exit with code 0 when all payloads agree.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"`npm run check` stdout was not valid JSON: {exc}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    assert "jsonSchema" in output, "`npm run check` output must include `jsonSchema`."
    assert output["jsonSchema"].get("$schema") == DRAFT_URI, (
        f"`npm run check` jsonSchema.$schema must equal `{DRAFT_URI}` "
        f"(got {output['jsonSchema'].get('$schema')!r})."
    )
    agreements = output.get("agreements", [])
    assert isinstance(agreements, list) and len(agreements) == len(CORPUS), (
        f"`npm run check` must report agreements for every payload "
        f"(expected {len(CORPUS)}, got {len(agreements)})."
    )
    for idx, entry in enumerate(agreements):
        assert entry.get("agree") is True, (
            f"`npm run check` reported disagreement on payload index {idx}: {entry}."
        )
    assert output.get("allAgree") is True, (
        "`npm run check` must report allAgree=true when every payload agrees."
    )


def test_npm_run_check_handles_string_payload_without_throwing():
    payload = {"schema": SCHEMA_DEFINITION, "corpus": ["not-an-object"]}
    result = subprocess.run(
        ["npm", "run", "--silent", "check"],
        cwd=PROJECT_DIR,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        "`npm run check` must exit 0 when both schemas reject a non-object payload.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"`npm run check` stdout was not valid JSON: {exc}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    assert output.get("allAgree") is True, (
        "Both original and round-tripped schemas must reject a non-object payload."
    )
    agreements = output.get("agreements", [])
    assert len(agreements) == 1 and agreements[0].get("agree") is True, (
        f"Expected a single agreeing rejection for the string payload, got: {agreements}."
    )
