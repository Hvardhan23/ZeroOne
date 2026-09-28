"""Statistical analysis layer for Probability & Betting Simulation.

Reads existing saved result files and calculates metrics without modifying
raw experiment data. Supports analysis of single experiments or comparisons
across multiple scenarios.

Key design principles:
- Non-destructive: reads only, does not modify raw result files
- No numpy dependency: uses pure Python calculations
- Configurable: accepts file paths or loaded dictionaries
- Reusable: can analyze any experiment following the result format
- Well-documented: each metric and formula explained
"""

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_result_summaries(summaries_dir: str = "results/summaries") -> List[Dict[str, Any]]:
    """Load all result summary JSON files from the summaries directory.

    Args:
        summaries_dir: Path to the summaries directory.

    Returns:
        List of dictionaries, one per experiment run.
    """
    summaries_path = Path(summaries_dir)
    if not summaries_path.exists():
        return []

    results = []
    for sf in sorted(summaries_path.glob("*.json")):
        try:
            with open(sf, "r") as f:
                data = json.load(f)
            results.append(data)
        except (json.JSONDecodeError, IOError):
            continue

    return results


def classify_outcome(
    final_balance: float, starting_balance: float
) -> str:
    """Classify a simulation's outcome into one of four categories.

    Categories:
    - "profit": final_balance > starting_balance
    - "break_even": final_balance == starting_balance
    - "loss": final_balance < starting_balance (and not bankrupt)
    - "bankrupt": simulation ended in bankruptcy

    Note: A bankrupt simulation is also classified as "loss" but tracked
    separately as "bankrupt" per the project's important distinction.

    Args:
        final_balance: The simulation's final balance.
        starting_balance: The simulation's starting balance.

    Returns:
        One of "profit", "break_even", "loss", or "bankrupt".
    """
    if final_balance == 0:
        return "bankrupt"
    elif final_balance > starting_balance:
        return "profit"
    elif final_balance == starting_balance:
        return "break_even"
    else:
        return "loss"


def calculate_descriptive_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate descriptive statistics for a list of numeric values.

    Args:
        values: List of numeric values.

    Returns:
        Dictionary with mean, median, min, max, std, variance, quartiles, percentiles.
    """
    if not values:
        return {
            "mean": 0.0,
            "median": 0.0,
            "minimum": 0.0,
            "maximum": 0.0,
            "standard_deviation": 0.0,
            "variance": 0.0,
            "quartile_1": 0.0,
            "quartile_3": 0.0,
            "percentile_25": 0.0,
            "percentile_75": 0.0,
        }

    values_sorted = sorted(values)
    n = len(values_sorted)

    # Mean
    mean_val = sum(values_sorted) / n

    # Median
    if n % 2 == 1:
        median_val = values_sorted[n // 2]
    else:
        median_val = (values_sorted[n // 2 - 1] + values_sorted[n // 2]) / 2

    # Min and Max
    min_val = values_sorted[0]
    max_val = values_sorted[-1]

    # Variance and standard deviation (sample variance, ddof=1)
    if n > 1:
        variance_val = sum((x - mean_val) ** 2 for x in values_sorted) / (n - 1)
        std_dev_val = math.sqrt(variance_val)
    else:
        variance_val = 0.0
        std_dev_val = 0.0

    # Quartiles using "inclusive" method
    # Q1 median of lower half, Q3 median of upper half
    lower_half = values_sorted[: n // 2]
    upper_half = values_sorted[(n + 1) // 2 :]

    if lower_half:
        q1_idx = (len(lower_half) - 1) / 2.0
        q1_val = (
            lower_half[int(math.floor(q1_idx))]
            + lower_half[int(math.ceil(q1_idx))]
        ) / 2
    else:
        q1_val = min_val

    if upper_half:
        q3_idx = (len(upper_half) - 1) / 2.0
        q3_val = (
            upper_half[int(math.floor(q3_idx))]
            + upper_half[int(math.ceil(q3_idx))]
        ) / 2
    else:
        q3_val = max_val

    # Percentiles using linear interpolation
    def percentile_index(p: float) -> float:
        """Calculate the index for a given percentile p (0-100)."""
        return (p / 100.0) * (n - 1)

    def linear_interpolate(sorted_vals: List[float], idx: float) -> float:
        """Linearly interpolate between two adjacent values."""
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return sorted_vals[lo]
        frac = idx - lo
        return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac

    p25_val = linear_interpolate(values_sorted, percentile_index(25))
    p75_val = linear_interpolate(values_sorted, percentile_index(75))

    return {
        "mean": mean_val,
        "median": median_val,
        "minimum": min_val,
        "maximum": max_val,
        "standard_deviation": std_dev_val,
        "variance": variance_val,
        "quartile_1": q1_val,
        "quartile_3": q3_val,
        "percentile_25": p25_val,
        "percentile_75": p75_val,
    }


def calculate_bankruptcy_metrics(
    simulations: List[Dict[str, Any]],
) -> Dict[str, float | int]:
    """Calculate bankruptcy-related metrics.

    Args:
        simulations: List of simulation result dictionaries.

    Returns:
        Dictionary with bankruptcy_rate, number_bankrupt, total_simulations.
    """
    total = len(simulations)

    if total == 0:
        return {
            "bankruptcy_rate": 0.0,
            "number_bankrupt": 0,
            "total_simulations": 0,
        }

    # Check if this uses the compact summary format (has bankruptcy_count)
    # or individual simulation format
    first = simulations[0]
    has_bankruptcy_count = "bankruptcy_count" in first

    if has_bankruptcy_count:
        # Compact format: sum up bankruptcy_counts
        bankrupt_count = sum(s.get("bankruptcy_count", 0) for s in simulations)
        # The summary already has a bankruptcy_rate; we can use it or recalculate
        # Recalculate from individual entries if available
        # If entries don't have final_balance, use the stored count
        bankrupt_simulations = bankrupt_count
    else:
        # Individual simulation format: check final_balance == 0
        bankrupt_simulations = sum(
            1 for s in simulations if s.get("final_balance", 0) == 0
        )

    bankruptcy_rate = bankrupt_simulations / total if total > 0 else 0.0

    return {
        "bankruptcy_rate": bankruptcy_rate,
        "number_bankrupt": bankrupt_simulations,
        "total_simulations": total,
    }


def calculate_profitability_metrics(
    simulations: List[Dict[str, Any]],
    starting_balance: float,
) -> Dict[str, float | int]:
    """Calculate profitability-related metrics.

    Precisely defined categories:
    - "profitable": final_balance > starting_balance
    - "break_even": final_balance == starting_balance
    - "loss": final_balance < starting_balance (and not bankrupt)
    - "bankrupt": simulation ended in bankruptcy (also counted as loss)

    Args:
        simulations: List of simulation result dictionaries.
        starting_balance: The starting balance for all simulations.

    Returns:
        Dictionary with profitable_rate, loss_rate, break_even_rate,
        number_profitable, number_losses, number_bankrupt.
    """
    total = len(simulations)
    if total == 0:
        return {
            "profitable_rate": 0.0,
            "loss_rate": 0.0,
            "break_even_rate": 0.0,
            "number_profitable": 0,
            "number_losses": 0,
            "number_bankrupt": 0,
        }

    profitable = 0
    loss_count = 0
    break_even_count = 0
    bankrupt_count = 0

    for sim in simulations:
        final_bal = sim.get("final_balance", 0)
        status = sim.get("status", "")

        # Bankrupt takes precedence in classification
        is_bankrupt_sim = final_bal == 0 or status == "BANKRUPT"

        if is_bankrupt_sim:
            bankrupt_count += 1
        elif final_bal > starting_balance:
            profitable += 1
        elif final_bal == starting_balance:
            break_even_count += 1
        else:
            # final_balance < starting_balance and not bankrupt
            loss_count += 1

    profitable_rate = profitable / total if total > 0 else 0.0
    loss_rate = loss_count / total if total > 0 else 0.0
    break_even_rate = break_even_count / total if total > 0 else 0.0
    bankruptcy_rate = bankrupt_count / total if total > 0 else 0.0

    return {
        "profitable_rate": profitable_rate,
        "loss_rate": loss_rate,
        "break_even_rate": break_even_rate,
        "bankruptcy_rate": bankruptcy_rate,
        "number_profitable": profitable,
        "number_losses": loss_count,
        "number_bankrupt": bankrupt_count,
    }


def analyze_scenario(
    simulations: List[Dict[str, Any]],
    starting_balance: float,
) -> Dict[str, Any]:
    """Analyze a single scenario's simulation results.

    Args:
        simulations: List of simulation result dictionaries from one scenario.
        starting_balance: The starting balance for that scenario.

    Returns:
        Dictionary with all calculated metrics grouped by category.
    """
    # Extract final balances
    final_balances = [s.get("final_balance", 0) for s in simulations]

    # Descriptive statistics
    desc = calculate_descriptive_statistics(final_balances)

    # Bankruptcy metrics
    bankruptcy = calculate_bankruptcy_metrics(simulations)

    # Profitability metrics
    profitability = calculate_profitability_metrics(simulations, starting_balance)

    # Survival/iterations analysis
    iterations = [s.get("total_iterations", 0) for s in simulations if s.get("total_iterations", 0) > 0]

    survival_metrics: Dict[str, float] = {
        "average_iterations_survived": (
            sum(iterations) / len(iterations) if iterations else 0.0
        ),
        "median_iterations_survived": (
            sorted(iterations)[len(iterations) // 2] if iterations else 0.0
        ),
    }

    return {
        "descriptive_statistics": desc,
        "bankruptcy_metrics": bankruptcy,
        "profitability_metrics": profitability,
        "survival_metrics": survival_metrics,
        "total_simulations": len(simulations),
        "starting_balance": starting_balance,
    }


def analyze_experiments(
    summaries_dir: str = "results/summaries",
    processed_dir: str = "data/processed",
) -> Dict[str, Any]:
    """Analyze all experiments in the summaries directory and generate comparison.

    Args:
        summaries_dir: Path to summaries directory.
        processed_dir: Path to directory for saving processed analysis.

    Returns:
        Dictionary with per-scenario analysis and cross-scenario comparison.
    """
    # Load all summaries
    all_summaries = load_result_summaries(summaries_dir)

    if not all_summaries:
        return {"error": "No summary files found."}

    # Group by scenario
    scenarios: Dict[str, List[Dict[str, Any]]] = {}
    for summary in all_summaries:
        scenario = summary.get("scenario")
        if scenario:
            if scenario not in scenarios:
                scenarios[scenario] = []
            scenarios[scenario].append(summary)

    # Analyze each scenario
    scenario_analyses: Dict[str, Dict[str, Any]] = {}
    for scenario_name, simulations in scenarios.items():
        # Get starting chips from configuration
        starting_chips = sum(
            s.get("configuration", {}).get("starting_chips", 0) for s in simulations
        ) / len(simulations) if simulations else 0

        analysis = analyze_scenario(simulations, starting_chips)
        analysis["starting_balance"] = starting_chips
        analysis["num_simulations"] = len(simulations)
        scenario_analyses[scenario_name] = analysis

    # Build cross-scenario comparison
    comparison: Dict[str, Any] = {
        "scenarios_compared": list(scenario_analyses.keys()),
        "bankruptcy_rates": {
            name: analysis["bankruptcy_metrics"]["bankruptcy_rate"]
            for name, analysis in scenario_analyses.items()
        },
        "profitable_rates": {
            name: analysis["profitability_metrics"]["profitable_rate"]
            for name, analysis in scenario_analyses.items()
        },
        "loss_rates": {
            name: (
                1.0
                - analysis["profitability_metrics"]["profitable_rate"]
                - analysis["bankruptcy_metrics"]["bankruptcy_rate"]
            )
            for name, analysis in scenario_analyses.items()
        },
        "average_final_balances": {
            name: analysis["descriptive_statistics"]["mean"]
            for name, analysis in scenario_analyses.items()
        },
        "median_final_balances": {
            name: analysis["descriptive_statistics"]["median"]
            for name, analysis in scenario_analyses.items()
        },
        "average_iterations_survived": {
            name: analysis["survival_metrics"]["average_iterations_survived"]
            for name, analysis in scenario_analyses.items()
        },
    }

    # Save processed analysis
    processed_path = Path(processed_dir)
    processed_path.mkdir(parents=True, exist_ok=True)

    # Save scenario analyses
    for scenario_name, analysis in scenario_analyses.items():
        safe_name = scenario_name.replace(" ", "_").replace("/", "_")
        analysis_path = processed_path / f"{safe_name}_analysis.json"
        with open(analysis_path, "w") as f:
            json.dump(analysis, f, indent=2)

    # Save comparison table
    comparison_path = processed_path / "cross_scenario_comparison.json"
    with open(comparison_path, "w") as f:
        json.dump(comparison, f, indent=2)

    # Save combined results
    combined_path = processed_path / "analysis_summary.json"
    combined = {
        "scenario_analyses": scenario_analyses,
        "comparison": comparison,
    }
    with open(combined_path, "w") as f:
        json.dump(combined, f, indent=2)

    return combined


def run_analysis(
    summaries_dir: str = "results/summaries",
    processed_dir: str = "data/processed",
) -> Dict[str, Any]:
    """Run the full analysis pipeline.

    Convenience function that loads summaries, analyzes each scenario,
    and generates comparison tables.

    Args:
        summaries_dir: Path to summaries directory.
        processed_dir: Path to directory for saved processed analysis.

    Returns:
        Dictionary with all analysis results.
    """
    return analyze_experiments(summaries_dir, processed_dir)