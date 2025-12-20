from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Iterable, List, Optional


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def die(msg: str, code: int = 1) -> "NoReturn":
    eprint(msg)
    raise SystemExit(code)


def run_cmd(args: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def is_git_repo(path: Path) -> bool:
    try:
        cp = run_cmd(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"], check=True)
        return cp.stdout.strip().lower() == "true"
    except Exception:
        return False


def load_ppignore(project_root: Path) -> tuple[Path, List[str]]:
    """
    Loads optional .ppignore from project_root.
    """
    ppignore_file = project_root / ".ppignore"
    patterns: List[str] = []

    if ppignore_file.is_file():
        for raw in ppignore_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line)

    return ppignore_file, patterns


def list_files_git(project_root: Path, excludes: List[str]) -> List[str]:
    args = [
        "git",
        "-C",
        str(project_root),
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "--",
        *[f":(exclude){pat}" for pat in excludes],
    ]
    cp = run_cmd(args, check=False)
    if cp.returncode not in (0, 1):
        die(f"Error: git ls-files failed:\n{cp.stderr.strip()}")
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def list_files_rg(project_root: Path, ppignore_file: Path) -> List[str]:
    if shutil.which("rg") is None:
        die("Error: Need 'git' (repo) or 'ripgrep' (rg) to honor ignores.")

    args = ["rg", "--files"]
    if ppignore_file.is_file():
        args += ["--ignore-file", str(ppignore_file)]

    cp = run_cmd(args, cwd=project_root, check=False)
    if cp.returncode not in (0, 1):
        die(f"Error: rg --files failed:\n{cp.stderr.strip()}")
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def should_skip(rel: str, patterns: Iterable[str]) -> bool:
    if not patterns:
        return False

    rel_posix = rel.replace("\\", "/")
    p = PurePosixPath(rel_posix)

    for pat in patterns:
        pat = pat.strip()
        if not pat or pat.startswith("#"):
            continue

        try:
            if p.match(pat):
                return True
        except Exception:
            pass

        if rel_posix == pat:
            return True

    return False


def is_binary_file(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            chunk = f.read(4096)
        return b"\x00" in chunk
    except Exception:
        return True


def write_yaml_snapshot(output_path: Path, project_root: Path, rel_files: List[str], patterns: List[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="\n") as out:
        out.write("files:\n")

        for rel in rel_files:
            if not rel:
                continue

            rel_posix = rel.replace("\\", "/")
            if should_skip(rel_posix, patterns):
                continue

            abs_path = project_root / rel_posix
            if not abs_path.is_file():
                continue

            out.write("\n")
            out.write(f'  - path: "{rel_posix}"\n')
            out.write("    content: |-\n")

            if is_binary_file(abs_path):
                out.write("      [binary file omitted]\n")
                continue

            try:
                text = abs_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                out.write("      [unreadable file omitted]\n")
                continue

            if text == "":
                continue

            for line in text.splitlines():
                out.write("      " + line + "\n")


def cmd_get(args: argparse.Namespace) -> int:
    project_root = Path(args.project_dir).expanduser().resolve()
    if not project_root.is_dir():
        die(f"Error: project dir not found: {project_root}")

    ppignore_file, pp_ignore = load_ppignore(project_root)

    if is_git_repo(project_root):
        rel_files = list_files_git(project_root, pp_ignore)
    elif shutil.which("rg") is not None:
        rel_files = list_files_rg(project_root, ppignore_file)
    else:
        die("Error: Need 'git' (repo) or 'ripgrep' (rg) to honor ignores.")

    # snapshots live in repo-root ./data/snapshots
    repo_root = Path(__file__).resolve().parents[3]  # .../repo/src/pt/get/cli.py -> parents[3] == repo root
    snapshots_dir = repo_root / "data" / "snapshots"

    prefix = project_root.name
    now = datetime.now()
    output_path = snapshots_dir / f"{prefix}_{now:%Y%m%d_%H%M}.yaml"

    write_yaml_snapshot(output_path, project_root, rel_files, pp_ignore)

    print(f"Wrote: {output_path}")
    return 0
