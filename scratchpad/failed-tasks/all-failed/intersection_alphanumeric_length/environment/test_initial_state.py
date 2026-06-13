import json
import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npx_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), f"{package_json} does not exist."


def test_package_json_declares_arktype_2_2_0():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json) as f:
        data = json.load(f)
    deps = data.get("dependencies", {}) or {}
    assert deps.get("arktype") == "2.2.0", (
        "Expected dependencies.arktype to be exactly \"2.2.0\" in package.json."
    )


def test_node_modules_installed():
    arktype_dir = os.path.join(PROJECT_DIR, "node_modules", "arktype")
    assert os.path.isdir(arktype_dir), (
        f"arktype is not installed at {arktype_dir}; node_modules should be pre-populated."
    )


def test_src_dir_exists():
    src_dir = os.path.join(PROJECT_DIR, "src")
    assert os.path.isdir(src_dir), f"Source directory {src_dir} does not exist."


def test_validate_script_not_yet_created():
    validate_ts = os.path.join(PROJECT_DIR, "src", "validate.ts")
    assert not os.path.exists(validate_ts), (
        f"{validate_ts} should not exist before the executor creates it."
    )
