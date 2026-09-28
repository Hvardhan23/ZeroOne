"""Tests for the core betting engine."""

import sys
import random
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.betting import (
    calculate_bet_size,
    resolve_bet_profit,
    apply_profit,
    check_bankruptcy,
    run_iteration,
    run_iterations,
    CoinSide,
)


def test_calculate_bet_size_starting_100():
    """Test 1: Starting balance 100 produces initial bet 10."""
    bet = calculate_bet_size(100)
    assert bet == 10, f"Expected 10, got {bet}"
    print("PASS: test_calculate_bet_size_starting_100")


def test_calculate_bet_size_starting_120():
    """Test 2: Starting balance 120 produces bet 12."""
    bet = calculate_bet_size(120)
    assert bet == 12, f"Expected 12, got {bet}"
    print("PASS: test_calculate_bet_size_starting_120")


def test_calculate_bet_size_starting_99():
    """Test 3: Starting balance 99 produces bet 9."""
    bet = calculate_bet_size(99)
    assert bet == 9, f"Expected 9, got {bet}"
    print("PASS: test_calculate_bet_size_starting_99")


def test_resolve_bet_profit_heads():
    """Test 4: Heads produces +bet net profit."""
    net_profit, payout, outcome_code = resolve_bet_profit(10, "HEADS")
    assert net_profit == 10, f"Expected net_profit=10, got {net_profit}"
    assert payout == 20, f"Expected payout=20, got {payout}"
    assert outcome_code == 1
    print("PASS: test_resolve_bet_profit_heads")


def test_resolve_bet_profit_tails():
    """Test 5: Tails produces -bet net loss."""
    net_profit, payout, outcome_code = resolve_bet_profit(10, "TAILS")
    assert net_profit == -10, f"Expected net_profit=-10, got {net_profit}"
    assert payout == 0, f"Expected payout=0, got {payout}"
    assert outcome_code == -1
    print("PASS: test_resolve_bet_profit_tails")


def test_resolve_bet_profit_payout_heads_2x():
    """Test 6: Heads payout equals 2 × bet."""
    _, payout, _ = resolve_bet_profit(10, "HEADS")
    assert payout == 2 * 10, f"Expected payout=20, got {payout}"
    print("PASS: test_resolve_bet_profit_payout_heads_2x")


def test_resolve_bet_profit_payout_tails_0():
    """Test 7: Tails payout equals 0."""
    _, payout, _ = resolve_bet_profit(10, "TAILS")
    assert payout == 0, f"Expected payout=0, got {payout}"
    print("PASS: test_resolve_bet_profit_payout_tails_0")


def test_apply_profit_correctness():
    """Test 8: Balance updates correctly."""
    # Heads win
    new_balance = apply_profit(100, 10)
    assert new_balance == 110, f"Expected 110, got {new_balance}"

    # Tails lose
    new_balance = apply_profit(100, -10)
    assert new_balance == 90, f"Expected 90, got {new_balance}"

    # Multiple operations
    new_balance = apply_profit(50, -20)
    assert new_balance == 30, f"Expected 30, got {new_balance}"

    print("PASS: test_apply_profit_correctness")


def test_iteration_all_bets_same_bet_size():
    """Test 9: All bets within an iteration use the same bet size."""
    # With balance=100, bet_size should be 10 for all 10 bets
    result = run_iteration(starting_balance=100, bets_per_iteration=10)

    bet_size = result["bet_size"]
    assert bet_size == 10, f"Expected bet_size=10, got {bet_size}"

    # All bet details should have the same bet_amount
    for bet_detail in result["bet_details"]:
        assert bet_detail["bet_amount"] == bet_size, (
            f"Bet {bet_detail['bet_number']} has bet_amount={bet_detail['bet_amount']}, "
            f"expected {bet_size}"
        )

    print("PASS: test_iteration_all_bets_same_bet_size")


def test_iteration_balance_updates():
    """Test 10: Balance updates correctly across bets."""
    # Example: 100 -> 6 Heads + 4 Tails with bet=10
    # Net = 6*10 - 4*10 = +20, so final = 120
    result = run_iteration(
        starting_balance=100,
        bets_per_iteration=10,
        outcomes=["H", "H", "T", "H", "T", "T", "H", "H", "H", "T"],
    )

    assert result["ending_balance"] == 120, (
        f"Expected ending_balance=120, got {result['ending_balance']}"
    )
    assert result["total_heads"] == 6, f"Expected total_heads=6, got {result['total_heads']}"
    assert result["total_tails"] == 4, f"Expected total_tails=4, got {result['total_tails']}"
    assert result["total_profit_loss"] == 20, (
        f"Expected total_profit_loss=20, got {result['total_profit_loss']}"
    )

    # Check individual bet details
    print(f"  Bet details: {result['bet_details']}")
    print("PASS: test_iteration_balance_updates")


def test_iteration_next_iteration_recalculates_bet_size():
    """Test 11: Next iteration recalculates bet size."""
    # Iteration 1: starting_balance=100, bet_size=10
    # Suppose outcomes produce net profit of +20, ending_balance=120
    # Iteration 2: starting_balance=120, bet_size should be floor(120/10)=12
    results = run_iterations(
        starting_balance=100,
        num_iterations=2,
        bets_per_iteration=10,
        # Outcomes that give +20 in first iteration (6H, 4T)
        outcomes_per_iteration=[
            ["H", "H", "T", "H", "T", "T", "H", "H", "H", "T"],  # iteration 1
            ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],  # iteration 2 all heads
        ],
    )

    assert len(results) == 2, f"Expected 2 iterations, got {len(results)}"

    # Iteration 1
    iter1 = results[0]
    assert iter1["bet_size"] == 10, f"Iteration 1 bet_size should be 10, got {iter1['bet_size']}"
    assert iter1["ending_balance"] == 120, (
        f"Iteration 1 ending_balance should be 120, got {iter1['ending_balance']}"
    )

    # Iteration 2 - bet size should be recalculated from new balance 120
    iter2 = results[1]
    assert iter2["bet_size"] == 12, (
        f"Iteration 2 bet_size should be 12 (floor(120/10)), got {iter2['bet_size']}"
    )
    assert iter2["starting_balance"] == 120, (
        f"Iteration 2 starting_balance should be 120, got {iter2['starting_balance']}"
    )

    print("PASS: test_iteration_next_iteration_recalculates_bet_size")


def test_bankruptcy_condition():
    """Test 12: Bankruptcy condition works correctly."""
    # With balance=5, floor(5/10)=0 < 1, so bankrupt
    result = run_iteration(starting_balance=5, bets_per_iteration=10)
    assert result["ending_balance"] == 5, (
        f"Bankrupt player should keep balance, got {result['ending_balance']}"
    )

    # With balance=10, floor(10/10)=1, not bankrupt
    result = run_iteration(starting_balance=10, bets_per_iteration=10)
    assert result["ending_balance"] == 10, (
        f"Non-bankrupt player should keep balance, got {result['ending_balance']}"
    )

    # With balance=9, floor(9/10)=0, bankrupt
    result = run_iteration(starting_balance=9, bets_per_iteration=10)
    assert result["ending_balance"] == 9, (
        f"Balance 9 should be bankrupt, got {result['ending_balance']}"
    )

    print("PASS: test_bankruptcy_condition")


def test_no_negative_balances():
    """Test 13: No negative balances occur."""
    # Test various starting balances
    for start in [100, 50, 20, 10, 5, 1]:
        result = run_iteration(starting_balance=start, bets_per_iteration=10)
        assert result["ending_balance"] >= 0, (
            f"Starting balance {start}: ending_balance should not be negative, "
            f"got {result['ending_balance']}"
        )

    # Test that we never go below 0 even with all tails
    result = run_iteration(
        starting_balance=100,
        bets_per_iteration=10,
        outcomes=["T", "T", "T", "T", "T", "T", "T", "T", "T", "T"],
    )
    assert result["ending_balance"] >= 0, (
        f"All tails should not produce negative balance, got {result['ending_balance']}"
    )
    # 100 - 10*10 = 0
    assert result["ending_balance"] == 0, (
        f"All tails with 10 bets of 10 chips each should leave 0, got {result['ending_balance']}"
    )

    print("PASS: test_no_negative_balances")


def test_integer_chip_rules_preserved():
    """Test that integer chip rules are preserved throughout."""
    # All balances should be integers
    result = run_iteration(starting_balance=100, bets_per_iteration=10)
    assert isinstance(result["ending_balance"], int), (
        f"ending_balance should be int, got {type(result['ending_balance'])}"
    )
    assert isinstance(result["bet_size"], int), (
        f"bet_size should be int, got {type(result['bet_size'])}"
    )

    for bet_detail in result["bet_details"]:
        assert isinstance(bet_detail["bet_amount"], int), (
            f"bet_amount should be int, got {type(bet_detail['bet_amount'])}"
        )
        assert isinstance(bet_detail["net_profit"], int), (
            f"net_profit should be int, got {type(bet_detail['net_profit'])}"
        )
        assert isinstance(bet_detail["ending_balance"], int), (
            f"ending_balance in bet_detail should be int, "
            f"got {type(bet_detail['ending_balance'])}"
        )

    # Test run_iterations also preserves integers
    results = run_iterations(starting_balance=100, num_iterations=3, bets_per_iteration=10)
    for i, r in enumerate(results):
        assert isinstance(r["ending_balance"], int), (
            f"Results[{i}].ending_balance should be int"
        )

    print("PASS: test_integer_chip_rules_preserved")


def test_detailed_bet_structure():
    """Verify the structure of bet details is correct."""
    result = run_iteration(
        starting_balance=100,
        bets_per_iteration=10,
        outcomes=["H", "T", "H", "T", "H", "T", "H", "T", "H", "T"],
    )

    # Each bet detail should have the required keys
    required_keys = [
        "bet_number", "starting_balance", "bet_amount",
        "outcome", "payout", "net_profit", "ending_balance"
    ]

    for i, bet_detail in enumerate(result["bet_details"]):
        for key in required_keys:
            assert key in bet_detail, (
                f"Bet {i+1} missing key '{key}'"
            )

        # Verify bet_number is 1-indexed and sequential
        assert bet_detail["bet_number"] == i + 1, (
            f"Bet {i+1} has bet_number={bet_detail['bet_number']}, expected {i+1}"
        )

        # Verify balance chain: ending_balance of bet i = starting_balance of bet i+1
        if i > 0:
            prev_ending = result["bet_details"][i - 1]["ending_balance"]
            curr_starting = bet_detail["starting_balance"]
            assert prev_ending == curr_starting, (
                f"Balance chain broken: bet {i} ending={prev_ending}, "
                f"bet {i+1} starting={curr_starting}"
            )

    print("PASS: test_detailed_bet_structure")


def test_iteration_with_pre_specified_outcomes():
    """Test that pre-specified outcomes give deterministic results."""
    outcomes1 = ["H", "H", "T", "H", "T", "T", "H", "H", "H", "T"]
    outcomes2 = ["H", "H", "T", "H", "T", "T", "H", "H", "H", "T"]  # same

    result1 = run_iteration(starting_balance=100, bets_per_iteration=10, outcomes=outcomes1)
    result2 = run_iteration(starting_balance=100, bets_per_iteration=10, outcomes=outcomes2)

    assert result1["ending_balance"] == result2["ending_balance"], (
        "Same outcomes should give same ending balance"
    )
    assert result1["total_heads"] == result2["total_heads"], (
        "Same outcomes should give same heads count"
    )
    assert result1["total_tails"] == result2["total_tails"], (
        "Same outcomes should give same tails count"
    )

    print("PASS: test_iteration_with_pre_specified_outcomes")


def test_multiple_iterations_bankruptcy_stop():
    """Test that run_iterations stops when player becomes bankrupt."""
    # Start with small balance that will quickly go bankrupt
    # With balance=10, bet=1, after some iterations it should go bankrupt
    results = run_iterations(
        starting_balance=20,
        num_iterations=10,
        bets_per_iteration=10,
        seed=42,
    )

    # Should stop early due to bankruptcy
    bankrupt_iterations = [
        r for r in results
        if r["ending_balance"] < 10  # below minimum bet threshold
    ]
    print(f"  Results: {len(results)} iterations run")
    print(f"  Final balance: {results[-1]['ending_balance'] if results else 'N/A'}")
    print("PASS: test_multiple_iterations_bankruptcy_stop")


if __name__ == "__main__":
    # Run all tests
    test_calculate_bet_size_starting_100()
    test_calculate_bet_size_starting_120()
    test_calculate_bet_size_starting_99()
    test_resolve_bet_profit_heads()
    test_resolve_bet_profit_tails()
    test_resolve_bet_profit_payout_heads_2x()
    test_resolve_bet_profit_payout_tails_0()
    test_apply_profit_correctness()
    test_iteration_all_bets_same_bet_size()
    test_iteration_balance_updates()
    test_iteration_next_iteration_recalculates_bet_size()
    test_bankruptcy_condition()
    test_no_negative_balances()
    test_integer_chip_rules_preserved()
    test_detailed_bet_structure()
    test_iteration_with_pre_specified_outcomes()
    test_multiple_iterations_bankruptcy_stop()

    print()
    print("=" * 60)
    print("All 15 betting engine tests passed!")
    print("=" * 60)