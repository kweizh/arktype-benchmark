import json
import os
import re
import subprocess
import tempfile

import pytest

PROJECT_DIR = "/home/user/myproject"
DIST_FILE = os.path.join(PROJECT_DIR, "dist", "pipeline.js")
SRC_FILE = os.path.join(PROJECT_DIR, "src", "pipeline.ts")
PACKAGE_JSON = os.path.join(PROJECT_DIR, "package.json")


HARNESS_JS = r"""
const path = require('path');
const { pathToFileURL } = require('url');

(async () => {
    const results = {};
    const modPath = path.resolve(process.argv[2]);
    let mod;
    try {
        mod = await import(pathToFileURL(modPath).href);
    } catch (e) {
        results.load_error = String(e && e.stack ? e.stack : e);
        process.stdout.write(JSON.stringify(results));
        return;
    }

    results.exports = {
        applyTax: typeof mod.applyTax,
        formatInvoice: typeof mod.formatInvoice,
    };

    const safeCall = (fn, args) => {
        try {
            const value = fn(...args);
            return { ok: true, value };
        } catch (e) {
            return {
                ok: false,
                name: (e && e.constructor && e.constructor.name) || 'Error',
                message: String(e && e.message ? e.message : e),
            };
        }
    };

    if (typeof mod.applyTax === 'function') {
        results.applyTax_default = safeCall(mod.applyTax, [100]);
        results.applyTax_explicit = safeCall(mod.applyTax, [100, 0.2]);
        results.applyTax_invalid = safeCall(mod.applyTax, ['100', 0.1]);
    }

    if (typeof mod.formatInvoice === 'function') {
        results.formatInvoice_default = safeCall(mod.formatInvoice, [[10, 20, 30]]);
        results.formatInvoice_discount = safeCall(mod.formatInvoice, [[10, 20, 30], 0.5]);
    }

    process.stdout.write(JSON.stringify(results));
})().catch(e => {
    process.stderr.write(String(e && e.stack ? e.stack : e));
    process.exit(1);
});
"""


def _run_npm(args, cwd=PROJECT_DIR):
    return subprocess.run(
        ["npm", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="session")
def built_project():
    dist_dir = os.path.join(PROJECT_DIR, "dist")
    if os.path.isdir(dist_dir):
        subprocess.run(["rm", "-rf", dist_dir], check=True)

    if not os.path.isdir(os.path.join(PROJECT_DIR, "node_modules")):
        install = _run_npm(["install"])
        assert install.returncode == 0, (
            f"npm install failed: stdout={install.stdout}\nstderr={install.stderr}"
        )

    build = _run_npm(["run", "build"])
    assert build.returncode == 0, (
        f"npm run build failed: stdout={build.stdout}\nstderr={build.stderr}"
    )
    assert os.path.isfile(DIST_FILE), (
        f"Build did not produce expected entrypoint at {DIST_FILE}."
    )
    return DIST_FILE


@pytest.fixture(scope="session")
def harness_results(built_project):
    with tempfile.NamedTemporaryFile(
        "w", suffix=".cjs", delete=False, dir=PROJECT_DIR
    ) as f:
        f.write(HARNESS_JS)
        harness_path = f.name
    try:
        result = subprocess.run(
            ["node", harness_path, built_project],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )
    finally:
        try:
            os.unlink(harness_path)
        except OSError:
            pass
    assert result.returncode == 0, (
        f"Verification harness failed: stdout={result.stdout}\nstderr={result.stderr}"
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"Harness output was not valid JSON: {e}\nstdout={result.stdout}\nstderr={result.stderr}"
        )
    assert "load_error" not in data, (
        f"Failed to import compiled module: {data.get('load_error')}"
    )
    return data


def test_compiled_entrypoint_exists(built_project):
    assert os.path.isfile(built_project), (
        f"Compiled entrypoint {built_project} does not exist."
    )


def test_module_exports_both_functions(harness_results):
    exports = harness_results.get("exports", {})
    assert exports.get("applyTax") == "function", (
        f"Expected `applyTax` to be exported as a function, got {exports.get('applyTax')}."
    )
    assert exports.get("formatInvoice") == "function", (
        f"Expected `formatInvoice` to be exported as a function, got {exports.get('formatInvoice')}."
    )


def test_apply_tax_default_rate(harness_results):
    r = harness_results.get("applyTax_default", {})
    assert r.get("ok") is True, (
        f"applyTax(100) raised an error: {r.get('name')}: {r.get('message')}"
    )
    assert r.get("value") == 110, (
        f"Expected applyTax(100) == 110, got {r.get('value')!r}."
    )


def test_apply_tax_explicit_rate(harness_results):
    r = harness_results.get("applyTax_explicit", {})
    assert r.get("ok") is True, (
        f"applyTax(100, 0.2) raised an error: {r.get('name')}: {r.get('message')}"
    )
    assert r.get("value") == 120, (
        f"Expected applyTax(100, 0.2) == 120, got {r.get('value')!r}."
    )


def test_apply_tax_invalid_first_arg_throws_traversal_error(harness_results):
    r = harness_results.get("applyTax_invalid", {})
    assert r.get("ok") is False, (
        f"Expected applyTax(\"100\", 0.1) to throw, but it returned {r.get('value')!r}."
    )
    name = r.get("name") or ""
    message = r.get("message") or ""
    assert "TraversalError" in name or "TraversalError" in message, (
        f"Expected a TraversalError when first parameter is invalid, "
        f"got {name}: {message}"
    )
    assert "[0]" in message, (
        "Expected the TraversalError message to reference the offending parameter "
        f"position (e.g. '[0]'); got: {message}"
    )


def test_format_invoice_default_discount(harness_results):
    r = harness_results.get("formatInvoice_default", {})
    assert r.get("ok") is True, (
        f"formatInvoice([10, 20, 30]) raised an error: {r.get('name')}: {r.get('message')}"
    )
    assert r.get("value") == {"total": 60, "count": 3}, (
        f"Expected formatInvoice([10, 20, 30]) == {{total: 60, count: 3}}, "
        f"got {r.get('value')!r}."
    )


def test_format_invoice_explicit_discount(harness_results):
    r = harness_results.get("formatInvoice_discount", {})
    assert r.get("ok") is True, (
        f"formatInvoice([10, 20, 30], 0.5) raised an error: "
        f"{r.get('name')}: {r.get('message')}"
    )
    assert r.get("value") == {"total": 30, "count": 3}, (
        f"Expected formatInvoice([10, 20, 30], 0.5) == {{total: 30, count: 3}}, "
        f"got {r.get('value')!r}."
    )


def test_source_uses_type_fn_signature():
    assert os.path.isfile(SRC_FILE), (
        f"Expected TypeScript source at {SRC_FILE}."
    )
    with open(SRC_FILE) as f:
        source = f.read()
    type_fn_calls = len(re.findall(r"type\.fn\s*\(", source))
    assert type_fn_calls >= 2, (
        f"Expected at least two `type.fn(...)` definitions in {SRC_FILE}, "
        f"found {type_fn_calls}."
    )
    colon_separators = len(re.findall(r"[\"']\s*:\s*[\"']", source))
    assert colon_separators >= 2, (
        "Expected both `type.fn` definitions to declare a return type using the "
        "`\":\"` separator; could not find two such separators in source."
    )


def test_package_json_pins_arktype_version():
    with open(PACKAGE_JSON) as f:
        data = json.load(f)
    deps = data.get("dependencies", {})
    assert deps.get("arktype") == "2.2.0", (
        f"Expected dependencies.arktype == '2.2.0' in package.json, "
        f"got {deps.get('arktype')!r}."
    )
