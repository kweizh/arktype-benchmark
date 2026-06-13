import json
import os
import re
import subprocess
import tempfile
import textwrap

import pytest

PROJECT_DIR = "/home/user/myproject"
INDEX_TS = os.path.join(PROJECT_DIR, "src", "index.ts")
PACKAGE_JSON = os.path.join(PROJECT_DIR, "package.json")


def _read_source() -> str:
    with open(INDEX_TS) as f:
        return f.read()


def _strip_comments(src: str) -> str:
    # Remove block comments and line comments to make pattern checks robust.
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def test_index_ts_exists():
    assert os.path.isfile(INDEX_TS), f"Expected source file at {INDEX_TS}."


def test_package_json_arktype_pinned():
    assert os.path.isfile(PACKAGE_JSON), f"Expected {PACKAGE_JSON} to exist."
    with open(PACKAGE_JSON) as f:
        pkg = json.load(f)
    deps = pkg.get("dependencies", {})
    assert deps.get("arktype") == "2.2.0", (
        f"dependencies.arktype in package.json must be exactly '2.2.0', got {deps.get('arktype')!r}."
    )


def test_uses_scope_and_export():
    src = _strip_comments(_read_source())
    assert re.search(r"\bscope\s*\(", src), (
        "Source must construct the schema using `scope({ Member: { ... } })`."
    )
    assert ".export(" in src, (
        "Source must call `.export()` on the scope to obtain the Module."
    )


def test_uses_optional_key_syntax():
    src = _strip_comments(_read_source())
    assert re.search(r"""['"]manager\?['"]""", src), (
        "`manager` must be declared with optional-key syntax, e.g. \"manager?\"."
    )
    assert re.search(r"""['"]subordinates\?['"]""", src), (
        "`subordinates` must be declared with optional-key syntax, e.g. \"subordinates?\"."
    )


def _run_harness(harness_code: str) -> dict:
    """
    Write a TS harness that imports Member + findRoot from the project's
    src/index.ts and prints a JSON result line prefixed with `RESULT:`.
    Returns the parsed JSON object.
    """
    tmp_dir = tempfile.mkdtemp(prefix="arktype-harness-", dir=PROJECT_DIR)
    harness_path = os.path.join(tmp_dir, "harness.ts")
    with open(harness_path, "w") as f:
        f.write(harness_code)
    try:
        result = subprocess.run(
            ["npx", "tsx", harness_path],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR,
            timeout=120,
        )
        # Find the RESULT: line in stdout.
        for line in result.stdout.splitlines():
            if line.startswith("RESULT:"):
                return json.loads(line[len("RESULT:"):])
        raise AssertionError(
            "Harness did not emit a RESULT: line.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    finally:
        try:
            os.remove(harness_path)
            os.rmdir(tmp_dir)
        except OSError:
            pass


CEO_ID = "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
DIR_ID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
ENG_ID = "a11d4fae-7dec-11d0-a765-00a0c91e6bf6"


def test_valid_three_level_tree_validates():
    harness = textwrap.dedent(f"""
        import {{ Member }} from "./src/index";

        const ceo: any = {{
            id: "{CEO_ID}",
            name: "Satya",
        }};
        const director: any = {{
            id: "{DIR_ID}",
            name: "Phil",
            manager: ceo,
        }};
        const engineer: any = {{
            id: "{ENG_ID}",
            name: "Alice",
            manager: director,
        }};
        director.subordinates = [engineer];
        ceo.subordinates = [director];

        let ok = true;
        let err: string | undefined;
        try {{
            Member.assert(ceo);
        }} catch (e: any) {{
            ok = false;
            err = String(e && e.message ? e.message : e);
        }}
        console.log("RESULT:" + JSON.stringify({{ ok, err }}));
    """).strip()
    result = _run_harness(harness)
    assert result["ok"], (
        f"Valid 3-level UUID org tree should validate via Member.assert, but it threw: {result.get('err')!r}"
    )


def test_invalid_uuid_is_rejected():
    harness = textwrap.dedent(f"""
        import {{ Member }} from "./src/index";

        const ceo: any = {{
            id: "{CEO_ID}",
            name: "Satya",
        }};
        const director: any = {{
            id: "not-a-uuid",
            name: "Phil",
            manager: ceo,
        }};
        ceo.subordinates = [director];

        let threw = false;
        try {{
            Member.assert(ceo);
        }} catch (_e: any) {{
            threw = true;
        }}
        console.log("RESULT:" + JSON.stringify({{ threw }}));
    """).strip()
    result = _run_harness(harness)
    assert result["threw"], (
        "Member.assert must throw when any node's `id` is not a valid UUID."
    )


def test_non_array_subordinates_is_rejected():
    harness = textwrap.dedent(f"""
        import {{ Member }} from "./src/index";

        const bad: any = {{
            id: "{CEO_ID}",
            name: "Satya",
            subordinates: "oops",
        }};

        let threw = false;
        try {{
            Member.assert(bad);
        }} catch (_e: any) {{
            threw = true;
        }}
        console.log("RESULT:" + JSON.stringify({{ threw }}));
    """).strip()
    result = _run_harness(harness)
    assert result["threw"], (
        "Member.assert must reject a node whose `subordinates` field is not an array."
    )


def test_find_root_walks_manager_chain():
    harness = textwrap.dedent(f"""
        import {{ Member, findRoot }} from "./src/index";

        const ceo: any = {{
            id: "{CEO_ID}",
            name: "Satya",
        }};
        const director: any = {{
            id: "{DIR_ID}",
            name: "Phil",
            manager: ceo,
        }};
        const engineer: any = {{
            id: "{ENG_ID}",
            name: "Alice",
            manager: director,
        }};
        director.subordinates = [engineer];
        ceo.subordinates = [director];

        Member.assert(ceo);

        const rootFromEng = findRoot(engineer);
        const rootFromDir = findRoot(director);
        const rootFromCeo = findRoot(ceo);
        console.log("RESULT:" + JSON.stringify({{
            rootFromEngId: rootFromEng && rootFromEng.id,
            rootFromDirId: rootFromDir && rootFromDir.id,
            rootFromCeoId: rootFromCeo && rootFromCeo.id,
            expectedRootId: "{CEO_ID}",
        }}));
    """).strip()
    result = _run_harness(harness)
    assert result["rootFromEngId"] == CEO_ID, (
        f"findRoot(engineer) must return the CEO node (id={CEO_ID}), got id={result['rootFromEngId']!r}."
    )
    assert result["rootFromDirId"] == CEO_ID, (
        f"findRoot(director) must return the CEO node (id={CEO_ID}), got id={result['rootFromDirId']!r}."
    )
    assert result["rootFromCeoId"] == CEO_ID, (
        f"findRoot(ceo) must return the CEO itself when invoked on the root, got id={result['rootFromCeoId']!r}."
    )


def test_entry_script_runs_cleanly():
    result = subprocess.run(
        ["npx", "tsx", "src/index.ts"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"`npx tsx src/index.ts` must exit with status 0.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
