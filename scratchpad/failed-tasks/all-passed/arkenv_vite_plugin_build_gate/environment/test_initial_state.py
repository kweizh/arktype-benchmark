import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_npx_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), (
        f"package.json not found at {package_json}."
    )


def test_package_json_has_required_dependencies():
    """The Dockerfile pre-installs arktype, arkenv, @arkenv/vite-plugin, vite, react,
    react-dom, and @vitejs/plugin-react. Confirm they are listed in package.json so
    the executor can use them without running `npm install` themselves."""
    package_json = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json) as f:
        data = json.load(f)
    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

    assert "arktype" in deps, "arktype is not listed in package.json."
    assert deps["arktype"] == "2.2.0", (
        f"Expected arktype version 2.2.0 but got {deps['arktype']!r}."
    )

    assert "arkenv" in deps, "arkenv is not listed in package.json."
    assert deps["arkenv"] == "0.12.1", (
        f"Expected arkenv version 0.12.1 but got {deps['arkenv']!r}."
    )

    for required in (
        "@arkenv/vite-plugin",
        "vite",
        "react",
        "react-dom",
        "@vitejs/plugin-react",
    ):
        assert required in deps, (
            f"{required!r} is not listed in package.json (dependencies or devDependencies)."
        )


def test_node_modules_installed():
    """Verify the preinstalled node_modules contain the packages required to build."""
    for required in (
        "arktype",
        "arkenv",
        "@arkenv/vite-plugin",
        "vite",
        "react",
        "react-dom",
        "@vitejs/plugin-react",
    ):
        module_dir = os.path.join(PROJECT_DIR, "node_modules", *required.split("/"))
        assert os.path.isdir(module_dir), (
            f"Expected pre-installed node module at {module_dir}."
        )


def test_arkenv_vite_plugin_importable():
    """Sanity check: the @arkenv/vite-plugin module is loadable from the project."""
    result = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            "import arkenv from '@arkenv/vite-plugin'; "
            "if (typeof arkenv !== 'function') { "
            "  console.error('default export is not a function'); process.exit(1); "
            "} console.log('ok');",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        "Failed to import @arkenv/vite-plugin from project: "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        f"Unexpected stdout when importing @arkenv/vite-plugin: {result.stdout!r}"
    )


def test_executor_artifacts_not_seeded():
    """The implementer must construct vite.config.ts, src/main.tsx, .env.example, etc.
    Make sure these are NOT seeded in the starting environment."""
    for relative in (
        "vite.config.ts",
        "vite.config.js",
        "src/main.tsx",
        ".env",
        ".env.example",
    ):
        path = os.path.join(PROJECT_DIR, relative)
        assert not os.path.exists(path), (
            f"{path} should not exist in the initial environment; the executor must create it."
        )
