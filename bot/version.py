import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def get_version() -> str:
    """Version from pyproject.toml plus the current git commit, resolved at call time."""
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return version
    return f"{version}+{head.stdout.strip()}" if head.returncode == 0 else version
