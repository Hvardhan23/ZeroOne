"""Core simulation logic for running coin flips and betting experiments.

Separates simulation logic from experiment definitions and analysis.
Handles running multiple simulations, managing state, and collecting results.
"""

from typing import Literal, Optional
import json
import time
import random

from .coin import simulate_flips
from .betting import run_iteration, check_bankruptcy as is_bankrupt

Side = Literal["HEADS", "TAILS"]


def run_coin_simulation(
    num_flips: int,
    seed: int | None = None,
) -> dict[str, int]:
    """Run a coin flip simulation for a given number of flips.

    Args:
        num_flips: Number of coin flips to simulate.
        seed: Optional random seed for reproducibility.

    Returns:
        Dictionary with HEADS and TAILS counts.
    """
    return simulate_flips(num_flips=num_flips, seed=seed)


def run_betting_simulation(
    starting_chips: int,
    num_simulations: int = 1,
    bets_per_iteration: int = 10,
    win_side: Side = "HEADS",
    loss_side: Side = "TAILS",
    seed: int | None = None,
) -> dict[str, object]:
    """Run multiple betting simulations.

    Each simulation runs iterations of 10 bets until bankruptcy.
    The simulation stops when the player becomes bankrupt.

    Args:
        starting_chips: Starting number of chips for each simulation.
        num_simulations: Number of independent simulations to run.
        bets_per_iteration: Number of bets per iteration (default 10).
        win_side: The winning side (default "HEADS").
        loss_side: The losing side (default "TAILS").
        seed: Optional random seed for reproducibility.

    Returns:
        Dictionary containing simulation results including:
        - starting_chips, final_bankruptcy_status, num_simulations,
          results (list of final balances per simulation), runtime.
    """
    import random

    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    results = []

    for _ in range(num_simulations):
        balance = starting_chips
        iteration = 0

        while not is_bankrupt(balance):
            iteration += 1
            result = run_iteration(
                starting_balance=balance,
                bets_per_iteration=bets_per_iteration,
                win_side=win_side,
                loss_side=loss_side,
                rng=rng,
            )
            balance = result["ending_balance"]

        results.append(balance)

    return {
        "starting_chips": starting_chips,
        "num_simulations": num_simulations,
        "bets_per_iteration": bets_per_iteration,
        "win_side": win_side,
        "loss_side": loss_side,
        "results": results,
        "final_balances": results,
        "bankruptcy_count": sum(1 for r in results if r == 0),
        "surviving_count": sum(1 for r in results if r > 0),
        "runtime_seconds": time.time(),
    }
def run_monte_carlo(
    starting_chips: int,
    number_of_simulations: int,
    master_seed: int | None = None,
    bets_per_iteration: int = 10,
    win_side: Side = "HEADS",
    loss_side: Side = "TAILS",
    save_detailed: bool = True,
) -> dict[str, object]:
    """Run a Monte Carlo simulation of the betting strategy.

    Runs multiple independent simulations of the betting game, each starting
    from the same number of chips but with independent randomness.

    Key features:
    - Reproducibility: if master_seed is supplied, child seeds are derived
      as master_seed + simulation_index, so rerunning produces the exact same
      results.
    - Each simulation has its own seed, so outcomes differ between simulations.
    - Can disable detailed per-simulation data saving for large experiments
      (save_detailed=false) to reduce storage requirements.

    Args:
        starting_chips: Starting chip balance for each simulation.
        number_of_simulations: Number of independent simulations to run.
        master_seed: Optional master seed for reproducibility.
          If supplied, child seeds are master_seed + simulation_index.
          If None, each simulation uses independent random seeds.
        bets_per_iteration: Number of bets per iteration (default 10).
        win_side: The winning side (default "HEADS").
        loss_side: The losing side (default "TAILS").
        save_detailed: If True, save per-simulation detail data.
          Set False for large experiments (e.g., 10,000 simulations) to
          reduce storage requirements.

    Returns:
        Dictionary containing:
        - simulation_results: list of per-simulation dictionaries, each with:
            simulation_id, experiment_id, scenario, starting_chips,
            total_iterations, total_bets, total_heads, total_tails,
            final_balance, maximum_balance, minimum_balance,
            total_profit_loss, bankrupt, bankruptcy_iteration,
            random_seed
        - summary: dictionary with aggregate statistics:
            number_of_simulations, number_bankrupt, bankruptcy_rate,
            number_profitable, profitability_rate,
            average_final_balance, median_final_balance,
            minimum_final_balance, maximum_final_balance,
            average_iterations_survived, median_iterations_survived,
            average_maximum_balance, median_maximum_balance
        - experiment_id: unique experiment run ID
        - master_seed: the master seed used (or None)
    """
    import random as random_module

    # Determine seeds for each simulation
    if master_seed is not None:
        # Use master_seed + i for each simulation for reproducibility
        simulation_seeds = [master_seed + i for i in range(number_of_simulations)]
    else:
        # Use independent random seeds
        simulation_seeds = [
            random_module.randint(1, 2**31 - 1) for _ in range(number_of_simulations)
        ]

    # Run each simulation
    simulation_results: list[dict[str, object]] = []

    for sim_idx in range(number_of_simulations):
        seed = simulation_seeds[sim_idx]
        rng = random_module.Random(seed)

        # Track per-simulation statistics
        sim_starting_chips = starting_chips
        current_balance = starting_chips
        iterations_survived = 0
        total_heads = 0
        total_tails = 0
        max_balance = starting_chips
        min_balance = starting_chips
        total_profit_loss = 0
        bankruptcy_iteration: int | None = None
        bankrupt = False

        # Iterate until bankruptcy
        while not is_bankrupt(current_balance):
            iterations_survived += 1

            # Run one iteration of 10 bets
            result = run_iteration(
                starting_balance=current_balance,
                bets_per_iteration=bets_per_iteration,
                win_side=win_side,
                loss_side=loss_side,
                rng=rng,
            )

            # Update tracking
            current_balance = result["ending_balance"]
            total_profit_loss += result["total_profit_loss"]
            total_heads += result["total_heads"]
            total_tails += result["total_tails"]

            # Update max/min balance
            if current_balance > max_balance:
                max_balance = current_balance
            if current_balance < min_balance:
                min_balance = current_balance

            # Check for bankruptcy after this iteration
            if is_bankrupt(current_balance) and not bankrupt:
                bankrupt = True
                bankruptcy_iteration = iterations_survived

        # After the simulation (player is bankrupt or no more iterations possible)
        final_balance = current_balance
        profit_loss = final_balance - starting_chips

        if bankrupt:
            # Player went bankrupt
            pass  # bankruptcy_iteration already set

        # Build per-simulation result
        sim_result: dict[str, object] = {
            "simulation_id": f"SIM_{sim_idx + 1}",
            "experiment_id": f"EXP_{int(time.time())}_{sim_idx}",
            "scenario": "baseline",  # Will be overridden by caller
            "starting_chips": starting_chips,
            "total_iterations": iterations_survived,
            "total_bets": iterations_survived * bets_per_iteration,
            "total_heads": total_heads,
            "total_tails": total_tails,
            "final_balance": final_balance,
            "maximum_balance": max_balance,
            "minimum_balance": min_balance,
            "total_profit_loss": profit_loss,
            "bankrupt": bankrupt,
            "bankruptcy_iteration": bankruptcy_iteration,
            "random_seed": seed,
        }

        simulation_results.append(sim_result)

    # Calculate summary statistics
    num_sim = number_of_simulations
    bankrupt_count = sum(1 for s in simulation_results if s["bankrupt"])
    bankruptcy_rate = bankrupt_count / num_sim if num_sim > 0 else 0

    profitable_count = sum(1 for s in simulation_results if s["total_profit_loss"] > 0)
    profitability_rate = profitable_count / num_sim if num_sim > 0 else 0

    final_balances = [s["final_balance"] for s in simulation_results]
    average_final_balance = sum(final_balances) / num_sim if num_sim > 0 else 0
    median_final_balance = (
        sorted(final_balances)[num_sim // 2] if num_sim > 0 else 0
    )
    minimum_final_balance = min(final_balances) if final_balances else 0
    maximum_final_balance = max(final_balances) if final_balances else 0

    iterations_survived_list = [s["total_iterations"] for s in simulation_results]
    average_iterations_survived = sum(iterations_survived_list) / num_sim if num_sim > 0 else 0
    median_iterations_survived = (
        sorted(iterations_survived_list)[num_sim // 2] if num_sim > 0 else 0
    )

    maximum_balances = [s["maximum_balance"] for s in simulation_results]
    average_maximum_balance = sum(maximum_balances) / num_sim if num_sim > 0 else 0
    median_maximum_balance = (
        sorted(maximum_balances)[num_sim // 2] if num_sim > 0 else 0
    )

    # Build summary
    summary: dict[str, object] = {
        "number_of_simulations": num_sim,
        "number_bankrupt": bankrupt_count,
        "bankruptcy_rate": bankruptcy_rate,
        "number_profitable": profitable_count,
        "profitability_rate": profitability_rate,
        "average_final_balance": average_final_balance,
        "median_final_balance": median_final_balance,
        "minimum_final_balance": minimum_final_balance,
        "maximum_final_balance": maximum_final_balance,
        "average_iterations_survived": average_iterations_survived,
        "median_iterations_survived": median_iterations_survived,
        "average_maximum_balance": average_maximum_balance,
        "median_maximum_balance": median_maximum_balance,
    }

    # Build experiment ID
    experiment_id = f"MC_{int(time.time())}"

    return {
        "simulation_results": simulation_results,
        "summary": summary,
        "experiment_id": experiment_id,
        "master_seed": master_seed,
    }
