from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath
from typing import List, Tuple


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def die(msg: str, code: int = 1) -> "NoReturn":
    eprint(msg)
    raise SystemExit(code)


PLACEHOLDERS = {
    "[binary file omitted]",
    "[unreadable file omitted]",
}


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s


def parse_files_yaml(yaml_path: Path) -> List[Tuple[str, str]]:
    """
    Parses YAML file-set format (as produced by `pt context` or by an LLM):

      files:
        - path: "relative/path"
          content: |-
            <indented content>

    This is a tiny format-specific parser (no PyYAML dependency).
    """
    if not yaml_path.is_file():
        die(f"Error: YAML file not found: {yaml_path}")

    raw = yaml_path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()

    # find "files:"
    i = 0
    while i < len(lines) and lines[i].strip() != "files:":
        i += 1
    if i >= len(lines):
        die(f"Error: invalid YAML (missing 'files:'): {yaml_path}")
    i += 1

    items: List[Tuple[str, str]] = []

    def at_entry_start(line: str) -> bool:
        return line.startswith("  - path:")

    while i < len(lines):
        line = lines[i]

        if line.strip() == "":
            i += 1
            continue

        if not at_entry_start(line):
            # allow noise/unknown lines
            i += 1
            continue

        #  - path: "x"
        _, _, rhs = line.partition(":")
        path_val = _strip_quotes(rhs.strip())
        if not path_val:
            die(f"Error: invalid entry path in {yaml_path} at line {i+1}")

        i += 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1

        if i >= len(lines) or not lines[i].startswith("    content:"):
            die(f"Error: invalid entry (missing 'content') in {yaml_path} near line {i+1}")

        content_line = lines[i].strip()
        if "content:" not in content_line or "|" not in content_line:
            die(f"Error: unsupported content format in {yaml_path} near line {i+1}")

        i += 1

        content_lines: List[str] = []
        while i < len(lines) and not at_entry_start(lines[i]):
            cl = lines[i]

            if cl.startswith("      "):
                content_lines.append(cl[6:])
            elif cl.strip() == "":
                content_lines.append("")
            else:
                content_lines.append(cl.lstrip())

            i += 1

        content = "\n".join(content_lines)
        items.append((path_val, content))

    return items


# Backwards-compatible alias (older tests/imports expect this name)
def parse_snapshot_yaml(yaml_path: Path) -> List[Tuple[str, str]]:
    return parse_files_yaml(yaml_path)


def safe_join(project_root: Path, rel_path: str) -> Path:
    """
    Prevents path traversal and absolute paths.
    """
    rel_posix = rel_path.replace("\\", "/").strip()
    if rel_posix == "":
        die("Error: empty path in YAML.")

    p = PurePosixPath(rel_posix)
    if p.is_absolute():
        die(f"Error: absolute path is not allowed: {rel_path}")

    if ".." in p.parts:
        die(f"Error: path traversal is not allowed: {rel_path}")

    root = project_root.resolve()
    target = (root / Path(*p.parts)).resolve()

    if target != root and root not in target.parents:
        die(f"Error: path escapes project root: {rel_path}")

    return target


def cmd_apply(args: argparse.Namespace) -> int:
    project_root = Path(args.project_dir).expanduser().resolve()
    if not project_root.is_dir():
        die(f"Error: project dir not found: {project_root}")

    yaml_path = Path(args.yaml_file).expanduser().resolve()
    items = parse_files_yaml(yaml_path)

    if not items:
        eprint(f"Warning: no files found in: {yaml_path}")
        return 0

    written = 0
    skipped = 0

    for rel_path, content in items:
        target = safe_join(project_root, rel_path)

        stripped = content.strip()
        if stripped in PLACEHOLDERS and not args.write_placeholders:
            eprint(f"Skipping placeholder content: {rel_path}")
            skipped += 1
            continue

        if args.no_clobber and target.exists():
            eprint(f"Skipping existing file (--no-clobber): {rel_path}")
            skipped += 1
            continue

        if args.dry_run:
            print(f"Would write: {target}")
            written += 1
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="\n") as f:
            f.write(content)
            if content != "" and not content.endswith("\n"):
                f.write("\n")

        print(f"Wrote: {target}")
        written += 1

    print(f"Done. Written: {written}, skipped: {skipped}")
    return 0
