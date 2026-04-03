"""Tests for similarity scoring."""
import pytest
from prompt_ci.similarity import _token_overlap, score_similarity


def test_token_overlap_identical():
    assert _token_overlap("hello world", "hello world") == 1.0


def test_token_overlap_disjoint():
    assert _token_overlap("hello world", "foo bar") == 0.0


def test_token_overlap_partial():
    score = _token_overlap("hello world", "hello there")
    assert 0 < score < 1


def test_token_overlap_both_empty():
    assert _token_overlap("", "") == 1.0


def test_score_similarity_mock_uses_token_overlap():
    score, method = score_similarity("positive", "positive", "mock", "mock")
    assert method == "token-overlap"
    assert score == 1.0


def test_score_similarity_mock_partial():
    score, method = score_similarity(
        "- point one\n- point two\n- point three",
        "- point one\n- point two",
        "mock",
        "mock",
    )
    assert method == "token-overlap"
    assert 0 < score < 1


def test_score_similarity_judge_fallback_on_bad_provider():
    """Unknown provider raises in judge; falls back to token-overlap."""
    score, method = score_similarity("hello", "hello", "nonexistent", "model")
    assert method == "token-overlap"
    assert score == 1.0
