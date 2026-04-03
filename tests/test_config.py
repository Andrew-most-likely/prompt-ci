"""Tests for config loading."""
import pytest
from pathlib import Path
from prompt_ci.config import load_config, Config, TestCase


VALID_YAML = """\
provider: mock
model: mock
threshold: 0.75
golden_dir: .golden-test

tests:
  - name: test_one
    prompt: "Hello {{input}}"
    input: "world"
    threshold: 0.90
  - name: test_two
    prompt: "Summarize: {{input}}"
    input: "some text"
"""


def test_load_config_valid(tmp_path):
    cfg_file = tmp_path / "prompt-ci.yaml"
    cfg_file.write_text(VALID_YAML)
    config = load_config(str(cfg_file))

    assert config.provider == "mock"
    assert config.model == "mock"
    assert config.threshold == 0.75
    assert config.golden_dir == ".golden-test"
    assert len(config.tests) == 2
    assert config.tests[0].name == "test_one"
    assert config.tests[0].threshold == 0.90
    assert config.tests[1].threshold is None


def test_load_config_defaults(tmp_path):
    cfg_file = tmp_path / "prompt-ci.yaml"
    cfg_file.write_text("tests:\n  - name: t\n    prompt: p\n")
    config = load_config(str(cfg_file))

    assert config.provider == "anthropic"
    assert config.threshold == 0.80
    assert config.golden_dir == ".golden"


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/prompt-ci.yaml")


def test_testcase_variables(tmp_path):
    yaml = """\
provider: mock
model: mock
tests:
  - name: var_test
    prompt: "Be {{tone}}: {{input}}"
    input: "text"
    variables:
      tone: concise
"""
    cfg_file = tmp_path / "prompt-ci.yaml"
    cfg_file.write_text(yaml)
    config = load_config(str(cfg_file))
    assert config.tests[0].variables == {"tone": "concise"}
