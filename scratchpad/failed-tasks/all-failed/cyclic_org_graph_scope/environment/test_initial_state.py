import json
import os
import shutil

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
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg_path), f"package.json not found at {pkg_path}."


def test_arktype_pinned_to_2_2_0():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = pkg.get("dependencies", {})
    assert deps.get("arktype") == "2.2.0", (
        f"package.json dependencies.arktype must be exactly '2.2.0', got {deps.get('arktype')!r}."
    )


def test_tsconfig_exists():
    tsconfig_path = os.path.join(PROJECT_DIR, "tsconfig.json")
    assert os.path.isfile(tsconfig_path), f"tsconfig.json not found at {tsconfig_path}."


def test_node_modules_installed():
    nm = os.path.join(PROJECT_DIR, "node_modules", "arktype")
    assert os.path.isdir(nm), (
        f"arktype is not installed under {nm}. Dependencies must be installed before evaluation."
    )


def test_src_directory_exists():
    src_dir = os.path.join(PROJECT_DIR, "src")
    assert os.path.isdir(src_dir), f"Source directory {src_dir} does not exist."
