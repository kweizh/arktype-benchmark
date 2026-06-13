import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/arktype-pagination"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npx_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg_path), f"package.json not found at {pkg_path}."


def test_package_json_pins_arktype_2_2_0():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = pkg.get("dependencies", {})
    assert deps.get("arktype") == "2.2.0", (
        f"package.json must pin arktype to exactly 2.2.0, got: {deps.get('arktype')!r}."
    )


def test_node_modules_arktype_installed():
    arktype_dir = os.path.join(PROJECT_DIR, "node_modules", "arktype")
    assert os.path.isdir(arktype_dir), (
        f"arktype is not installed under {arktype_dir}; expected `npm install` to have run."
    )


def test_node_modules_tsx_installed():
    tsx_dir = os.path.join(PROJECT_DIR, "node_modules", "tsx")
    assert os.path.isdir(tsx_dir), (
        f"tsx is not installed under {tsx_dir}; the task relies on `npx tsx`."
    )


def test_tsconfig_exists():
    tsconfig_path = os.path.join(PROJECT_DIR, "tsconfig.json")
    assert os.path.isfile(tsconfig_path), (
        f"tsconfig.json not found at {tsconfig_path}."
    )


def test_instruction_md_present():
    instruction_path = os.path.join(PROJECT_DIR, "instruction.md")
    assert os.path.isfile(instruction_path), (
        f"instruction.md not found at {instruction_path}."
    )


def test_arktype_runtime_importable():
    # Sanity check: the installed arktype build can be loaded by Node.
    result = subprocess.run(
        [
            "node",
            "-e",
            "const a = require('arktype'); if (!a.scope || !a.type) { process.exit(2); }",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"Failed to load `arktype` from the project's node_modules. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
