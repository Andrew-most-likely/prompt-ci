"""Tests for golden file storage."""
import json
import pytest
from pathlib import Path
from prompt_ci.storage import save_golden, load_golden, golden_path


def test_save_and_load_golden(tmp_path):
    golden_dir = str(tmp_path / "golden")
    path = save_golden(golden_dir, "my_test", "the prompt", "the output", "claude-3", "anthropic")

    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["test_name"] == "my_test"
    assert data["output"] == "the output"
    assert data["model"] == "claude-3"
    assert data["provider"] == "anthropic"
    assert "recorded_at" in data
    assert "prompt_hash" in data


def test_recorded_at_is_utc_aware(tmp_path):
    golden_dir = str(tmp_path / "golden")
    save_golden(golden_dir, "t", "p", "o", "m", "anthropic")
    data = load_golden(golden_dir, "t")
    # datetime.now(timezone.utc).isoformat() includes +00:00 offset
    assert "+00:00" in data["recorded_at"]


def test_load_golden_missing_returns_none(tmp_path):
    result = load_golden(str(tmp_path), "nonexistent")
    assert result is None


def test_golden_path(tmp_path):
    p = golden_path(str(tmp_path), "foo_bar")
    assert p == tmp_path / "foo_bar.json"


def test_save_golden_creates_dir(tmp_path):
    nested = str(tmp_path / "a" / "b" / "c")
    save_golden(nested, "t", "p", "o", "m", "mock")
    assert (Path(nested) / "t.json").exists()
