import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_npx_binary_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_scope_ts_not_yet_created():
    scope_path = os.path.join(PROJECT_DIR, "src", "scope.ts")
    assert not os.path.exists(scope_path), (
        f"Executor-created file {scope_path} must not exist in the initial state."
    )
