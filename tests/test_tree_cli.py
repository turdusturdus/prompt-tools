from __future__ import annotations

import argparse
from datetime import datetime as real_datetime
from pathlib import Path

import pytest

import pt.tree.cli as tcli


def test_build_tree_lines_basic() -> None:
    lines = tcli._build_tree_lines(
        ["a.txt", "dir/sub.txt", "dir/inner/x.py"],
        {"a.txt": 1, "dir/sub.txt": 2, "dir/inner/x.py": 3},
    )
    assert lines[0] == "."
    joined = "\n".join(lines)
    assert "a.txt (1)" in joined
    assert "dir" in joined
    assert "sub.txt (2)" in joined
    assert "inner" in joined
    assert "x.py (3)" in joined


def test_cmd_tree_writes_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "myproj"
    project.mkdir()
    (project / "a.txt").write_text("hello\n", encoding="utf-8")
    (project / "dir").mkdir()
    (project / "dir" / "b.txt").write_text("world\n", encoding="utf-8")

    # Place a fake cli.py at tmp_path/src/pt/tree/cli.py so parents[3] == tmp_path
    fake_cli_file = tmp_path / "src" / "pt" / "tree" / "cli.py"
    fake_cli_file.parent.mkdir(parents=True, exist_ok=True)
    fake_cli_file.write_text("# fake", encoding="utf-8")
    monkeypatch.setattr(tcli, "__file__", str(fake_cli_file))

    class FakeDateTime:
        @staticmethod
        def now():
            return real_datetime(2025, 11, 10, 12, 40)

    monkeypatch.setattr(tcli, "datetime", FakeDateTime)

    # Force git path and deterministic file list
    monkeypatch.setattr(tcli, "is_git_repo", lambda p: True)
    monkeypatch.setattr(tcli, "list_files_git", lambda root, excludes: ["a.txt", "dir/b.txt"])

    ns = argparse.Namespace(project_dir=str(project))
    rc = tcli.cmd_tree(ns)
    assert rc == 0

    out = tmp_path / "data" / "trees" / "myproj" / "myproj_20251110_1240.yaml"
    assert out.is_file()

    text = out.read_text(encoding="utf-8")
    assert text.startswith("tree: |-\n")
    # line counts should be present for these text files
    assert "a.txt (1)" in text
    assert "b.txt (1)" in text

    # files list should NOT be present anymore
    assert "\nfiles:\n" not in text
