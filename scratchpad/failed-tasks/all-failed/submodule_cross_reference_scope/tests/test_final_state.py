"""Final-state verifier for the `submodule_cross_reference_scope` task.

Test criteria (verbatim, enforced below):
  1. `module.db.config.assert({...})` MUST validate a config payload.
  2. `module.http.server.assert({...})` MUST validate when given a payload that
     contains a nested `db.config`-shaped property.
  3. Cross-submodule references MUST resolve (verified by validating a payload
     that exercises the reference).
  4. Invalid `db.config` payloads passed via the server schema MUST be rejected.
  5. The scope MUST be defined in a single `scope({...}).export()` call with at
     least two submodule keys using dot notation.
"""

import json
import os
import re
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCOPE_TS = os.path.join(PROJECT_DIR, "src", "scope.ts")
PACKAGE_JSON = os.path.join(PROJECT_DIR, "package.json")
VERIFY_SCRIPT = os.path.join(PROJECT_DIR, ".verify-module.mjs")


def _read_source() -> str:
    assert os.path.isfile(SCOPE_TS), f"Expected scope source at {SCOPE_TS}"
    with open(SCOPE_TS, "r", encoding="utf-8") as f:
        return f.read()


def _find_scope_export_block(source: str):
    """Return (body_text, post_text) for the single scope({...}).export() chain.

    body_text is the text between the outermost braces of the scope({...}) call.
    post_text is everything after the closing paren of scope(...), used to confirm
    that `.export()` is chained.
    """
    start_indices = [m.start() for m in re.finditer(r"\bscope\s*\(", source)]
    matches = []
    for start in start_indices:
        # find first '{' after 'scope('
        paren_open = source.index("(", start)
        i = paren_open + 1
        # skip whitespace
        while i < len(source) and source[i].isspace():
            i += 1
        if i >= len(source) or source[i] != "{":
            # scope() call without an inline object literal — not our chain
            continue
        brace_open = i
        depth = 0
        j = brace_open
        in_string = None
        escape = False
        while j < len(source):
            ch = source[j]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == in_string:
                    in_string = None
            else:
                if ch in ("'", '"', "`"):
                    in_string = ch
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
            j += 1
        if depth != 0:
            continue
        brace_close = j
        # find matching ')' after brace_close
        k = brace_close + 1
        while k < len(source) and source[k].isspace():
            k += 1
        if k >= len(source) or source[k] != ")":
            continue
        paren_close = k
        body = source[brace_open + 1 : brace_close]
        post = source[paren_close + 1 : paren_close + 32]
        matches.append((body, post))
    return matches


def test_project_files_exist():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} is missing."
    assert os.path.isfile(SCOPE_TS), f"Expected {SCOPE_TS} to exist."
    assert os.path.isfile(PACKAGE_JSON), f"Expected {PACKAGE_JSON} to exist."


def test_package_json_pins_arktype_2_2_0():
    with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies", {}) or {})
    deps.update(pkg.get("devDependencies", {}) or {})
    assert deps.get("arktype") == "2.2.0", (
        f"Expected dependencies.arktype to be exactly '2.2.0', got {deps.get('arktype')!r}."
    )


def test_tsx_available():
    # tsx should be reachable either as a global binary or via npx within the project.
    if shutil.which("tsx") is not None:
        return
    result = subprocess.run(
        ["npx", "--no-install", "tsx", "--version"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`npx --no-install tsx --version` failed; tsx must be installed locally. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_single_scope_export_chain():
    source = _read_source()
    matches = _find_scope_export_block(source)
    assert len(matches) == 1, (
        f"Expected exactly one `scope({{...}}).export()` chain in src/scope.ts, found {len(matches)}."
    )
    _body, post = matches[0]
    assert post.lstrip().startswith(".export()"), (
        "The single scope({...}) call must be immediately followed by `.export()`."
    )


def test_scope_has_db_and_http_dot_notation_keys():
    source = _read_source()
    matches = _find_scope_export_block(source)
    assert len(matches) == 1, "Expected exactly one scope({...}).export() chain."
    body, _ = matches[0]
    db_keys = re.findall(r"""["']\s*(db\.[A-Za-z0-9_]+)\s*["']\s*:""", body)
    http_keys = re.findall(r"""["']\s*(http\.[A-Za-z0-9_]+)\s*["']\s*:""", body)
    assert db_keys, (
        "Expected at least one dot-notation submodule key starting with `db.` "
        "(e.g., \"db.config\") inside the scope({...}) object literal."
    )
    assert http_keys, (
        "Expected at least one dot-notation submodule key starting with `http.` "
        "(e.g., \"http.server\") inside the scope({...}) object literal."
    )


def test_http_server_references_db_config_alias():
    """The http.server submodule must reference the `db.config` alias by name,
    rather than redefining the database configuration shape inline.
    """
    source = _read_source()
    # Find the body of the "http.server" key definition.
    match = re.search(
        r"""["']http\.server["']\s*:\s*\{""",
        source,
    )
    assert match is not None, (
        "Could not find an `\"http.server\": { ... }` definition inside scope({...})."
    )
    brace_open = source.index("{", match.end() - 1)
    depth = 0
    i = brace_open
    in_string = None
    escape = False
    while i < len(source):
        ch = source[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
        else:
            if ch in ("'", '"', "`"):
                in_string = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
        i += 1
    assert depth == 0, "Failed to parse the `http.server` submodule body."
    http_server_body = source[brace_open + 1 : i]
    assert re.search(r"""["']\s*db\.config\s*["']""", http_server_body), (
        "The `http.server` submodule must reference the `db.config` alias by name "
        "(e.g., `db: \"db.config\"`) instead of redefining the shape inline."
    )


def _write_verify_script():
    """Create a Node ESM script that imports the user's module and runs the four
    runtime assertions, printing a JSON summary to stdout.
    """
    script = r"""
import scopeModule from "./src/scope.ts";

function run() {
  const results = {};

  // 1. Module shape
  results.has_db_config = !!(scopeModule && scopeModule.db && scopeModule.db.config && typeof scopeModule.db.config.assert === "function");
  results.has_http_server = !!(scopeModule && scopeModule.http && scopeModule.http.server && typeof scopeModule.http.server.assert === "function");

  // 2. db.config.assert accepts a valid payload
  try {
    scopeModule.db.config.assert({ host: "127.0.0.1", port: 5432 });
    results.db_config_accepts_valid = true;
  } catch (e) {
    results.db_config_accepts_valid = false;
    results.db_config_accepts_valid_error = String(e && e.message ? e.message : e);
  }

  // 3. db.config.assert rejects an invalid payload (port wrong type)
  try {
    scopeModule.db.config.assert({ host: "127.0.0.1", port: "not-a-number" });
    results.db_config_rejects_invalid = false;
  } catch (e) {
    results.db_config_rejects_invalid = true;
  }

  // 4. http.server.assert accepts a payload whose nested db config is valid.
  // We try common nested property names ("db", "database", "config") since
  // the executor is free to choose the key name.
  const candidateKeys = ["db", "database", "dbConfig", "config"];
  let httpValidAccepted = false;
  let httpValidAcceptedKey = null;
  for (const key of candidateKeys) {
    const payload = { host: "0.0.0.0", port: 8080 };
    payload[key] = { host: "127.0.0.1", port: 5432 };
    try {
      scopeModule.http.server.assert(payload);
      httpValidAccepted = true;
      httpValidAcceptedKey = key;
      break;
    } catch (_) {
      // try next key
    }
  }
  results.http_server_accepts_valid = httpValidAccepted;
  results.http_server_accepted_key = httpValidAcceptedKey;

  // 5. http.server.assert rejects a payload whose nested db config is invalid.
  // Re-use the key that worked above.
  if (httpValidAcceptedKey) {
    const badPayload = { host: "0.0.0.0", port: 8080 };
    badPayload[httpValidAcceptedKey] = { host: "127.0.0.1", port: "not-a-number" };
    try {
      scopeModule.http.server.assert(badPayload);
      results.http_server_rejects_invalid = false;
    } catch (_) {
      results.http_server_rejects_invalid = true;
    }
  } else {
    results.http_server_rejects_invalid = false;
  }

  process.stdout.write(JSON.stringify(results));
}

run();
"""
    with open(VERIFY_SCRIPT, "w", encoding="utf-8") as f:
        f.write(script)


@pytest.fixture(scope="module")
def runtime_results():
    _write_verify_script()
    try:
        result = subprocess.run(
            ["npx", "--no-install", "tsx", VERIFY_SCRIPT],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
    finally:
        pass
    assert result.returncode == 0, (
        f"Verifier tsx script failed.\nstdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    try:
        data = json.loads(result.stdout.strip().splitlines()[-1])
    except Exception as exc:
        raise AssertionError(
            f"Could not parse verifier JSON output. stdout={result.stdout!r}"
        ) from exc
    yield data
    if os.path.exists(VERIFY_SCRIPT):
        os.remove(VERIFY_SCRIPT)


def test_module_exposes_dot_notation_submodules(runtime_results):
    assert runtime_results.get("has_db_config") is True, (
        "Expected `module.db.config.assert` to be a function on the exported module."
    )
    assert runtime_results.get("has_http_server") is True, (
        "Expected `module.http.server.assert` to be a function on the exported module."
    )


def test_db_config_assert_accepts_valid_payload(runtime_results):
    assert runtime_results.get("db_config_accepts_valid") is True, (
        "module.db.config.assert({host: '127.0.0.1', port: 5432}) must succeed. "
        f"Error: {runtime_results.get('db_config_accepts_valid_error')!r}"
    )


def test_db_config_assert_rejects_invalid_payload(runtime_results):
    assert runtime_results.get("db_config_rejects_invalid") is True, (
        "module.db.config.assert must reject a payload whose `port` is not a number."
    )


def test_http_server_assert_accepts_payload_with_valid_db_config(runtime_results):
    assert runtime_results.get("http_server_accepts_valid") is True, (
        "module.http.server.assert must accept a payload whose nested db-config "
        "property (commonly named `db`, `database`, `dbConfig`, or `config`) is a "
        "valid db.config payload."
    )


def test_http_server_assert_rejects_payload_with_invalid_db_config(runtime_results):
    assert runtime_results.get("http_server_rejects_invalid") is True, (
        "module.http.server.assert must reject a payload whose nested db-config "
        "property is an invalid db.config payload (e.g., wrong port type)."
    )
