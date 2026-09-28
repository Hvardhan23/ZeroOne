"""Tests for Monte Carlo simulation functionality."""

import sys
import importlib.util
import json
import os
from pathlib import Path

# Ensure result directories exist
os.makedirs('results/summaries', exist_ok=True)
os.makedirs('results/detailed', exist_ok=True)


# Helper to run Monte Carlo (imports fresh each time)
def _run_monte_carlo(starting_chips, number_of_simulations, master_seed):
    """Run Monte Carlo simulation for testing."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from src.simulation import run_monte_carlo
    return run_monte_carlo(
        starting_chips=starting_chips,
        number_of_simulations=number_of_simulations,
        master_seed=master_seed,
    )


# Test 1: Reproducibility with same master seed
def test_monte_carlo_reproducible():
    """Same master seed should produce same results."""
    result1 = _run_monte_carlo(starting_chips=50, number_of_simulations=5, master_seed=42)
    result2 = _run_monte_carlo(starting_chips=50, number_of_simulations=5, master_seed=42)

    # Compare summary statistics
    assert result1['summary']['bankruptcy_rate'] == result2['summary']['bankruptcy_rate']
    assert result1['summary']['average_final_balance'] == result2['summary']['average_final_balance']

    # Compare individual simulation results
    for s1, s2 in zip(result1['simulation_results'], result2['simulation_results']):
        assert s1['final_balance'] == s2['final_balance']
        assert s1['random_seed'] == s2['random_seed']

    print('PASS: test_monte_carlo_reproducible')


# Test 2: Different master seed gives different results
def test_monte_carlo_different_seed():
    """Different master seed should produce different results."""
    result3 = _run_monte_carlo(starting_chips=50, number_of_simulations=5, master_seed=123)

    # Should be different from the seed=42 run
    diff_found = False
    for s1, s2 in zip(result1['simulation_results'], result3['simulation_results']):
        if s1['final_balance'] != s2['final_balance']:
            diff_found = True
            break

    assert diff_found, "Different master seed should give different results"
    print('PASS: test_monte_carlo_different_seed')


# Test 3: Aggregation calculations
def test_monte_carlo_aggregation():
    """Test that aggregation statistics are calculated correctly."""
    result = _run_monte_carlo(starting_chips=100, number_of_simulations=10, master_seed=42)
    s = result['summary']

    # Check that rates are between 0 and 1
    assert 0 <= s['bankruptcy_rate'] <= 1, f"Bankruptcy rate should be in [0,1], got {s['bankruptcy_rate']}"
    assert 0 <= s['profitability_rate'] <= 1, f"Profitability rate should be in [0,1], got {s['profitability_rate']}"

    # Check that counts are integers
    assert isinstance(s['number_bankrupt'], int), "number_bankrupt should be int"
    assert isinstance(s['number_profitable'], int), "number_profitable should be int"
    assert isinstance(s['number_of_simulations'], int), "number_of_simulations should be int"

    # Check that averages are reasonable
    assert s['average_final_balance'] > 0, "average_final_balance should be positive"
    assert s['minimum_final_balance'] <= s['maximum_final_balance'], "min should <= max"

    print('PASS: test_monte_carlo_aggregation')


# Test 4: bankruptcy rate test
def test_monte_carlo_bankruptcy_rate():
    """Test bankruptcy rate is sensible for different starting chips."""
    # With 50 chips, bankruptcy should be very likely
    result = _run_monte_carlo(starting_chips=50, number_of_simulations=20, master_seed=42)
    assert result['summary']['bankruptcy_rate'] > 0.5, f"With 50 chips, bankruptcy rate should be > 50%, got {result['summary']['bankruptcy_rate']}"

    # With 1000 chips, bankruptcy should be less likely
    result2 = _run_monte_carlo(starting_chips=1000, number_of_simulations=20, master_seed=42)
    assert result2['summary']['bankruptcy_rate'] < 0.5, f"With 1000 chips, bankruptcy rate should be < 50%, got {result2['summary']['bankruptcy_rate']}"

    print('PASS: test_monte_carlo_bankruptcy_rate')


# Test 5: Monte Carlo returns correct structure
def test_monte_carlo_structure():
    """Test that Monte Carlo return structure is correct."""
    result = _run_monte_carlo(starting_chips=50, number_of_simulations=3, master_seed=42)

    # Top-level keys
    assert 'simulation_results' in result
    assert 'summary' in result
    assert 'experiment_id' in result
    assert 'master_seed' in result

    # Simulation result keys
    for sim_result in result['simulation_results']:
        required_keys = [
            'simulation_id', 'experiment_id', 'scenario', 'starting_chips',
            'total_iterations', 'total_bets', 'total_heads', 'total_tails',
            'final_balance', 'maximum_balance', 'minimum_balance',
            'total_profit_loss', 'bankrupt', 'bankruptcy_iteration',
            'random_seed'
        ]
        for key in required_keys:
            assert key in sim_result, f"Missing key '{key}' in simulation result"

    # Summary keys
    summary = result['summary']
    summary_keys = [
        'number_of_simulations', 'number_bankrupt', 'bankruptcy_rate',
        'number_profitable', 'profitability_rate',
        'average_final_balance', 'median_final_balance',
        'minimum_final_balance', 'maximum_final_balance',
        'average_iterations_survived', 'median_iterations_survived',
        'average_maximum_balance', 'median_maximum_balance'
    ]
    for key in summary_keys:
        assert key in summary, f"Missing key '{key}' in summary"

    print('PASS: test_monte_carlo_structure')


if __name__ == '__main__':
    # Run all tests
    test_monte_carlo_reproducible()
    test_monte_carlo_different_seed()
    test_monte_carlo_aggregation()
    test_monte_carlo_bankruptcy_rate()
    test_monte_carlo_structure()
    print()
    print('All 5 Monte Carlo tests passed!')