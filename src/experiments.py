"""Experiment definitions and configuration management.

Separates experiment definitions from simulation logic and analysis.
Handles experiment configuration, running experiments, and result organization.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from .simulation import run_coin_simulation, run_betting_simulation
from .betting import check_bankruptcy
from .utils import validate_config


def load_config(config_path: str = "config/experiment_config.yaml") -> Dict[str, Any]:
    """Load experiment configuration from YAML file.

    Args:
        config_path: Path to the configuration YAML file.

    Returns:
        Dictionary of configuration values.

    Raises:
        ValueError: If configuration values are invalid.
    """
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    validate_config(config)
    return config


def get_experiment_config(
    experiment_name: str,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Get configuration for a specific experiment.

    Args:
        experiment_name: Name of the experiment to configure.
        config: Optional configuration dictionary (loaded from file if not provided).

    Returns:
        Dictionary of experiment-specific configuration values.
    """
    if config is None:
        config = load_config()

    experiment_configs = {
        "coin_probability": {
            "starting_chips": config.get("starting_chips", 100),
            "num_flips": config.get("coin_flips", 100),
            "random_seed": config.get("random_seed"),
            "number_of_simulations": config.get("number_of_simulations", 1),
        },
        "betting_strategy": {
            "starting_chips": config.get("starting_chips", 100),
            "bets_per_iteration": config.get("bets_per_iteration", 10),
            "win_side": config.get("win_side", "HEADS"),
            "loss_side": config.get("loss_side", "TAILS"),
            "win_multiplier": config.get("win_multiplier", 2),
            "minimum_bet": config.get("minimum_bet", 1),
            "bankruptcy_rule": config.get("bankruptcy_rule", "balance_below_minimum_bet"),
            "coin_flips": config.get("coin_flips", 100),
            "random_seed": config.get("random_seed"),
            "number_of_simulations": config.get("number_of_simulations", 1),
            "starting_capital_scenarios": config.get(
                "starting_capital_scenarios", [100]
            ),
        },
    }

    return experiment_configs.get(experiment_name, {})


def run_coin_experiment(
    experiment_name: str = "coin_probability",
    config_path: str = "config/experiment_config.yaml",
    output_dir: str = "data/results",
) -> Dict[str, Any]:
    """Run Experiment 1: Coin Probability experiment.

    Studies the observed probability of Heads vs Tails using repeated coin flips.

    Args:
        experiment_name: Name of the experiment.
        config_path: Path to configuration YAML file.
        output_dir: Base directory for output results.

    Returns:
        Dictionary of experiment results.
    """
    config = load_config(config_path)
    experiment_config = get_experiment_config("coin_probability", config)

    num_flips = experiment_config.get("num_flips", 100)
    seed = experiment_config.get("random_seed")
    num_simulations = experiment_config.get("number_of_simulations", 1)

    all_results = []

    for i in range(num_simulations):
        result = run_coin_simulation(
            num_flips=num_flips,
            seed=None if seed is None else seed + i,
        )
        all_results.append(result)

    # Calculate observed probabilities
    total_flips = sum(r["HEADS"] + r["TAILS"] for r in all_results)
    total_heads = sum(r["HEADS"] for r in all_results)
    total_tails = sum(r["TAILS"] for r in all_results)

    return {
        "experiment_name": experiment_name,
        "num_flips_per_simulation": num_flips,
        "num_simulations": num_simulations,
        "total_flips": total_flips,
        "total_heads": total_heads,
        "total_tails": total_tails,
        "observed_heads_probability": total_heads / total_flips if total_flips > 0 else 0,
        "observed_tails_probability": total_tails / total_flips if total_flips > 0 else 0,
        "expected_heads_probability": 0.5,
        "expected_tails_probability": 0.5,
        "results": all_results,
    }


def run_betting_experiment(
    experiment_name: str = "betting_strategy",
    config_path: str = "config/experiment_config.yaml",
    output_dir: str = "data/results",
    starting_chip_scenarios: Optional[list[int]] = None,
) -> Dict[str, Any]:
    """Run Experiment 2: Betting Strategy experiment.

    Studies a betting strategy where a person starts with a fixed number of chips
    and repeatedly makes 10 equally distributed bets.

    Args:
        experiment_name: Name of the experiment.
        config_path: Path to configuration YAML file.
        output_dir: Base directory for output results.
        starting_chip_scenarios: List of starting chip levels to test.

    Returns:
        Dictionary of experiment results.
    """
    config = load_config(config_path)
    experiment_config = get_experiment_config("betting_strategy", config)

    if starting_chip_scenarios is None:
        starting_chip_scenarios = experiment_config.get(
            "starting_capital_scenarios", [100]
        )

    bets_per_iteration = experiment_config.get("bets_per_iteration", 10)
    win_side = experiment_config.get("win_side", "HEADS")
    loss_side = experiment_config.get("loss_side", "TAILS")
    seed = experiment_config.get("random_seed")
    num_simulations = experiment_config.get("number_of_simulations", 1)

    all_results = []

    for chips in starting_chip_scenarios:
        sim_result = run_betting_simulation(
            starting_chips=chips,
            num_simulations=num_simulations,
            bets_per_iteration=bets_per_iteration,
            win_side=win_side,
            loss_side=loss_side,
            seed=seed,
        )
        all_results.append(
            {
                "starting_chips": chips,
                "num_simulations": num_simulations,
                "final_balances": sim_result["results"],
                "bankruptcy_count": sim_result["bankruptcy_count"],
                "surviving_count": sim_result["surviving_count"],
                "bankruptcy_rate": (
                    sim_result["bankruptcy_count"] / num_simulations
                    if num_simulations > 0
                    else 0
                ),
            }
        )

    return {
        "experiment_name": experiment_name,
        "starting_chip_scenarios": starting_chip_scenarios,
        "bets_per_iteration": bets_per_iteration,
        "win_side": win_side,
        "loss_side": loss_side,
        "num_simulations": num_simulations,
        "simulation_results": all_results,
    }