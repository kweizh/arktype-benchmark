import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_bun_available():
    assert shutil.which("bun") is not None, "bun binary not found in PATH."


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


def test_package_json_includes_elysia():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json) as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies", {}) or {})
    deps.update(data.get("devDependencies", {}) or {})
    assert "elysia" in deps, "elysia must be listed as a dependency in package.json."


def test_arktype_node_module_installed():
    arktype_pkg = os.path.join(PROJECT_DIR, "node_modules", "arktype", "package.json")
    assert os.path.isfile(arktype_pkg), (
        f"arktype is not installed in node_modules ({arktype_pkg} missing). "
        "Run `bun install` in the environment image."
    )
    with open(arktype_pkg) as f:
        data = json.load(f)
    assert data.get("version") == "2.2.0", (
        f"Installed arktype version must be 2.2.0 (was {data.get('version')!r})."
    )


def test_elysia_node_module_installed():
    elysia_pkg = os.path.join(PROJECT_DIR, "node_modules", "elysia", "package.json")
    assert os.path.isfile(elysia_pkg), (
        f"elysia is not installed in node_modules ({elysia_pkg} missing). "
        "Run `bun install` in the environment image."
    )


def test_arktype_resolves_via_bun():
    result = subprocess.run(
        ["bun", "-e", "import('arktype').then(() => process.exit(0)).catch((e) => { console.error(e); process.exit(1); })"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`arktype` is not importable via bun. "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def test_elysia_resolves_via_bun():
    result = subprocess.run(
        ["bun", "-e", "import('elysia').then(() => process.exit(0)).catch((e) => { console.error(e); process.exit(1); })"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`elysia` is not importable via bun. "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
