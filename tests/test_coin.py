"""Tests for coin flip functionality."""

import pytest
from src.coin import flip_coin, simulate_flips


def test_flip_coin_returns_valid_side():
    """Test that flip_coin returns either HEADS or TAILS."""
    result = flip_coin()
    assert result in ("HEADS", "TAILS")


def test_flip_coin_reproducibility():
    """Test that flip_coin with same seed gives same result."""
    result1 = flip_coin(seed=42)
    result2 = flip_coin(seed=42)
    assert result1 == result2


def test_simulate_flips_counts():
    """Test that simulate_flips returns correct counts."""
    result = simulate_flips(num_flips=10, seed=42)
    assert result["HEADS"] + result["TAILS"] == 10
    assert isinstance(result["HEADS"], int)
    assert isinstance(result["TAILS"], int)


def test_simulate_flips_default_seed():
    """Test simulate_flips with no seed still returns valid counts."""
    result = simulate_flips(num_flips=100)
    assert result["HEADS"] + result["TAILS"] == 100


def test_simulate_flips_outcomes_included():
    """Test that outcomes list is included in simulation result."""
    result = simulate_flips(num_flips=5, seed=123)
    assert "outcomes" in result
    assert len(result["outcomes"]) == 5
    assert all(outcome in ("HEADS", "TAILS") for outcome in result["outcomes"])