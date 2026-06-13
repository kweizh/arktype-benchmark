import json
import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), (
        f"package.json not found at {package_json}."
    )


def test_package_json_pins_arktype_2_2_0():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json) as f:
        data = json.load(f)
    deps = data.get("dependencies", {})
    assert deps.get("arktype") == "2.2.0", (
        "Expected dependencies.arktype to be pinned to '2.2.0' in package.json."
    )


def test_tsconfig_exists():
    tsconfig = os.path.join(PROJECT_DIR, "tsconfig.json")
    assert os.path.isfile(tsconfig), (
        f"tsconfig.json not found at {tsconfig}."
    )


def test_src_dir_exists():
    src_dir = os.path.join(PROJECT_DIR, "src")
    assert os.path.isdir(src_dir), (
        f"Source directory {src_dir} does not exist."
    )


def test_arktype_installed_in_node_modules():
    arktype_pkg = os.path.join(PROJECT_DIR, "node_modules", "arktype", "package.json")
    assert os.path.isfile(arktype_pkg), (
        "arktype is not installed in node_modules; expected pre-installed at "
        f"{arktype_pkg}."
    )
    with open(arktype_pkg) as f:
        data = json.load(f)
    assert data.get("version") == "2.2.0", (
        f"Expected installed arktype version 2.2.0, got {data.get('version')}."
    )
