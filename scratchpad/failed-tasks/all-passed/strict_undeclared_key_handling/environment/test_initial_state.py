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
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), (
        f"package.json not found at {package_json_path}."
    )


def test_arktype_dependency_pinned():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json_path) as f:
        package_json = json.load(f)
    deps = package_json.get("dependencies", {})
    assert deps.get("arktype") == "2.2.0", (
        f"Expected dependencies.arktype to be pinned to '2.2.0' in {package_json_path}, "
        f"got {deps.get('arktype')!r}."
    )


def test_arktype_installed():
    arktype_pkg = os.path.join(PROJECT_DIR, "node_modules", "arktype", "package.json")
    assert os.path.isfile(arktype_pkg), (
        f"arktype package is not installed at {arktype_pkg}; run `npm install` "
        "during environment build."
    )
    with open(arktype_pkg) as f:
        pkg = json.load(f)
    assert pkg.get("version") == "2.2.0", (
        f"Installed arktype version is {pkg.get('version')!r}, expected '2.2.0'."
    )


def test_tsconfig_exists():
    tsconfig_path = os.path.join(PROJECT_DIR, "tsconfig.json")
    assert os.path.isfile(tsconfig_path), (
        f"tsconfig.json not found at {tsconfig_path}."
    )


def test_src_dir_exists():
    src_dir = os.path.join(PROJECT_DIR, "src")
    assert os.path.isdir(src_dir), f"Source directory {src_dir} does not exist."
