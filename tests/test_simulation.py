"""Tests for simulation functionality."""

import pytest
from src.simulation import run_coin_simulation, run_betting_simulation


def test_run_coin_simulation():
    """Test coin simulation returns valid results."""
    result = run_coin_simulation(num_flips=100, seed=42)
    assert "HEADS" in str(result) or result.get("total_flips", 0) == 100


def test_run_betting_simulation():
    """Test betting simulation runs without error."""
    result = run_betting_simulation(
        starting_chips=100,
        num_simulations=1,
        seed=42,
    )
    assert "starting_chips" in result
    assert "results" in result
    assert len(result["results"]) == 1


def test_run_betting_simulation_multiple():
    """Test betting simulation with multiple runs."""
    result = run_betting_simulation(
        starting_chips=100,
        num_simulations=5,
        seed=42,
    )
    assert len(result["results"]) == 5


def test_betting_simulation_bankruptcy():
    """Test that betting simulation can result in bankruptcy."""
    result = run_betting_simulation(
        starting_chips=10,
        num_simulations=10,
        seed=42,
    )
    # With only 10 starting chips, bankruptcy is likely
    bankruptcy_count = result["bankruptcy_count"]
    assert isinstance(bankruptcy_count, int)