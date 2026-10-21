#!/usr/bin/env python3
"""Create a release commit and annotated semantic-version tag."""


import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "TypedUnit" / "_version.py"


def run(*args: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(args, cwd=ROOT, check=True, env=env)


def generate_version_file(version: str) -> None:
    """Write the committed source version file for a release only."""
    environment = os.environ.copy()
    environment["SETUPTOOLS_SCM_PRETEND_VERSION"] = version
    run(
        sys.executable,
        "-c",
        (
            "import setuptools_scm; "
            f"setuptools_scm.get_version(root={str(ROOT)!r}, "
            f"write_to={str(VERSION_FILE.relative_to(ROOT))!r}, "
            "version_scheme='only-version', local_scheme='no-local-version')"
        ),
        env=environment,
    )
    if not VERSION_FILE.exists():
        raise RuntimeError("SCM versioning did not generate TypedUnit/_version.py")


def main() -> None:
    if len(sys.argv) != 2 or not re.fullmatch(r"v\d+\.\d+\.\d+", sys.argv[1]):
        raise SystemExit(
            "release aborted: tag must use the form vMAJOR.MINOR.PATCH, for example v0.5.0"
        )
    tag = sys.argv[1]
    if (
        subprocess.run(["git", "diff", "--quiet"], cwd=ROOT).returncode
        or subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode
    ):
        raise SystemExit("release aborted: working tree has uncommitted changes")
    if (
        subprocess.run(
            ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        ).returncode
        == 0
    ):
        raise SystemExit(f"release aborted: tag {tag} already exists")
    generate_version_file(tag.removeprefix("v"))
    run(
        "git",
        "add",
        "TypedUnit/_version.py",
    )
    run(
        "git",
        "commit",
        "--allow-empty",
        "-m",
        f"Release {tag}",
        "-m",
        "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
    )
    run("git", "tag", "-a", tag, "-m", f"Release {tag}")


if __name__ == "__main__":
    main()
