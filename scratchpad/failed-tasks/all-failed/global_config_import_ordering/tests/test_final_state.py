import os
import re
import subprocess

PROJECT_DIR = "/home/user/myproject"
CONFIG_TS = os.path.join(PROJECT_DIR, "config.ts")
INDEX_TS = os.path.join(PROJECT_DIR, "index.ts")
BROKEN_TS = os.path.join(PROJECT_DIR, "broken.ts")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_config_ts_exists():
    assert os.path.isfile(CONFIG_TS), f"{CONFIG_TS} must exist."


def test_index_ts_exists():
    assert os.path.isfile(INDEX_TS), f"{INDEX_TS} must exist."


def test_broken_ts_exists():
    assert os.path.isfile(BROKEN_TS), f"{BROKEN_TS} must exist."


def test_config_ts_imports_configure_from_arktype_config():
    content = _read(CONFIG_TS)
    # Allow single or double quotes, and either named imports with extra members or just `configure`.
    pattern = re.compile(
        r"""import\s*\{[^}]*\bconfigure\b[^}]*\}\s*from\s*["']arktype/config["']""",
        re.DOTALL,
    )
    assert pattern.search(content), (
        "config.ts MUST contain `import { configure } from \"arktype/config\"` "
        "(the dedicated entrypoint that applies config before built-in keywords are compiled)."
    )


def test_config_ts_calls_configure_with_required_options():
    content = _read(CONFIG_TS)
    assert re.search(r"\bconfigure\s*\(", content), (
        "config.ts MUST contain a `configure({...})` call."
    )
    # Must set numberAllowsNaN: true so { x: NaN } can be accepted globally.
    assert re.search(r"numberAllowsNaN\s*:\s*true\b", content), (
        "config.ts must set `numberAllowsNaN: true` inside the configure(...) call."
    )
    # Must also set exactOptionalPropertyTypes: false as required by the task concept.
    assert re.search(r"exactOptionalPropertyTypes\s*:\s*false\b", content), (
        "config.ts must set `exactOptionalPropertyTypes: false` inside the configure(...) call."
    )


def test_index_and_broken_share_schema_module():
    """Both scripts must reference the same shared schema module (no inline duplication)."""
    index_src = _read(INDEX_TS)
    broken_src = _read(BROKEN_TS)

    # Identify all local (relative) imports in each file, excluding the config import.
    local_import_re = re.compile(
        r"""import\s+(?:[^"';]+?\s+from\s+)?["'](\.\.?/[^"']+)["']""",
    )
    index_locals = {
        m.group(1)
        for m in local_import_re.finditer(index_src)
        if "config" not in m.group(1).lower()
    }
    broken_locals = {
        m.group(1)
        for m in local_import_re.finditer(broken_src)
        if "config" not in m.group(1).lower()
    }

    shared = index_locals & broken_locals
    assert shared, (
        "index.ts and broken.ts MUST both import the schema from the same shared local module. "
        f"index.ts local imports: {sorted(index_locals)}, broken.ts local imports: {sorted(broken_locals)}."
    )

    # Sanity check: the shared module file should actually exist on disk (after resolving
    # common TypeScript extensions).
    found_existing = False
    for spec in shared:
        # Normalize path relative to PROJECT_DIR
        base = os.path.normpath(os.path.join(PROJECT_DIR, spec))
        candidates = [
            base,
            base + ".ts",
            base + ".tsx",
            base + ".js",
            os.path.join(base, "index.ts"),
            os.path.join(base, "index.tsx"),
            os.path.join(base, "index.js"),
        ]
        if any(os.path.isfile(c) for c in candidates):
            found_existing = True
            break
    assert found_existing, (
        f"The shared module(s) {sorted(shared)} referenced by both index.ts and broken.ts "
        "must resolve to an existing file under the project directory."
    )

    # Guard against inline duplication: neither file should contain its own inline
    # `type({...})` call defining the schema, because then the schemas would not
    # be coming from a shared module.
    # Heuristic: count top-level `type({` occurrences in each file.
    inline_type_calls_index = len(re.findall(r"\btype\s*\(\s*\{", index_src))
    inline_type_calls_broken = len(re.findall(r"\btype\s*\(\s*\{", broken_src))
    assert inline_type_calls_index == 0 and inline_type_calls_broken == 0, (
        "Neither index.ts nor broken.ts should define the schema inline with `type({ ... })`. "
        "They must import it from a shared module so that the schema definition is identical."
    )


def test_index_ts_accepts_nan():
    """`tsx index.ts` must validate { x: NaN } successfully (numberAllowsNaN: true takes effect)."""
    result = subprocess.run(
        ["npx", "--no-install", "tsx", "index.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"`tsx index.ts` exited with code {result.returncode}. "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    combined = result.stdout + result.stderr
    # Accept any reasonable success marker: "VALID", "valid", JSON of the parsed object,
    # or absence of an ArkType rejection message.
    looks_valid = (
        re.search(r"\bVALID\b", combined, re.IGNORECASE) is not None
        or "must be a number" not in combined
    )
    assert looks_valid, (
        "index.ts must indicate that { x: NaN } was accepted by the schema. "
        f"Got output: {combined!r}"
    )
    # And explicitly must NOT print an ArkType rejection complaining about NaN.
    assert "must be a number (was NaN)" not in combined, (
        "index.ts unexpectedly rejected NaN. Did you import './config' before 'arktype'? "
        f"Output: {combined!r}"
    )


def test_broken_ts_rejects_nan():
    """`tsx broken.ts` must reject { x: NaN } because the config was applied too late."""
    result = subprocess.run(
        ["npx", "--no-install", "tsx", "broken.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"`tsx broken.ts` must exit cleanly (exit 0) and print a rejection marker, "
        f"not crash. Got exit {result.returncode}. "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    combined = result.stdout + result.stderr
    looks_rejected = (
        re.search(r"\bINVALID\b", combined, re.IGNORECASE) is not None
        or "must be a number" in combined
    )
    assert looks_rejected, (
        "broken.ts must indicate that { x: NaN } was rejected (e.g. print 'INVALID' "
        "or an ArkType error like 'must be a number (was NaN)'). "
        f"Got output: {combined!r}"
    )
