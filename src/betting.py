"""Core betting engine for the Probability & Betting Simulation project.

Implements the repeated-betting mechanics with integer-chip arithmetic.
One iteration consists of exactly 10 bets, all using the same bet size
determined at the start of the iteration. After the iteration, bet size
is recalculated based on the new balance.

Rules (as specified):
- Starting capital: 100 chips
- One iteration = exactly 10 bets
- Bet size = floor(current_balance / 10) at iteration start
- All 10 bets within an iteration use the same bet size
- Heads: win, payout = 2 × bet, net profit = +bet
- Tails: loss, payout = 0, net profit = -bet
- New balance = balance + net_profit
- Bankruptcy: floor(balance / 10) < 1
- Integer chips only - no floating point
"""

from typing import Literal, Tuple, List, Dict, Any

CoinSide = Literal["HEADS", "TAILS"]
Side = Literal["HEADS", "TAILS"]
IterationResult = Dict[str, Any]


def calculate_bet_size(balance: int, bets_per_iteration: int = 10) -> int:
    """Calculate the bet size for one iteration.

    Bet size = floor(balance / 10), determined at the start of the iteration.
    All bets within the iteration use this fixed bet size.

    Args:
        balance: Current chip balance at the start of the iteration.
        bets_per_iteration: Number of bets in the iteration (default 10).

    Returns:
        Bet size integer (floor division).
    """
    return balance // bets_per_iteration


def resolve_bet_profit(bet_size: int, outcome: Side) -> Tuple[int, int, int]:
    """Calculate the profit, payout, and result for a single bet.

    Rules:
    - Heads: payout = 2 × bet, net profit = +bet (stake returned in payout)
    - Tails: payout = 0, net profit = -bet

    Args:
        bet_size: The amount bet on this single bet.
        outcome: Either "HEADS" or "TAILS".

    Returns:
        Tuple of (net_profit, payout, outcome_code) where:
        - net_profit: +bet for HEADS, -bet for TAILS
        - payout: 2×bet for HEADS, 0 for TAILS (stake included in payout)
        - outcome_code: 1 for HEADS, -1 for TAILS
    """
    if outcome == "HEADS":
        net_profit = bet_size
        payout = 2 * bet_size
        outcome_code = 1
    else:  # TAILS
        net_profit = -bet_size
        payout = 0
        outcome_code = -1

    return net_profit, payout, outcome_code


def apply_profit(balance: int, net_profit: int) -> int:
    """Apply net profit/loss to the current balance.

    New balance = balance + net_profit

    Args:
        balance: Current chip balance.
        net_profit: Profit or loss from a bet (can be positive or negative).

    Returns:
        New chip balance after applying profit. Always an integer.
    """
    return balance + net_profit


def check_bankruptcy(balance: int, minimum_bet: int = 1) -> bool:
    """Check if the player is bankrupt.

    Bankruptcy occurs when floor(balance / 10) < 1,
    meaning the player cannot place the minimum 1-chip bet.

    Args:
        balance: Current chip balance.
        minimum_bet: Minimum bet size required to continue (default 1).

    Returns:
        True if bankrupt, False otherwise.
    """
    return (balance // 10) < minimum_bet


def run_single_bet(
    balance: int,
    bet_size: int,
    outcome: Side,
) -> Tuple[int, int, int, int]:
    """Run a single bet and return the results.

    Args:
        balance: Balance before the bet.
        bet_size: The bet amount for this bet.
        outcome: Either "HEADS" or "TAILS".

    Returns:
        Tuple of (new_balance, net_profit, payout, outcome_code).
    """
    net_profit, payout, outcome_code = resolve_bet_profit(bet_size, outcome)
    new_balance = apply_profit(balance, net_profit)

    return new_balance, net_profit, payout, outcome_code


def run_iteration(
    starting_balance: int,
    bets_per_iteration: int = 10,
    win_side: Side = "HEADS",
    loss_side: Side = "TAILS",
    outcomes: List[Side] | None = None,
    rng: Any = None,
) -> IterationResult:
    """Run one iteration of exactly N bets.

    Key feature: bet size is determined once at the start of the iteration
    and is fixed for all N bets within that iteration. After the iteration,
    the caller should recalculate bet size based on the returned ending balance.

    Args:
        starting_balance: Chip balance at the start of the iteration.
        bets_per_iteration: Number of bets in the iteration (default 10).
        win_side: The winning side (default "HEADS").
        loss_side: The losing side (default "TAILS").
        outcomes: Optional pre-specified list of outcomes for each bet.
                  If provided, must have length = bets_per_iteration.
        rng: Optional random.Random instance for reproducibility.
             Ignored if outcomes are pre-specified.

    Returns:
        Dictionary with iteration-level and per-bet details:
        {
            "iteration": iteration_number,
            "starting_balance": starting_balance,
            "bet_size": bet_size,
            "bets_per_iteration": bets_per_iteration,
            "bet_details": [
                {
                    "bet_number": 1,
                    "starting_balance": balance_before_bet_1,
                    "bet_amount": bet_size,
                    "outcome": "HEADS",
                    "payout": 20,
                    "net_profit": 10,
                    "ending_balance": 110,
                },
                ...
            ],
            "ending_balance": final_balance,
            "total_heads": count_of_heads,
            "total_tails": count_of_tails,
            "total_profit_loss": net_profit_over_all_bets,
        }

    Raises:
        ValueError: If outcomes list length doesn't match bets_per_iteration.
    """
    import random

    if outcomes is not None:
        if len(outcomes) != bets_per_iteration:
            raise ValueError(
                f"outcomes list length ({len(outcomes)}) must match "
                f"bets_per_iteration ({bets_per_iteration})"
            )
        outcome_iter = iter(outcomes)
    elif rng is not None:
        outcome_iter = (rng.choice([win_side, loss_side]) for _ in range(bets_per_iteration))
    else:
        # Default: 50/50 using random module
        outcome_iter = (random.choice([win_side, loss_side]) for _ in range(bets_per_iteration))

    # Calculate bet size once at the start of the iteration
    bet_size = calculate_bet_size(starting_balance)

    # Check bankruptcy before starting
    if check_bankruptcy(starting_balance):
        return {
            "iteration": 1,
            "starting_balance": starting_balance,
            "bet_size": bet_size,
            "bets_per_iteration": bets_per_iteration,
            "bet_details": [],
            "ending_balance": starting_balance,
            "total_heads": 0,
            "total_tails": 0,
            "total_profit_loss": 0,
        }

    bet_details = []
    current_balance = starting_balance
    total_heads = 0
    total_tails = 0
    total_profit_loss = 0

    for bet_number in range(1, bets_per_iteration + 1):
        # Get the outcome for this bet
        try:
            outcome = next(outcome_iter)
        except StopIteration:
            break

        # Record starting balance before this bet
        balance_before = current_balance

        # Run the bet
        new_balance, net_profit, payout, outcome_code = run_single_bet(
            balance=balance_before,
            bet_size=bet_size,
            outcome=outcome,
        )

        # Track statistics
        if outcome == "HEADS":
            total_heads += 1
        else:
            total_tails += 1

        total_profit_loss += net_profit
        current_balance = new_balance

        # Record bet detail
        bet_detail = {
            "bet_number": bet_number,
            "starting_balance": balance_before,
            "bet_amount": bet_size,
            "outcome": outcome,
            "payout": payout,
            "net_profit": net_profit,
            "ending_balance": new_balance,
        }
        bet_details.append(bet_detail)

    return {
        "iteration": 1,  # This is the first (and only) iteration run
        "starting_balance": starting_balance,
        "bet_size": bet_size,
        "bets_per_iteration": bets_per_iteration,
        "bet_details": bet_details,
        "ending_balance": current_balance,
        "total_heads": total_heads,
        "total_tails": total_tails,
        "total_profit_loss": total_profit_loss,
    }


def run_iterations(
    starting_balance: int,
    num_iterations: int,
    bets_per_iteration: int = 10,
    win_side: Side = "HEADS",
    loss_side: Side = "TAILS",
    outcomes_per_iteration: List[List[Side]] | None = None,
    seed: int | None = None,
) -> List[IterationResult]:
    """Run multiple iterations of the betting game.

    After each iteration, the bet size is recalculated based on the ending
    balance of the previous iteration. The simulation stops if the player
    becomes bankrupt (floor(balance / 10) < 1).

    Args:
        starting_balance: Starting chip balance for the first iteration.
        num_iterations: Number of iterations to run.
        bets_per_iteration: Number of bets per iteration (default 10).
        win_side: The winning side (default "HEADS").
        loss_side: The losing side (default "TAILS").
        outcomes_per_iteration: Optional nested list of outcomes.
                                Each inner list should have length = bets_per_iteration.
        seed: Optional random seed for reproducibility.

    Returns:
        List of iteration result dictionaries, one per iteration run.
        Simulation stops early if bankruptcy occurs.
    """
    import random

    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = None

    results = []
    current_balance = starting_balance

    for iteration_num in range(1, num_iterations + 1):
        # Prepare outcomes for this iteration if provided
        if outcomes_per_iteration is not None:
            # Pull the correct sub-list for this iteration
            iter_index = iteration_num - 1
            if iter_index < len(outcomes_per_iteration):
                iteration_outcomes = outcomes_per_iteration[iter_index]
            else:
                iteration_outcomes = None
        else:
            iteration_outcomes = None

        # Run one iteration
        result = run_iteration(
            starting_balance=current_balance,
            bets_per_iteration=bets_per_iteration,
            win_side=win_side,
            loss_side=loss_side,
            outcomes=iteration_outcomes,
            rng=rng,
        )

        # Add iteration number to the result
        result["iteration"] = iteration_num

        # Check bankruptcy - stop if bankrupt
        if check_bankruptcy(result["ending_balance"]):
            results.append(result)
            break

        # Update balance for next iteration
        current_balance = result["ending_balance"]

        results.append(result)

    return results