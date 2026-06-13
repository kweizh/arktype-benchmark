import os
import re
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"
VITE_CONFIG = os.path.join(PROJECT_DIR, "vite.config.ts")
DIST_DIR = os.path.join(PROJECT_DIR, "dist")


def _clean_env_for_build():
    """Return a copy of os.environ stripped of the schema-relevant vars."""
    env = os.environ.copy()
    for key in ("VITE_API_URL", "VITE_FEATURE_FLAG"):
        env.pop(key, None)
    return env


def _remove_dist():
    if os.path.isdir(DIST_DIR):
        shutil.rmtree(DIST_DIR)


def _run_vite_build(extra_env):
    env = _clean_env_for_build()
    env.update(extra_env)
    _remove_dist()
    result = subprocess.run(
        ["npx", "--no-install", "vite", "build"],
        cwd=PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return result


def test_vite_config_exists():
    assert os.path.isfile(VITE_CONFIG), (
        f"Expected vite.config.ts at {VITE_CONFIG}; the executor must create it."
    )


def test_vite_config_registers_arkenv_plugin():
    """Criterion 4: vite.config.ts MUST import and register the @arkenv/vite-plugin plugin."""
    with open(VITE_CONFIG) as f:
        content = f.read()

    # Must import from @arkenv/vite-plugin.
    import_pattern = re.compile(
        r"""(?:import\s+[^;]*?from\s+|require\(\s*)['"]@arkenv/vite-plugin['"]""",
        re.MULTILINE,
    )
    assert import_pattern.search(content), (
        "vite.config.ts must import from '@arkenv/vite-plugin'."
    )

    # Must contain a plugins array (Vite plugin registration).
    plugins_pattern = re.compile(r"plugins\s*:\s*\[", re.MULTILINE)
    assert plugins_pattern.search(content), (
        "vite.config.ts must register plugins in a `plugins: [ ... ]` array."
    )


def test_build_succeeds_with_valid_env():
    """Criterion 1: vite build with valid env vars set MUST exit 0."""
    result = _run_vite_build(
        {
            "VITE_API_URL": "https://api.example.com",
            "VITE_FEATURE_FLAG": "true",
        }
    )
    assert result.returncode == 0, (
        "Expected `vite build` to exit 0 with valid VITE_API_URL and VITE_FEATURE_FLAG.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert os.path.isdir(DIST_DIR), (
        f"Expected `vite build` to produce {DIST_DIR} with valid env vars set."
    )


def test_build_fails_without_vite_api_url():
    """Criterion 2: vite build WITHOUT VITE_API_URL MUST exit non-zero AND mention the missing variable."""
    result = _run_vite_build(
        {
            "VITE_FEATURE_FLAG": "true",
        }
    )
    assert result.returncode != 0, (
        "Expected `vite build` to exit non-zero when VITE_API_URL is missing.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    assert "VITE_API_URL" in combined, (
        "Expected the build error output to mention the missing variable `VITE_API_URL`.\n"
        f"combined output:\n{combined}"
    )


def test_build_fails_with_malformed_vite_api_url():
    """Criterion 3: vite build with VITE_API_URL='not a url' MUST exit non-zero."""
    result = _run_vite_build(
        {
            "VITE_API_URL": "not a url",
            "VITE_FEATURE_FLAG": "true",
        }
    )
    assert result.returncode != 0, (
        "Expected `vite build` to exit non-zero when VITE_API_URL is a malformed URL.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
