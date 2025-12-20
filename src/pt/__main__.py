from __future__ import annotations

import argparse

from pt.get.cli import cmd_get


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pt",
        description=(
            "prompt-tools (pt)\n\n"
            "A small CLI for working with prompt-tools artifacts.\n"
            "Currently available commands:\n"
            "  - pt get   Create a YAML snapshot of a directory\n"
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_get = sub.add_parser(
        "get",
        help="Create a YAML snapshot of a directory.",
        description=(
            "Create a YAML snapshot of a directory.\n\n"
            "The command collects text files from PROJECT_DIR (respecting .gitignore and optional .ppignore)\n"
            "and writes a snapshot YAML into ./data/snapshots/.\n\n"
            "Output format (YAML):\n"
            "  files:\n"
            "    - path: \"relative/path/to/file.ext\"\n"
            "      content: |-\n"
            "        <file contents, indented>\n\n"
            "Notes:\n"
            "  • The \"path\" field is always relative to PROJECT_DIR.\n"
            "  • The \"content\" field is a YAML block scalar (|-), so the file is stored verbatim.\n"
            "  • Binary files are omitted and replaced with: [binary file omitted]\n"
            "  • If PROJECT_DIR is a git repo, file discovery uses git ls-files.\n"
            "    Otherwise it falls back to ripgrep (rg --files).\n"
            "  • If a .ppignore file exists in PROJECT_DIR, its patterns are used to exclude files.\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p_get.add_argument(
        "project_dir",
        metavar="PROJECT_DIR",
        help="Directory to snapshot (paths inside the YAML are relative to this directory).",
    )
    p_get.set_defaults(func=cmd_get)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
