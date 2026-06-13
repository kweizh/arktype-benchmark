import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_npx_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), f"package.json not found at {package_json}."


def test_arktype_pinned_to_2_2_0():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json) as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies") or {})
    deps.update(data.get("devDependencies") or {})
    assert "arktype" in deps, "arktype dependency missing from package.json."
    assert deps["arktype"] == "2.2.0", (
        f"arktype must be pinned to 2.2.0 in package.json, found '{deps.get('arktype')}'."
    )


def test_arktype_installed_in_node_modules():
    arktype_pkg = os.path.join(PROJECT_DIR, "node_modules", "arktype", "package.json")
    assert os.path.isfile(arktype_pkg), (
        f"arktype is not installed in node_modules at {arktype_pkg}."
    )
    with open(arktype_pkg) as f:
        data = json.load(f)
    assert data.get("version") == "2.2.0", (
        f"Installed arktype version must be 2.2.0, found '{data.get('version')}'."
    )


def test_tsx_runnable():
    result = subprocess.run(
        ["npx", "--yes", "tsx", "--version"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"`npx tsx --version` failed in {PROJECT_DIR}. stderr: {result.stderr}"
    )


def test_validate_ts_not_yet_created():
    validate_ts = os.path.join(PROJECT_DIR, "validate.ts")
    assert not os.path.exists(validate_ts), (
        f"validate.ts must NOT exist before the task starts; found {validate_ts}."
    )
