"""Tests for prompt building and mock runner."""
import pytest
from prompt_ci.config import TestCase, Config
from prompt_ci.runner import build_prompt, run_prompt


def _make_test(**kwargs) -> TestCase:
    defaults = {"name": "test", "prompt": "Hello {{input}}", "input": "world"}
    defaults.update(kwargs)
    return TestCase(**defaults)


def _mock_config() -> Config:
    return Config(provider="mock", model="mock")


# --- build_prompt ---

def test_build_prompt_substitutes_input():
    t = _make_test(prompt="Summarize: {{input}}", input="some text")
    result = build_prompt(t)
    assert result == "Summarize: some text"


def test_build_prompt_appends_when_no_placeholder():
    t = _make_test(prompt="Summarize this:", input="some text")
    result = build_prompt(t)
    assert "Summarize this:" in result
    assert "some text" in result


def test_build_prompt_no_input():
    t = _make_test(prompt="Just a prompt", input=None)
    result = build_prompt(t)
    assert result == "Just a prompt"


def test_build_prompt_variable_substitution():
    t = _make_test(
        prompt="Be {{tone}}: {{input}}",
        input="text",
        variables={"tone": "concise"},
    )
    result = build_prompt(t)
    assert result == "Be concise: text"


# --- run_prompt (mock provider) ---

def test_run_mock_bullet_response():
    config = _mock_config()
    result = run_prompt("Summarize in bullet points: text", config)
    assert result.startswith("-")


def test_run_mock_sentiment_response():
    config = _mock_config()
    result = run_prompt("What is the sentiment of this text?", config)
    assert result == "positive"


def test_run_mock_summary_response():
    config = _mock_config()
    result = run_prompt("Summarize this text for me", config)
    assert "summary" in result.lower() or "mock" in result.lower()


def test_run_mock_fallback_response():
    config = _mock_config()
    result = run_prompt("some unmatched prompt here", config)
    assert "Mock response" in result


def test_run_prompt_unknown_provider_raises():
    config = Config(provider="unknown", model="x")
    with pytest.raises(ValueError, match="Unknown provider"):
        run_prompt("test", config)
