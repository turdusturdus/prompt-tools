from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime as real_datetime

import pytest

import pt.get.cli as cli


def test_load_ppignore_missing(tmp_path: Path) -> None:
    ppfile, patterns = cli.load_ppignore(tmp_path)
    assert ppfile == tmp_path / ".ppignore"
    assert patterns == []


def test_load_ppignore_parses_lines(tmp_path: Path) -> None:
    (tmp_path / ".ppignore").write_text(
        """
# comment
dist/**
   
*.log
# another comment
build/**
""".lstrip(),
        encoding="utf-8",
    )
    _, patterns = cli.load_ppignore(tmp_path)
    assert patterns == ["dist/**", "*.log", "build/**"]


def test_should_skip_globs() -> None:
    patterns = ["foo/*.py", "**/bar.txt", "exact.md"]
    assert cli.should_skip("foo/x.py", patterns) is True
    assert cli.should_skip("a/b/bar.txt", patterns) is True
    assert cli.should_skip("exact.md", patterns) is True
    assert cli.should_skip("foo/x.txt", patterns) is False


def test_is_binary_file(tmp_path: Path) -> None:
    t = tmp_path / "t.txt"
    b = tmp_path / "b.bin"
    t.write_text("hello\n", encoding="utf-8")
    b.write_bytes(b"abc\x00def")
    assert cli.is_binary_file(t) is False
    assert cli.is_binary_file(b) is True


def test_write_yaml_snapshot_basic(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "a.txt").write_text("line1\nline2\n", encoding="utf-8")

    out = tmp_path / "out.yaml"
    cli.write_yaml_snapshot(
        output_path=out,
        project_root=project,
        rel_files=["a.txt"],
        patterns=[],
    )

    text = out.read_text(encoding="utf-8")
    assert text.startswith("files:\n")
    assert '  - path: "a.txt"\n' in text
    assert "    content: |-\n" in text
    assert "      line1\n" in text
    assert "      line2\n" in text


def test_write_yaml_snapshot_respects_ppignore(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "a.txt").write_text("ok\n", encoding="utf-8")
    (project / "skip.txt").write_text("nope\n", encoding="utf-8")

    out = tmp_path / "out.yaml"
    cli.write_yaml_snapshot(
        output_path=out,
        project_root=project,
        rel_files=["a.txt", "skip.txt"],
        patterns=["skip.txt"],
    )

    text = out.read_text(encoding="utf-8")
    assert '  - path: "a.txt"\n' in text
    assert '  - path: "skip.txt"\n' not in text


def test_cmd_get_errors_on_missing_dir(tmp_path: Path) -> None:
    ns = argparse.Namespace(project_dir=str(tmp_path / "nope"))
    with pytest.raises(SystemExit):
        cli.cmd_get(ns)


def test_cmd_get_uses_git_and_writes_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "myproj"
    project.mkdir()
    (project / "a.txt").write_text("hello\n", encoding="utf-8")

    # Place a fake cli.py at tmp_path/src/pt/get/cli.py so parents[3] == tmp_path
    fake_cli_file = tmp_path / "src" / "pt" / "get" / "cli.py"
    fake_cli_file.parent.mkdir(parents=True, exist_ok=True)
    fake_cli_file.write_text("# fake", encoding="utf-8")
    monkeypatch.setattr(cli, "__file__", str(fake_cli_file))

    # Freeze time
    class FakeDateTime:
        @staticmethod
        def now():
            return real_datetime(2025, 11, 10, 12, 40)

    monkeypatch.setattr(cli, "datetime", FakeDateTime)

    # Force git path
    monkeypatch.setattr(cli, "is_git_repo", lambda p: True)
    monkeypatch.setattr(cli, "list_files_git", lambda root, excludes: ["a.txt"])

    ns = argparse.Namespace(project_dir=str(project))
    rc = cli.cmd_get(ns)
    assert rc == 0

    out = tmp_path / "data" / "snapshots" / "myproj_20251110_1240.yaml"
    assert out.is_file()

    text = out.read_text(encoding="utf-8")
    assert '  - path: "a.txt"\n' in text
    assert "      hello\n" in text


def test_cmd_get_falls_back_to_rg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "rgproj"
    project.mkdir()
    (project / "b.txt").write_text("world\n", encoding="utf-8")

    fake_cli_file = tmp_path / "src" / "pt" / "get" / "cli.py"
    fake_cli_file.parent.mkdir(parents=True, exist_ok=True)
    fake_cli_file.write_text("# fake", encoding="utf-8")
    monkeypatch.setattr(cli, "__file__", str(fake_cli_file))

    class FakeDateTime:
        @staticmethod
        def now():
            return real_datetime(2025, 11, 10, 12, 40)

    monkeypatch.setattr(cli, "datetime", FakeDateTime)

    monkeypatch.setattr(cli, "is_git_repo", lambda p: False)
    monkeypatch.setattr(cli.shutil, "which", lambda name: "/usr/bin/rg" if name == "rg" else None)
    monkeypatch.setattr(cli, "list_files_rg", lambda root, ppignore_file: ["b.txt"])

    ns = argparse.Namespace(project_dir=str(project))
    rc = cli.cmd_get(ns)
    assert rc == 0

    out = tmp_path / "data" / "snapshots" / "rgproj_20251110_1240.yaml"
    assert out.is_file()
    assert '  - path: "b.txt"\n' in out.read_text(encoding="utf-8")
