#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cli.py 参数解析与 mock 模式基本路径测试。
不传 API Key 时 FortuneTeller 进入 mock 模式，不会发起真实请求。
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cli  # noqa: E402


def test_cli_requires_action(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    # argparse 缺 required 参数组 → 退出码 2
    assert exc.value.code == 2


def test_cli_daily_missing_birth(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["cli.py", "--daily", "--quiet"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1


def test_cli_daily_mock_mode(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["cli.py", "--daily", "--birth", "1995-03-15", "--quiet"],
    )
    cli.main()  # mock 模式不应抛异常
    out = capsys.readouterr().out
    assert len(out) > 0


def test_cli_fortune_mock_mode(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["cli.py", "--fortune", "--birth", "1995-03-15", "--gender", "男", "--quiet"],
    )
    cli.main()
    out = capsys.readouterr().out
    assert len(out) > 0


def test_cli_relation_mock_mode(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cli.py",
            "--relation",
            "--name-a",
            "小明",
            "--birth-a",
            "1995-03-15",
            "--name-b",
            "小红",
            "--birth-b",
            "1996-08-20",
            "--quiet",
        ],
    )
    cli.main()
    out = capsys.readouterr().out
    assert len(out) > 0


def test_cli_stats(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["cli.py", "--stats", "--quiet"])
    cli.main()
    out = capsys.readouterr().out
    assert "运行统计" in out or "requests" in out
