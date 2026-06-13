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
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(path), f"{path} does not exist."


def test_package_json_declares_arktype_dependency():
    path = os.path.join(PROJECT_DIR, "package.json")
    with open(path) as f:
        manifest = json.load(f)
    deps = manifest.get("dependencies", {})
    assert "arktype" in deps, "arktype is not declared in package.json dependencies."
    assert deps["arktype"].lstrip("^~") == "2.2.0", (
        f"arktype dependency must be pinned to 2.2.0 (found {deps['arktype']})."
    )


def test_package_json_declares_ark_json_schema_dependency():
    path = os.path.join(PROJECT_DIR, "package.json")
    with open(path) as f:
        manifest = json.load(f)
    deps = manifest.get("dependencies", {})
    assert "@ark/json-schema" in deps, (
        "@ark/json-schema is not declared in package.json dependencies."
    )


def test_package_json_declares_check_script():
    path = os.path.join(PROJECT_DIR, "package.json")
    with open(path) as f:
        manifest = json.load(f)
    scripts = manifest.get("scripts", {})
    assert "check" in scripts, "package.json must declare a 'check' script."


def test_tsconfig_exists():
    path = os.path.join(PROJECT_DIR, "tsconfig.json")
    assert os.path.isfile(path), f"{path} does not exist."


def test_src_round_trip_stub_exists():
    path = os.path.join(PROJECT_DIR, "src", "roundTrip.ts")
    assert os.path.isfile(path), f"{path} does not exist."


def test_node_modules_installed():
    path = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(path), (
        f"{path} does not exist. Dependencies should be pre-installed during image build."
    )


def test_arktype_module_installed():
    path = os.path.join(PROJECT_DIR, "node_modules", "arktype", "package.json")
    assert os.path.isfile(path), "arktype is not installed in node_modules."
    with open(path) as f:
        pkg = json.load(f)
    assert pkg.get("version") == "2.2.0", (
        f"Installed arktype version must be 2.2.0 (found {pkg.get('version')})."
    )


def test_ark_json_schema_module_installed():
    path = os.path.join(
        PROJECT_DIR, "node_modules", "@ark", "json-schema", "package.json"
    )
    assert os.path.isfile(path), "@ark/json-schema is not installed in node_modules."


def test_tsx_available_for_verification():
    result = subprocess.run(
        ["npx", "--no-install", "tsx", "--version"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"tsx must be installed locally for harness verification. stderr: {result.stderr}"
    )
