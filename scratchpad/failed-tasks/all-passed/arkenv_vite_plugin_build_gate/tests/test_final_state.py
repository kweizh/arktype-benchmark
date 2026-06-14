import json
import os
import re
import shutil
import subprocess
from typing import Mapping

PROJECT_DIR = "/home/user/myproject"
VITE_CONFIG_TS = os.path.join(PROJECT_DIR, "vite.config.ts")
VITE_CONFIG_JS = os.path.join(PROJECT_DIR, "vite.config.js")
MAIN_TSX = os.path.join(PROJECT_DIR, "src", "main.tsx")
ENV_EXAMPLE = os.path.join(PROJECT_DIR, ".env.example")
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
PACKAGE_JSON = os.path.join(PROJECT_DIR, "package.json")
DIST_INDEX_HTML = os.path.join(PROJECT_DIR, "dist", "index.html")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clean_build_artifacts() -> None:
    """Remove stale build output and any local .env files so the run is hermetic."""
    dist_dir = os.path.join(PROJECT_DIR, "dist")
    if os.path.isdir(dist_dir):
        shutil.rmtree(dist_dir)
    for relative in (
        ".env",
        ".env.local",
        ".env.production",
        ".env.production.local",
    ):
        path = os.path.join(PROJECT_DIR, relative)
        if os.path.isfile(path):
            os.remove(path)


def _vite_env() -> dict[str, str]:
    """Return a clean copy of os.environ with any pre-existing VITE_* variables removed
    so each test starts from a known baseline."""
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("VITE_")
    }
    # CI parity flag — silences npm noise.
    env.setdefault("CI", "1")
    env.setdefault("NODE_ENV", "production")
    return env


def _run_build(extra_env: Mapping[str, str]) -> subprocess.CompletedProcess[str]:
    """Run `npm run build` from the project root with the provided extra env."""
    _clean_build_artifacts()
    env = _vite_env()
    env.update(extra_env)
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )


# ---------------------------------------------------------------------------
# Source layout checks (Acceptance: source layout case)
# ---------------------------------------------------------------------------


def test_vite_config_exists_and_imports_arkenv_plugin():
    """Verification step 5: vite.config.ts must exist and import the plugin."""
    assert os.path.isfile(VITE_CONFIG_TS), (
        f"Expected Vite config at {VITE_CONFIG_TS}; a JS config is not acceptable."
    )
    # Defensive: the executor must not silently fall back to vite.config.js.
    assert not os.path.isfile(VITE_CONFIG_JS), (
        f"Unexpected {VITE_CONFIG_JS}; please use vite.config.ts only."
    )
    with open(VITE_CONFIG_TS, encoding="utf-8") as f:
        source = f.read()
    assert re.search(r"""from\s+['"]@arkenv/vite-plugin['"]""", source), (
        "vite.config.ts must import from '@arkenv/vite-plugin' (the actual plugin "
        "package — not a hand-rolled prebuild script)."
    )


def test_main_tsx_references_api_url():
    """Verification step 6: src/main.tsx must reference import.meta.env.VITE_API_URL."""
    assert os.path.isfile(MAIN_TSX), f"Expected React entry at {MAIN_TSX}."
    with open(MAIN_TSX, encoding="utf-8") as f:
        source = f.read()
    assert "import.meta.env.VITE_API_URL" in source, (
        "src/main.tsx must read `import.meta.env.VITE_API_URL` so the bundler retains it."
    )


def test_env_example_present_and_env_absent():
    """Verification step 7: .env.example committed, .env not present."""
    assert os.path.isfile(ENV_EXAMPLE), (
        f"Expected committed placeholder file at {ENV_EXAMPLE}."
    )
    assert not os.path.isfile(ENV_FILE), (
        f"{ENV_FILE} must NOT exist; values are supplied via real environment "
        "variables at build time."
    )


def test_npm_scripts_present():
    """Verification step 8: package.json must define build and validate-env scripts."""
    assert os.path.isfile(PACKAGE_JSON), f"Missing {PACKAGE_JSON}."
    with open(PACKAGE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    scripts = data.get("scripts", {}) or {}
    assert "build" in scripts, "package.json must define a `build` npm script."
    assert "vite build" in scripts["build"], (
        f"Expected `build` script to invoke `vite build`, got: {scripts['build']!r}."
    )
    assert "validate-env" in scripts, (
        "package.json must define a `validate-env` npm script (passthrough)."
    )


# ---------------------------------------------------------------------------
# Behavioural / build-gate checks (Acceptance: build behaviour cases)
# ---------------------------------------------------------------------------


def test_valid_env_build_succeeds():
    """Verification step 1: valid env -> exit 0 and dist/index.html produced."""
    result = _run_build(
        {
            "VITE_API_URL": "https://api.example.com",
            "VITE_FEATURE_FLAGS": "true",
            "VITE_MAX_UPLOAD_MB": "64",
        }
    )
    assert result.returncode == 0, (
        "Expected `npm run build` to succeed with valid env. "
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    assert os.path.isfile(DIST_INDEX_HTML), (
        f"Expected Vite build output at {DIST_INDEX_HTML} after a successful build, "
        f"but it was not produced.\nstdout={result.stdout!r}\nstderr={result.stderr!r}"
    )


def test_invalid_url_build_fails():
    """Verification step 2: VITE_API_URL=not-a-url -> non-zero exit with relevant error."""
    result = _run_build(
        {
            "VITE_API_URL": "not-a-url",
            "VITE_FEATURE_FLAGS": "true",
            "VITE_MAX_UPLOAD_MB": "64",
        }
    )
    assert result.returncode != 0, (
        "Expected `npm run build` to FAIL when VITE_API_URL is not a URL. "
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    combined = f"{result.stdout}\n{result.stderr}"
    assert "VITE_API_URL" in combined, (
        "Expected validation error to mention `VITE_API_URL`. "
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    # Look for an arkenv/arktype-style validation error message.
    arkenv_signature = re.compile(
        r"(ArkEnvError|must\s+be\s+a\s+url|must\s+be\s+a\s+URL|must\s+be\s+a\s+valid\s+url|url|URL)",
        re.IGNORECASE,
    )
    assert arkenv_signature.search(combined), (
        "Expected an arkenv/arktype-style validation error mentioning the URL constraint. "
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )


def test_out_of_range_integer_build_fails():
    """Verification step 3: VITE_MAX_UPLOAD_MB=0 -> non-zero exit referencing the var."""
    result = _run_build(
        {
            "VITE_API_URL": "https://api.example.com",
            "VITE_FEATURE_FLAGS": "true",
            "VITE_MAX_UPLOAD_MB": "0",
        }
    )
    assert result.returncode != 0, (
        "Expected `npm run build` to FAIL when VITE_MAX_UPLOAD_MB is 0. "
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    combined = f"{result.stdout}\n{result.stderr}"
    assert "VITE_MAX_UPLOAD_MB" in combined, (
        "Expected validation error to mention `VITE_MAX_UPLOAD_MB`. "
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )


def test_missing_variable_build_fails():
    """Verification step 4: VITE_API_URL unset -> non-zero exit."""
    # Supply the other two but explicitly omit VITE_API_URL.
    result = _run_build(
        {
            "VITE_FEATURE_FLAGS": "true",
            "VITE_MAX_UPLOAD_MB": "64",
        }
    )
    assert result.returncode != 0, (
        "Expected `npm run build` to FAIL when VITE_API_URL is missing. "
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
