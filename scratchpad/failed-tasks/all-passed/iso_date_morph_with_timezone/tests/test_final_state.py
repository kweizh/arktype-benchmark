import json
import os
import subprocess
import textwrap

PROJECT_DIR = "/home/user/myproject"
MODULE_REL_PATH = "src/parseIsoDate.ts"
MODULE_PATH = os.path.join(PROJECT_DIR, MODULE_REL_PATH)
RUNNER_PATH = os.path.join(PROJECT_DIR, "_zealt_runner.ts")
RESULT_PATH = os.path.join(PROJECT_DIR, "verify-output.json")


RUNNER_SOURCE = textwrap.dedent(
    """
    import { writeFileSync } from "node:fs";
    import { parseIsoDate } from "./src/parseIsoDate";

    type Case = {
      name: string;
      input: unknown;
      expectThrow: boolean;
      expectIsoString?: string;
    };

    const cases: Case[] = [
      {
        name: "z_suffix",
        input: "2024-01-15T10:30:00Z",
        expectThrow: false,
        expectIsoString: "2024-01-15T10:30:00.000Z",
      },
      {
        name: "plus_offset",
        input: "2024-01-15T10:30:00+05:00",
        expectThrow: false,
      },
      {
        name: "no_timezone",
        input: "2024-01-15T10:30:00",
        expectThrow: true,
      },
      {
        name: "not_a_date",
        input: "not-a-date",
        expectThrow: true,
      },
    ];

    const results: Record<string, unknown> = {};

    for (const c of cases) {
      try {
        const out = parseIsoDate(c.input as never);
        results[c.name] = {
          threw: false,
          isDate: out instanceof Date,
          iso: out instanceof Date ? out.toISOString() : null,
        };
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        results[c.name] = { threw: true, message: msg };
      }
    }

    writeFileSync("verify-output.json", JSON.stringify(results, null, 2));
    """
).strip() + "\n"


def _write_runner_and_execute():
    """Write the TypeScript runner and execute it via tsx, returning parsed JSON."""
    # Always rewrite the runner so it reflects the current verification logic.
    with open(RUNNER_PATH, "w") as f:
        f.write(RUNNER_SOURCE)
    # Remove any leftover result file from a previous run.
    if os.path.exists(RESULT_PATH):
        os.remove(RESULT_PATH)

    result = subprocess.run(
        ["npx", "--no-install", "tsx", "_zealt_runner.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        "Runner script failed to execute.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert os.path.isfile(RESULT_PATH), (
        f"Runner did not produce {RESULT_PATH}. stdout: {result.stdout!r}"
    )
    with open(RESULT_PATH) as f:
        return json.load(f)


def test_module_file_exists():
    assert os.path.isfile(MODULE_PATH), (
        f"Expected ArkType morph module at {MODULE_PATH}."
    )


def test_package_json_pins_arktype_2_2_0():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), "package.json is missing."
    with open(package_json) as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies", {}) or {})
    deps.update(data.get("devDependencies", {}) or {})
    assert deps.get("arktype") == "2.2.0", (
        f"arktype must be pinned to exactly 2.2.0, got {deps.get('arktype')!r}."
    )


def test_parse_iso_date_accepts_z_suffix():
    results = _write_runner_and_execute()
    case = results.get("z_suffix")
    assert case is not None, "Missing result for the Z-suffix case."
    assert case.get("threw") is False, (
        f'parseIsoDate("2024-01-15T10:30:00Z") must NOT throw, got: {case}'
    )
    assert case.get("isDate") is True, (
        f'parseIsoDate("2024-01-15T10:30:00Z") must return a Date instance, got: {case}'
    )
    assert case.get("iso") == "2024-01-15T10:30:00.000Z", (
        "Expected toISOString() to equal '2024-01-15T10:30:00.000Z', "
        f"got {case.get('iso')!r}."
    )


def test_parse_iso_date_accepts_plus_offset():
    results = _write_runner_and_execute()
    case = results.get("plus_offset")
    assert case is not None, "Missing result for the +HH:MM offset case."
    assert case.get("threw") is False, (
        f'parseIsoDate("2024-01-15T10:30:00+05:00") must NOT throw, got: {case}'
    )
    assert case.get("isDate") is True, (
        "parseIsoDate must return a Date instance for an explicit +HH:MM offset, "
        f"got: {case}"
    )


def test_parse_iso_date_rejects_missing_timezone():
    results = _write_runner_and_execute()
    case = results.get("no_timezone")
    assert case is not None, "Missing result for the missing-timezone case."
    assert case.get("threw") is True, (
        'parseIsoDate("2024-01-15T10:30:00") MUST throw because the input has no '
        f"explicit timezone, got: {case}"
    )


def test_parse_iso_date_rejects_non_date_string():
    results = _write_runner_and_execute()
    case = results.get("not_a_date")
    assert case is not None, "Missing result for the non-date case."
    assert case.get("threw") is True, (
        'parseIsoDate("not-a-date") MUST throw, got: {case}'.format(case=case)
    )
