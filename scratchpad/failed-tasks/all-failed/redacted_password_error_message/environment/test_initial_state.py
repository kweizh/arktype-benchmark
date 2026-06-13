import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npx_binary_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist."
    )


def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), (
        f"Expected package.json at {package_json}."
    )


def test_package_json_pins_arktype_2_2_0():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json) as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies", {}) or {})
    deps.update(data.get("devDependencies", {}) or {})
    arktype_version = deps.get("arktype")
    assert arktype_version is not None, (
        "Expected 'arktype' to be listed in package.json dependencies."
    )
    assert "2.2.0" in arktype_version, (
        f"Expected arktype to be pinned to 2.2.0, got: {arktype_version!r}."
    )


def test_tsconfig_exists():
    tsconfig = os.path.join(PROJECT_DIR, "tsconfig.json")
    assert os.path.isfile(tsconfig), f"Expected tsconfig.json at {tsconfig}."


def test_arktype_module_installed():
    arktype_pkg = os.path.join(PROJECT_DIR, "node_modules", "arktype", "package.json")
    assert os.path.isfile(arktype_pkg), (
        f"Expected arktype to be installed at {arktype_pkg}."
    )
    with open(arktype_pkg) as f:
        data = json.load(f)
    assert data.get("version") == "2.2.0", (
        f"Expected installed arktype version 2.2.0, got: {data.get('version')!r}."
    )


def test_arktype_importable_via_node():
    """Confirm that the installed arktype module can be loaded by Node.js."""
    result = subprocess.run(
        [
            "node",
            "-e",
            "const a = require('arktype'); if (!a.type) { process.exit(2); }",
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"Expected `require('arktype')` to succeed in {PROJECT_DIR}; "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}."
    )


def test_schema_file_absent():
    """The executor is responsible for creating src/schema.ts."""
    schema_path = os.path.join(PROJECT_DIR, "src", "schema.ts")
    assert not os.path.exists(schema_path), (
        f"Expected {schema_path} to NOT exist before the task is performed."
    )
