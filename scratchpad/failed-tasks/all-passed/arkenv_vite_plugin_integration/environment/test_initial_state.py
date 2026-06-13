import json
import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg_path), f"package.json not found at {pkg_path}."


def test_package_json_has_required_dependencies():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies", {}) or {})
    deps.update(pkg.get("devDependencies", {}) or {})

    assert "arktype" in deps, "arktype must be listed in package.json dependencies."
    assert deps["arktype"].lstrip("^~=") == "2.2.0", (
        f"arktype must be pinned to 2.2.0, got {deps['arktype']}."
    )

    assert "arkenv" in deps, "arkenv must be listed in package.json dependencies."
    assert deps["arkenv"].lstrip("^~=") == "0.12.1", (
        f"arkenv must be pinned to 0.12.1, got {deps['arkenv']}."
    )

    assert "@arkenv/vite-plugin" in deps, (
        "@arkenv/vite-plugin must be listed in package.json dependencies."
    )
    assert "vite" in deps, "vite must be listed in package.json dependencies."


def test_node_modules_installed():
    nm = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(nm), (
        "node_modules directory not found; dependencies must be pre-installed."
    )

    for pkg_name in ("arktype", "arkenv", "vite"):
        assert os.path.isdir(os.path.join(nm, pkg_name)), (
            f"node_modules/{pkg_name} missing; dependencies must be pre-installed."
        )

    plugin_dir = os.path.join(nm, "@arkenv", "vite-plugin")
    assert os.path.isdir(plugin_dir), (
        "node_modules/@arkenv/vite-plugin missing; the Vite plugin must be pre-installed."
    )


def test_index_html_exists():
    index_path = os.path.join(PROJECT_DIR, "index.html")
    assert os.path.isfile(index_path), f"index.html entry not found at {index_path}."


def test_main_entry_exists():
    entry_path = os.path.join(PROJECT_DIR, "src", "main.ts")
    assert os.path.isfile(entry_path), f"src/main.ts entry not found at {entry_path}."


def test_tsconfig_exists():
    ts_path = os.path.join(PROJECT_DIR, "tsconfig.json")
    assert os.path.isfile(ts_path), f"tsconfig.json not found at {ts_path}."


def test_vite_config_not_yet_created():
    # The executor is expected to CREATE vite.config.ts. It must not be present yet.
    for ext in ("ts", "js", "mjs", "mts"):
        candidate = os.path.join(PROJECT_DIR, f"vite.config.{ext}")
        assert not os.path.exists(candidate), (
            f"{candidate} already exists; the executor must create vite.config.ts themselves."
        )
