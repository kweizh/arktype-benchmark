import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npx_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_tsx_available():
    # tsx may be installed globally or as a project dependency exposed via npx.
    result = subprocess.run(
        ["npx", "--no-install", "tsx", "--version"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`npx tsx --version` failed; tsx is not available. "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), f"{package_json} does not exist."


def test_package_json_pins_arktype_2_2_0():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json) as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies", {}) or {})
    deps.update(data.get("devDependencies", {}) or {})
    assert "arktype" in deps, "arktype must be listed as a dependency in package.json."
    assert deps["arktype"] == "2.2.0", (
        f"arktype must be pinned to 2.2.0 in package.json (was {deps['arktype']!r})."
    )


def test_arktype_node_module_installed():
    arktype_pkg = os.path.join(PROJECT_DIR, "node_modules", "arktype", "package.json")
    assert os.path.isfile(arktype_pkg), (
        f"arktype is not installed in node_modules ({arktype_pkg} missing). "
        "Run `npm install` in the environment image."
    )
    with open(arktype_pkg) as f:
        data = json.load(f)
    assert data.get("version") == "2.2.0", (
        f"Installed arktype version must be 2.2.0 (was {data.get('version')!r})."
    )


def test_arktype_config_entrypoint_resolves():
    # Confirm that "arktype/config" is a real, resolvable entrypoint in the installed package.
    result = subprocess.run(
        ["node", "-e", "require.resolve('arktype/config')"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`arktype/config` entrypoint does not resolve. "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
