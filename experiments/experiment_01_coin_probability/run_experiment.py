"""Experiment 1: Coin Probability.

Studies the observed probability of Heads vs Tails using repeated coin flips.

Experiment supports multiple flip counts configured in experiment_config.yaml.
Uses ResultManager for result persistence.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import csv
import yaml

from src.coin import simulate_flips
from src.results import ResultManager


def run_single_simulation(
    num_flips: int,
    seed: int | None = None,
) -> dict[str, int | float]:
    """Run a single coin flip simulation.

    Args:
        num_flips: Number of coin flips to simulate.
        seed: Optional random seed for reproducibility.

    Returns:
        Dictionary with simulation results.
    """
    from src.coin import simulate_flips as _simulate_flips
    result = _simulate_flips(num_flips=num_flips, seed=seed)

    total_heads = result["HEADS"]
    total_tails = result["TAILS"]
    total_flips = total_heads + total_tails

    heads_probability = total_heads / total_flips if total_flips > 0 else 0
    tails_probability = total_tails / total_flips if total_flips > 0 else 0

    return {
        "num_flips": num_flips,
        "heads": total_heads,
        "tails": total_tails,
        "heads_probability": heads_probability,
        "tails_probability": tails_probability,
        "theoretical_heads_probability": 0.5,
        "theoretical_tails_probability": 0.5,
        "heads_probability_difference": heads_probability - 0.5,
        "tails_probability_difference": tails_probability - 0.5,
    }


def main():
    """Run the coin probability experiment."""
    # Load configuration
    config_path = project_root / "config" / "experiment_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Get flip counts from config, fallback to defaults
    flip_counts = config.get("coin_flip_counts", [100, 1000, 10000, 100000, 1000000])
    if isinstance(flip_counts, int):
        flip_counts = [flip_counts]

    seed = config.get("random_seed")

    # Initialize ResultManager
    results_manager = ResultManager("results")

    print("=" * 60)
    print("Coin Flip Probability Experiment")
    print("=" * 60)
    print()

    all_results = []

    for i, num_flips in enumerate(flip_counts):
        current_seed = None if seed is None else seed + i

        result = run_single_simulation(
            num_flips=num_flips,
            seed=current_seed,
        )
        all_results.append(result)

        # Build summary data
        summary_data = {
            "total_flips": result["num_flips"],
            "heads": result["heads"],
            "tails": result["tails"],
            "heads_probability": result["heads_probability"],
            "tails_probability": result["tails_probability"],
            "theoretical_heads_probability": 0.5,
            "theoretical_tails_probability": 0.5,
            "heads_probability_difference": result["heads_probability_difference"],
            "tails_probability_difference": result["tails_probability_difference"],
        }

        # Save summary using ResultManager
        # The returned experiment_id can be used for CSV files if needed
        saved_id = results_manager.save_summary(
            experiment_name="coin_probability",
            scenario=None,
            configuration={"num_flips": num_flips, "random_seed": current_seed},
            random_seed=current_seed,
            results=summary_data,
            status="COMPLETED",
        )

        # Write detailed per-flip CSV
        # Experiment 1 detailed format: experiment_id, flip_number, outcome
        detailed_path = Path("results") / f"detailed_{saved_id}.csv"

        outcomes = []
        # We need to generate the outcomes to write to CSV
        # Since simulate_flips doesn't return individual outcomes in the basic API,
        # let's use the outcomes from the result if available, or regenerate
        from src.coin import simulate_flips as _simulate_flips
        sim_result = _simulate_flips(num_flips=num_flips, seed=current_seed)
        outcomes = sim_result.get("outcomes", [])

        with open(detailed_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["experiment_id", "flip_number", "outcome"])
            for j, outcome in enumerate(outcomes):
                writer.writerow([saved_id, j + 1, outcome])

        # Print per-scenario summary
        print(f"Flips: {num_flips}: Heads={result['heads']}, Tails={result['tails']}, "
              f"Heads prob={result['heads_probability']:.4f}")

    # Print overall summary
    print()
    print("=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print()
    for result in all_results:
        print(f"Total flips:     {result['num_flips']}")
        print(f"Heads:           {result['heads']}")
        print(f"Tails:           {result['tails']}")
        print(f"Observed Heads prob:  {result['heads_probability']:.4f}")
        print(f"Observed Tails prob:  {result['tails_probability']:.4f}")
        print(f"Theoretical Heads prob:  {result['theoretical_heads_probability']}")
        print(f"Theoretical Tails prob:  {result['theoretical_tails_probability']}")
        print()
        print("-" * 60)
        print()

    # List saved summaries
    print(f"Saved {len(list(Path('results/summaries').glob('*.json')))} summary(ies)")


if __name__ == "__main__":
    main()