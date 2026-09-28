"""Tests for the betting scenarios (Experiment 2)."""

import sys
sys.path.insert(0, '.')

from src.betting import calculate_bet_size, resolve_bet_profit, apply_profit, check_bankruptcy, run_iteration, run_iterations

# Test scenario starting chips and bet sizes
def test_low_scenario_starting_chips():
    """Test: low scenario starts at 50 chips."""
    # With 50 chips and 10 bets per iteration:
    # initial bet = floor(50 / 10) = 5
    bet = calculate_bet_size(50)
    assert bet == 5, f"Expected bet=5 for 50 chips, got {bet}"
    print("PASS: test_low_scenario_starting_chips")


def test_baseline_scenario_starting_chips():
    """Test: baseline scenario starts at 100 chips."""
    # With 100 chips and 10 bets per iteration:
    # initial bet = floor(100 / 10) = 10
    bet = calculate_bet_size(100)
    assert bet == 10, f"Expected bet=10 for 100 chips, got {bet}"
    print("PASS: test_baseline_scenario_starting_chips")


def test_high_scenario_starting_chips():
    """Test: high scenario starts at 1000 chips."""
    # With 1000 chips and 10 bets per iteration:
    # initial bet = floor(1000 / 10) = 100
    bet = calculate_bet_size(1000)
    assert bet == 100, f"Expected bet=100 for 1000 chips, got {bet}"
    print("PASS: test_high_scenario_starting_chips")


def test_scenario_bet_sizes_consistent():
    """Test: all scenarios use the same betting rules (identical logic)."""
    # The betting logic is in the functions, which are shared across all scenarios
    # Just verify the functions work correctly for all three scenarios
    
    # Low scenario (50 chips)
    result_low = run_iteration(starting_balance=50, bets_per_iteration=10, 
                               outcomes=["HEADS"]*5 + ["TAILS"]*5)
    assert result_low["bet_size"] == 5, f"Low scenario bet_size should be 5, got {result_low['bet_size']}"
    
    # 5 HEADS * 5 = +25 profit, 5 TAILS * -5 = -25 profit, net = 0
    # So ending_balance should be 50
    assert result_low["ending_balance"] == 50, f"Low scenario ending_balance should be 50, got {result_low['ending_balance']}"
    assert result_low["total_profit_loss"] == 0, f"Low scenario total_profit_loss should be 0, got {result_low['total_profit_loss']}"
    
    # Baseline scenario (100 chips)
    result_baseline = run_iteration(starting_balance=100, bets_per_iteration=10,
                                    outcomes=["HEADS"]*5 + ["TAILS"]*5)
    assert result_baseline["bet_size"] == 10, f"Baseline scenario bet_size should be 10, got {result_baseline['bet_size']}"
    # Net profit = 0, ending_balance should be 100
    assert result_baseline["ending_balance"] == 100, f"Baseline scenario ending_balance should be 100, got {result_baseline['ending_balance']}"
    assert result_baseline["total_profit_loss"] == 0, f"Baseline scenario total_profit_loss should be 0, got {result_baseline['total_profit_loss']}"
    
    # High scenario (1000 chips)
    result_high = run_iteration(starting_balance=1000, bets_per_iteration=10,
                                outcomes=["HEADS"]*5 + ["TAILS"]*5)
    assert result_high["bet_size"] == 100, f"High scenario bet_size should be 100, got {result_high['bet_size']}"
    assert result_high["ending_balance"] == 1000, f"High scenario ending_balance should be 1000, got {result_high['ending_balance']}"
    assert result_high["total_profit_loss"] == 0, f"High scenario total_profit_loss should be 0, got {result_high['total_profit_loss']}"
    
    print("PASS: test_scenario_bet_sizes_consistent")


def test_scenario_names_preserved():
    """Test: scenario names are preserved through the system."""
    from src.experiments import get_experiment_config
    
    import yaml
    with open('config/experiment_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    scenarios = config.get("starting_capital_scenarios", [])
    scenario_names = [s.get("name") for s in scenarios]
    
    assert "low" in scenario_names, f"'low' should be in scenario names, got {scenario_names}"
    assert "baseline" in scenario_names, f"'baseline' should be in scenario names, got {scenario_names}"
    assert "high" in scenario_names, f"'high' should be in scenario names, got {scenario_names}"
    
    print("PASS: test_scenario_names_preserved")


def test_iteration_results_correct_for_low():
    """Test: low scenario (50 chips) produces correct iteration results."""
    result = run_iteration(starting_balance=50, bets_per_iteration=10, 
                           outcomes=["TAILS"]*10)  # All tails
    
    # 10 TAILS * -5 = -50 profit
    # Starting 50, ending should be 0
    assert result["ending_balance"] == 0, f"Low all-tails should go bankrupt to 0, got {result['ending_balance']}"
    assert result["total_profit_loss"] == -50, f"Low all-tails profit should be -50, got {result['total_profit_loss']}"
    assert result["total_tails"] == 10, f"Low all-tails should have 10 tails, got {result['total_tails']}"
    assert result["total_heads"] == 0, f"Low all-tails should have 0 heads, got {result['total_heads']}"
    
    # Check bet size is 5
    assert result["bet_size"] == 5, f"Low bet_size should be 5, got {result['bet_size']}"
    
    # Check bet details
    for bd in result["bet_details"]:
        assert bd["bet_amount"] == 5, f"Low bet detail bet_amount should be 5, got {bd['bet_amount']}"
        assert bd["net_profit"] == -5, f"Low bet detail net_profit should be -5, got {bd['net_profit']}"
        # Check ending_balance decreases by 5 each bet: 50, 45, 40, ..., 0
        expected_balance = 50 - 5 * bd["bet_number"]
        assert bd["ending_balance"] == expected_balance, \
            f"Low bet detail ending_balance should be {expected_balance} (bet {bd['bet_number']}), got {bd['ending_balance']}"
    
    print("PASS: test_iteration_results_correct_for_low")


def test_iteration_results_correct_for_baseline():
    """Test: baseline scenario (100 chips) produces correct iteration results."""
    result = run_iteration(starting_balance=100, bets_per_iteration=10,
                           outcomes=["TAILS"]*10)  # All tails
    
    # 10 TAILS * -10 = -100 profit
    # Starting 100, ending should be 0 (bankrupt)
    assert result["ending_balance"] == 0, f"Baseline all-tails should go bankrupt to 0, got {result['ending_balance']}"
    assert result["total_profit_loss"] == -100, f"Baseline all-tails profit should be -100, got {result['total_profit_loss']}"
    assert result["total_tails"] == 10, f"Baseline all-tails should have 10 tails, got {result['total_tails']}"
    assert result["total_heads"] == 0, f"Baseline all-tails should have 0 heads, got {result['total_heads']}"
    
    # Check bet size is 10
    assert result["bet_size"] == 10, f"Baseline bet_size should be 10, got {result['bet_size']}"
    
    # Check bet details have bet_amount = 10
    for bd in result["bet_details"]:
        assert bd["bet_amount"] == 10, f"Baseline bet detail bet_amount should be 10, got {bd['bet_amount']}"
    
    print("PASS: test_iteration_results_correct_for_baseline")


def test_iteration_results_correct_for_high():
    """Test: high scenario (1000 chips) produces correct iteration results."""
    result = run_iteration(starting_balance=1000, bets_per_iteration=10,
                           outcomes=["TAILS"]*10)  # All tails
    
    # 10 TAILS * -100 = -1000 profit
    # Starting 1000, ending should be 0 (bankrupt)
    assert result["ending_balance"] == 0, f"High all-tails should go bankrupt to 0, got {result['ending_balance']}"
    assert result["total_profit_loss"] == -1000, f"High all-tails profit should be -1000, got {result['total_profit_loss']}"
    assert result["total_tails"] == 10, f"High all-tails should have 10 tails, got {result['total_tails']}"
    assert result["total_heads"] == 0, f"High all-tails should have 0 heads, got {result['total_heads']}"
    
    # Check bet size is 100
    assert result["bet_size"] == 100, f"High bet_size should be 100, got {result['bet_size']}"
    
    # Check bet details have bet_amount = 100
    for bd in result["bet_details"]:
        assert bd["bet_amount"] == 100, f"High bet detail bet_amount should be 100, got {bd['bet_amount']}"
    
    print("PASS: test_iteration_results_correct_for_high")


def test_bankruptcy_in_low_scenario():
    """Test: bankruptcy can occur in low scenario (50 chips)."""
    # With 50 chips and bet=5, after 10 tails: balance = 0 (bankrupt)
    result = run_iteration(starting_balance=50, bets_per_iteration=10, outcomes=["TAILS"]*10)
    assert result["ending_balance"] == 0
    print("PASS: test_bankruptcy_in_low_scenario")


def test_bankruptcy_in_baseline_scenario():
    """Test: bankruptcy can occur in baseline scenario (100 chips)."""
    # With 100 chips and bet=10, after 10 tails: balance = 0 (bankrupt)
    result = run_iteration(starting_balance=100, bets_per_iteration=10, outcomes=["TAILS"]*10)
    assert result["ending_balance"] == 0
    print("PASS: test_bankruptcy_in_baseline_scenario")


def test_bankruptcy_in_high_scenario():
    """Test: bankruptcy can occur in high scenario (1000 chips)."""
    # With 1000 chips and bet=100, after 10 tails: balance = 0 (bankrupt)
    result = run_iteration(starting_balance=1000, bets_per_iteration=10, outcomes=["TAILS"]*10)
    assert result["ending_balance"] == 0
    print("PASS: test_bankruptcy_in_high_scenario")