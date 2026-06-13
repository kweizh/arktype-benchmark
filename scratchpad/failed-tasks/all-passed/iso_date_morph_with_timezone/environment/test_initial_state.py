import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(
        PROJECT_DIR
    ), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(
        package_json
    ), f"package.json not found at {package_json}."


def test_arktype_dependency_pinned_to_2_2_0():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json) as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies", {}) or {})
    deps.update(data.get("devDependencies", {}) or {})
    assert "arktype" in deps, "arktype is not declared in package.json dependencies."
    assert deps["arktype"] == "2.2.0", (
        f"arktype must be pinned to exactly 2.2.0, got {deps['arktype']!r}."
    )


def test_node_modules_installed():
    node_modules = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(
        node_modules
    ), "node_modules/ is missing. Run `npm install` first."


def test_arktype_package_installed():
    arktype_pkg = os.path.join(PROJECT_DIR, "node_modules", "arktype", "package.json")
    assert os.path.isfile(arktype_pkg), (
        "arktype package is not installed under node_modules/."
    )
    with open(arktype_pkg) as f:
        data = json.load(f)
    assert data.get("version") == "2.2.0", (
        f"Installed arktype version must be 2.2.0, got {data.get('version')!r}."
    )


def test_tsx_available_in_project():
    # tsx is used to run TypeScript without an explicit build step
    result = subprocess.run(
        ["npx", "--no-install", "tsx", "--version"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`tsx` is not available in the project. stderr: {result.stderr!r}"
    )
