from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pt.context.cli import (
    die,
    is_binary_file,
    is_git_repo,
    list_files_git,
    list_files_rg,
    load_ppignore,
    should_skip,
)


def _safe_line_count(project_root: Path, rel_posix: str) -> Optional[int]:
    """
    Returns number of text lines for a file.
    - For binary/unreadable files returns None.
    """
    abs_path = project_root / rel_posix
    if not abs_path.is_file():
        return None

    if is_binary_file(abs_path):
        return None

    try:
        text = abs_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    return len(text.splitlines())


def _build_tree_lines(rel_files: List[str], line_counts: Dict[str, Optional[int]]) -> List[str]:
    """
    Build an ASCII tree from a list of posix-style relative paths.
    Appends "(<n>)" for leaf files when line count is available, otherwise "(?)".

    Example:
      .
      ├── a.txt (12)
      └── dir
          └── sub.txt (3)
    """
    # Normalize and sort
    paths: List[List[str]] = []
    for rel in rel_files:
        rel = rel.strip().replace("\\", "/")
        if not rel:
            continue
        parts = [p for p in rel.split("/") if p]
        if parts:
            paths.append(parts)

    paths.sort()

    # Build a simple prefix-tree
    tree: dict = {}
    for parts in paths:
        node = tree
        for part in parts:
            node = node.setdefault(part, {})

    lines: List[str] = ["."]

    def walk(node: dict, prefix: str, parent_parts: List[str]) -> None:
        keys = sorted(node.keys())
        for idx, k in enumerate(keys):
            is_last = idx == (len(keys) - 1)
            branch = "└── " if is_last else "├── "

            child = node[k]
            cur_parts = parent_parts + [k]

            if child:
                # directory
                lines.append(prefix + branch + k)
                extension = "    " if is_last else "│   "
                walk(child, prefix + extension, cur_parts)
            else:
                # file leaf
                rel_path = "/".join(cur_parts)
                n = line_counts.get(rel_path)
                suffix = f" ({n})" if isinstance(n, int) else " (?)"
                lines.append(prefix + branch + k + suffix)

    walk(tree, "", [])
    return lines


def write_yaml_tree(output_path: Path, project_root: Path, rel_files: List[str], patterns: List[str]) -> None:
    """
    Writes a YAML artifact containing ONLY:

      tree: |-
        <ascii tree with optional line counts>

    It intentionally does NOT include any metadata keys (tool/project/generated_at)
    and intentionally does NOT include a files list.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Filter with .ppignore-like patterns (same as context)
    filtered: List[str] = []
    for rel in rel_files:
        rel_posix = rel.replace("\\", "/").strip()
        if not rel_posix:
            continue
        if should_skip(rel_posix, patterns):
            continue
        if (project_root / rel_posix).is_file():
            filtered.append(rel_posix)

    # Precompute line counts
    line_counts: Dict[str, Optional[int]] = {}
    for rel in filtered:
        line_counts[rel] = _safe_line_count(project_root, rel)

    tree_lines = _build_tree_lines(filtered, line_counts)

    with output_path.open("w", encoding="utf-8", newline="\n") as out:
        out.write("tree: |-\n")
        for line in tree_lines:
            out.write("  " + line + "\n")


def cmd_tree(args: argparse.Namespace) -> int:
    project_root = Path(args.project_dir).expanduser().resolve()
    if not project_root.is_dir():
        die(f"Error: project dir not found: {project_root}")

    ppignore_file, pp_ignore = load_ppignore(project_root)

    if is_git_repo(project_root):
        rel_files = list_files_git(project_root, pp_ignore)
    else:
        rel_files = list_files_rg(project_root, ppignore_file)

    # trees live in repo-root ./data/trees/<project-name>/
    repo_root = Path(__file__).resolve().parents[3]  # .../repo/src/pt/tree/cli.py -> parents[3] == repo root
    trees_root = repo_root / "data" / "trees"

    prefix = project_root.name
    now = datetime.now()
    output_path = trees_root / prefix / f"{prefix}_{now:%Y%m%d_%H%M}.yaml"

    write_yaml_tree(output_path, project_root, rel_files, pp_ignore)

    print(f"Wrote: {output_path}")
    return 0
