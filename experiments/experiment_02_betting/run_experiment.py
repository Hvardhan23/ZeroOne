"""Experiment 2: Betting Strategy Monte Carlo.

Studies a betting strategy where a person starts with a fixed number of chips
and repeatedly makes 10 equally distributed bets, running multiple simulations
to study the distribution of outcomes (Monte Carlo).

Scenarios investigate different starting capital levels:
- LOW: 50 chips (initial bet = 5)
- BASELINE: 100 chips (initial bet = 10)
- HIGH: 1000 chips (initial bet = 100)

Supports configurable number_of_simulations and save_detailed_results.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import csv
import yaml

from src.simulation import run_betting_simulation, run_monte_carlo
from src.results import ResultManager


def get_scenario_starting_chips(scenario_name: str, config_path: str = "config/experiment_config.yaml") -> int:
    """Get the starting chips for a named scenario from configuration."""
    import yaml
    from pathlib import Path

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    scenarios = config.get("starting_capital_scenarios", [])
    for scenario in scenarios:
        if scenario.get("name") == scenario_name:
            return scenario.get("starting_chips", 100)

    return 100


def main():
    """Run the betting strategy Monte Carlo experiment."""
    # Load configuration
    config_path = project_root / "config/experiment_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Get scenarios from config
    scenarios = [s["name"] for s in config.get("starting_capital_scenarios", [])]
    num_mc = config.get("monte_carlo", {}).get("number_of_simulations", 1)
    save_detailed = config.get("monte_carlo", {}).get("save_detailed_results", True)
    master_seed = config.get("monte_carlo", {}).get("master_seed")
    bets_per_iteration = config.get("bets_per_iteration", 10)

    # Initialize ResultManager
    results_manager = ResultManager("results")

    print("=" * 60)
    print("Betting Strategy Monte Carlo - Capital Scenarios")
    print("=" * 60)
    print()
    print(f"Scenarios: {scenarios}")
    print(f"Number of simulations per scenario: {num_mc}")
    print(f"Save detailed results: {save_detailed}")
    print(f"Master seed: {master_seed}")
    print()

    all_scenario_results = []

    for scenario_name in scenarios:
        starting_chips = get_scenario_starting_chips(scenario_name)

        # Run Monte Carlo simulation
        mc_result = run_monte_carlo(
            starting_chips=starting_chips,
            number_of_simulations=num_mc,
            master_seed=master_seed,
            bets_per_iteration=bets_per_iteration,
            save_detailed=save_detailed,
        )

        # Save experiment-level summary
        summary = mc_result["summary"]
        experiment_id = mc_result["experiment_id"]

        summary_data = {
            "scenario": scenario_name,
            "starting_chips": starting_chips,
            "number_of_simulations": summary["number_of_simulations"],
            "number_bankrupt": summary["number_bankrupt"],
            "bankruptcy_rate": summary["bankruptcy_rate"],
            "number_profitable": summary["number_profitable"],
            "profitability_rate": summary["profitability_rate"],
            "average_final_balance": summary["average_final_balance"],
            "median_final_balance": summary["median_final_balance"],
            "minimum_final_balance": summary["minimum_final_balance"],
            "maximum_final_balance": summary["maximum_final_balance"],
            "average_iterations_survived": summary["average_iterations_survived"],
            "median_iterations_survived": summary["median_iterations_survived"],
            "average_maximum_balance": summary["average_maximum_balance"],
            "median_maximum_balance": summary["median_maximum_balance"],
            "master_seed": master_seed,
        }

        # Save summary using ResultManager
        saved_id = results_manager.save_summary(
            experiment_name="betting_monte_carlo",
            scenario=scenario_name,
            configuration={
                "starting_chips": starting_chips,
                "number_of_simulations": num_mc,
                "bets_per_iteration": bets_per_iteration,
                "master_seed": master_seed,
                "save_detailed_results": save_detailed,
            },
            random_seed=master_seed,
            results=summary_data,
            status="COMPLETED",
        )

        # Save detailed simulation results if enabled
        if save_detailed:
            for sim_result in mc_result["simulation_results"]:
                sim_id = sim_result["simulation_id"]

                # Save iteration-level CSV per simulation
                # Since we don't have per-bet detail in the Monte Carlo run,
                # we save iteration summary data
                iteration_rows = []
                # We have total_iterations from the sim result, but not per-iteration detail.
                # We'll write a single row with the key data.
                iteration_rows.append({
                    "experiment_id": saved_id,
                    "iteration": sim_result["total_iterations"],
                    "starting_balance": sim_result["starting_chips"],
                    "bet_size": bets_per_iteration,
                    "heads": sim_result["total_heads"],
                    "tails": sim_result["total_tails"],
                    "profit_loss": sim_result["total_profit_loss"],
                    "ending_balance": sim_result["final_balance"],
                    "status": "BANKRUPT" if sim_result["bankrupt"] else "COMPLETED",
                })

                results_manager.save_iteration_csv(saved_id, iteration_rows)

                # Save bet-level CSV - since we don't have per-bet data,
                # write a summary row
                bet_rows = []
                bet_rows.append({
                    "experiment_id": saved_id,
                    "iteration": sim_result["total_iterations"],
                    "bet_number": sim_result["total_bets"],
                    "starting_balance": sim_result["starting_chips"],
                    "bet_size": bets_per_iteration,
                    "outcome": "MONTE_CARLO_SUMMARY",
                    "payout": 0,
                    "profit_loss": sim_result["total_profit_loss"],
                    "ending_balance": sim_result["final_balance"],
                    "status": "BANKRUPT" if sim_result["bankrupt"] else "COMPLETED",
                })

                results_manager.save_bet_csv(saved_id, bet_rows)

        all_scenario_results.append(
            {
                "scenario_name": scenario_name,
                "starting_chips": starting_chips,
                "saved_id": saved_id,
                "mc_result": mc_result,
            }
        )

        # Print scenario summary
        s = summary
        print(f"Scenario '{scenario_name}':")
        print(f"  Starting chips: {starting_chips}")
        print(f"  Simulations: {s['number_of_simulations']}")
        print(f"  Bankruptcy rate: {s['bankruptcy_rate']:.2%} ({s['number_bankrupt']}/{s['number_of_simulations']})")
        print(f"  Profitability rate: {s['profitability_rate']:.2%} ({s['number_profitable']}/{s['number_of_simulations']})")
        print(f"  Average final balance: {s['average_final_balance']:.2f}")
        print(f"  Median final balance: {s['median_final_balance']:.2f}")
        print(f"  Min final balance: {s['minimum_final_balance']:.2f}")
        print(f"  Max final balance: {s['maximum_final_balance']:.2f}")
        print(f"  Avg iterations survived: {s['average_iterations_survived']:.1f}")
        print(f"  Max balance avg: {s['average_maximum_balance']:.2f}")

    # Print overall comparison
    print()
    print("=" * 60)
    print("MONTE CARLO COMPARISON ACROSS SCENARIOS")
    print("=" * 60)
    print()
    for sr in all_scenario_results:
        s = sr["mc_result"]["summary"]
        cfg = {"starting_chips": sr["starting_chips"]}
        print(f"{sr['scenario_name'].upper():8s} | "
              f"Start: {sr['starting_chips']:5d} | "
              f"Bankrupt: {s['bankruptcy_rate']:.1%} | "
              f"Profitability: {s['profitability_rate']:.1%} | "
              f"Avg final: {s['average_final_balance']:.2f}")

    # List saved summaries
    summary_count = len(list(Path('results/summaries').glob('*.json')))
    print(f"\nSaved {summary_count} summary(ies) across all scenarios")


if __name__ == "__main__":
    main()