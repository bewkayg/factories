"""Smoke tests: scripts import cleanly and the CSV merge runs on the real data."""

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent


def load_script(filename: str):
    """Import a script by path (works for names like 'harita.bot.py')."""
    path = ROOT / filename
    module_name = path.stem.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # runs top level only; __main__ block is skipped
    return module


@pytest.mark.parametrize("filename", ["bolge_bot.py", "harita.bot.py", "main.py"])
def test_script_imports(filename):
    load_script(filename)


def test_bolge_listesi_yapisi():
    bolgeler = load_script("bolge_bot.py").BOLGELER
    assert isinstance(bolgeler, dict) and bolgeler
    for bolge, iller in bolgeler.items():
        assert isinstance(iller, dict) and iller, bolge
        for il, aramalar in iller.items():
            assert aramalar and all(isinstance(a, str) and a for a in aramalar), il


def test_merge_csv(tmp_path):
    shutil.copytree(ROOT / "veriler", tmp_path / "veriler")
    izmir = ROOT / "izmir_fabrikalar.csv"
    if izmir.exists():
        shutil.copy(izmir, tmp_path)

    result = subprocess.run(
        [sys.executable, str(ROOT / "merge.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr

    out = tmp_path / "TUM_FABRIKALAR_ANA_LISTE.csv"
    df = pd.read_csv(out, sep=";", encoding="utf-8-sig")
    assert len(df) > 0
    assert {"Bölge", "İl", "Harita Linki"} <= set(df.columns)
    assert not df["Harita Linki"].duplicated().any()
