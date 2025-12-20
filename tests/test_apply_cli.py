from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from pt.apply.cli import cmd_apply, parse_snapshot_yaml


def test_parse_snapshot_yaml_basic(tmp_path: Path) -> None:
    y = tmp_path / "s.yaml"
    y.write_text(
        (
            "files:\n"
            "  - path: \"a.txt\"\n"
            "    content: |-\n"
            "      line1\n"
            "      \n"
            "      line3\n"
        ),
        encoding="utf-8",
    )

    items = parse_snapshot_yaml(y)
    assert items == [("a.txt", "line1\n\nline3")]


def test_cmd_apply_creates_files_and_dirs(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()

    snap = tmp_path / "snap.yaml"
    snap.write_text(
        (
            "files:\n"
            "  - path: \"a.txt\"\n"
            "    content: |-\n"
            "      hello\n"
            "  - path: \"dir/sub.txt\"\n"
            "    content: |-\n"
            "      world\n"
        ),
        encoding="utf-8",
    )

    ns = argparse.Namespace(
        project_dir=str(project),
        yaml_file=str(snap),
        dry_run=False,
        no_clobber=False,
        write_placeholders=False,
    )

    rc = cmd_apply(ns)
    assert rc == 0

    assert (project / "a.txt").read_text(encoding="utf-8") == "hello\n"
    assert (project / "dir" / "sub.txt").read_text(encoding="utf-8") == "world\n"


def test_cmd_apply_rejects_path_traversal(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()

    snap = tmp_path / "snap.yaml"
    snap.write_text(
        (
            "files:\n"
            "  - path: \"../evil.txt\"\n"
            "    content: |-\n"
            "      nope\n"
        ),
        encoding="utf-8",
    )

    ns = argparse.Namespace(
        project_dir=str(project),
        yaml_file=str(snap),
        dry_run=False,
        no_clobber=False,
        write_placeholders=False,
    )

    with pytest.raises(SystemExit):
        cmd_apply(ns)


def test_cmd_apply_skips_binary_placeholder_by_default(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    project = tmp_path / "proj"
    project.mkdir()

    snap = tmp_path / "snap.yaml"
    snap.write_text(
        (
            "files:\n"
            "  - path: \"bin.dat\"\n"
            "    content: |-\n"
            "      [binary file omitted]\n"
        ),
        encoding="utf-8",
    )

    ns = argparse.Namespace(
        project_dir=str(project),
        yaml_file=str(snap),
        dry_run=False,
        no_clobber=False,
        write_placeholders=False,
    )

    rc = cmd_apply(ns)
    assert rc == 0
    assert not (project / "bin.dat").exists()

    out = capsys.readouterr()
    assert "Skipping placeholder content" in out.err
