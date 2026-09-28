"""Utility functions for the Probability & Betting Simulation project.

General-purpose helpers used across the project for data processing,
result formatting, and common operations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def generate_experiment_id(experiment_name: str, timestamp: bool = True) -> str:
    """Generate a unique experiment ID.

    Args:
        experiment_name: Name of the experiment.
        timestamp: Whether to include a timestamp component.

    Returns:
        Unique experiment ID string.
    """
    import time as time_module

    timestamp_str = (
        datetime.now().strftime("%Y%m%d_%H%M%S")
        if timestamp
        else ""
    )
    unique_id = f"{experiment_name}_{timestamp_str}_{int(time_module.time())}"
    return unique_id


def format_balance_history(
    balances: List[int],
) -> Dict[str, int | float]:
    """Format a balance history into summary statistics.

    Args:
        balances: List of balance values over time.

    Returns:
        Dictionary with summary statistics.
    """
    if not balances:
        return {
            "initial_balance": 0,
            "final_balance": 0,
            "min_balance": 0,
            "max_balance": 0,
            "net_change": 0,
            "net_change_percent": 0.0,
        }

    initial = balances[0]
    final = balances[-1]
    net_change = final - initial
    net_change_percent = (net_change / initial) * 100 if initial != 0 else 0.0

    return {
        "initial_balance": initial,
        "final_balance": final,
        "min_balance": min(balances),
        "max_balance": max(balances),
        "net_change": net_change,
        "net_change_percent": net_change_percent,
    }


def write_json_results(
    data: Dict[str, Any],
    output_path: str,
    experiment_id: str | None = None,
) -> None:
    """Write results to a JSON file, preserving previous runs.

    Args:
        data: Dictionary of results data to write.
        output_path: Path to the output JSON file.
        experiment_id: Optional experiment ID for naming.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing results if file exists, to preserve them
    existing_data = {}
    if output_file.exists():
        with open(output_file, "r") as f:
            existing_data = json.load(f)

    # Merge: add new data under experiment ID if provided
    if experiment_id:
        existing_data[experiment_id] = data
    else:
        existing_data.update(data)

    with open(output_file, "w") as f:
        json.dump(existing_data, f, indent=2, default=str)


def read_json_results(
    input_path: str,
) -> Dict[str, Any]:
    """Read results from a JSON file.

    Args:
        input_path: Path to the JSON file to read.

    Returns:
        Dictionary of results data.
    """
    input_file = Path(input_path)
    if input_file.exists():
        with open(input_file, "r") as f:
            return json.load(f)
    return {}


def validate_bankruptcy_rule(
    balance: int,
    rule: str = "balance_below_minimum_bet",
    minimum_bet: int = 1,
) -> bool:
    """Validate bankruptcy based on the specified rule.

    Args:
        balance: Current chip balance.
        rule: Bankruptcy rule to apply.
        minimum_bet: Minimum bet size required.

    Returns:
        True if the player is considered bankrupt under the rule.
    """
    if rule == "balance_below_minimum_bet":
        return (balance // 10) < minimum_bet
    return False


def validate_config(config: dict) -> None:
    """Validate configuration dictionary, raising ValueError for invalid params.

    Checks:
    - bets_per_iteration must be > 0
    - starting_chips must be >= 0
    - win_multiplier must be > 0
    - number_of_simulations must be > 0
    - coin_flips must be > 0

    Args:
        config: Dictionary of configuration values.

    Raises:
        ValueError: If any configuration value is invalid.
    """
    errors = []

    bets_per_iteration = config.get("bets_per_iteration", 10)
    if not isinstance(bets_per_iteration, int) or bets_per_iteration <= 0:
        errors.append(f"bets_per_iteration must be a positive integer, got {bets_per_iteration}")

    starting_chips = config.get("starting_chips", 100)
    if not isinstance(starting_chips, int) or starting_chips < 0:
        errors.append(f"starting_chips must be a non-negative integer, got {starting_chips}")

    win_multiplier = config.get("win_multiplier", 2)
    if not isinstance(win_multiplier, (int, float)) or win_multiplier <= 0:
        errors.append(f"win_multiplier must be a positive number, got {win_multiplier}")

    number_of_simulations = config.get("number_of_simulations", 1)
    if not isinstance(number_of_simulations, int) or number_of_simulations <= 0:
        errors.append(f"number_of_simulations must be a positive integer, got {number_of_simulations}")

    coin_flips = config.get("coin_flips", 100)
    if not isinstance(coin_flips, int) or coin_flips <= 0:
        errors.append(f"coin_flips must be a positive integer, got {coin_flips}")

    if errors:
        raise ValueError("Configuration validation errors:\n" + "\n".join(f"  - {e}" for e in errors))