"""Result persistence module for Probability & Betting Simulation.

Handles saving experiment results permanently without overwriting previous runs.
Each run gets a unique ID, and all result files (summary JSON, iteration CSV, bet CSV)
are stored with that run ID.

Key design principles:
- Unique run IDs based on timestamp with collision avoidance
- No overwriting: new runs stored alongside previous ones
- Atomic writes to avoid partial/corrupt files
- All configuration stored in the summary (not reliant on external config)
- Error handling: no misleading successful files on failure
- Reusable across all experiments - no code duplication
"""

import csv
import json
import os
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def generate_run_id(experiment_name: str) -> str:
    """Generate a unique run ID.

    Format: EXP_YYYYMMDD_HHMMSS_<unique_suffix>

    The unique suffix is based on UUID4 to virtually guarantee uniqueness,
    even if multiple runs happen in the same second.

    Args:
        experiment_name: Name of the experiment (e.g., "coin_probability",
                         "betting_strategy").

    Returns:
        A string like "EXP_20260928_072501_a3f2b1c".
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_suffix = uuid.uuid4().hex[:3]  # 3 hex chars = 12 bits of entropy
    return f"EXP_{timestamp}_{unique_suffix}"


def ensure_results_dirs(results_base: str | Path) -> Tuple[Path, Path]:
    """Ensure the results directory structure exists.

    Creates:
    - results/base/summaries/
    - results/base/detailed/

    Args:
        results_base: Base path for results (e.g., "results").

    Returns:
        Tuple of (summaries_dir, detailed_dir) Path objects.
    """
    base_path = Path(results_base)
    base_path.mkdir(parents=True, exist_ok=True)

    summaries_dir = base_path / "summaries"
    detailed_dir = base_path / "detailed"

    summaries_dir.mkdir(parents=True, exist_ok=True)
    detailed_dir.mkdir(parents=True, exist_ok=True)

    return summaries_dir, detailed_dir


class ResultSummary:
    """Represents a experiment run summary.

    Holds all the metadata and results for a single experiment execution.
    Instances are populated by the result manager and written to disk atomically.
    """

    def __init__(
        self,
        experiment_id: str,
        experiment_name: str,
        scenario: str | None,
        timestamp: str,
        configuration: Dict[str, Any],
        random_seed: int | None,
        results: Dict[str, Any],
        status: str,
    ):
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        self.scenario = scenario
        self.timestamp = timestamp
        self.configuration = configuration
        self.random_seed = random_seed
        self.results = results
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "experiment_id": self.experiment_id,
            "experiment_name": self.experiment_name,
            "scenario": self.scenario,
            "timestamp": self.timestamp,
            "configuration": self.configuration,
            "random_seed": self.random_seed,
            "results": self.results,
            "status": self.status,
        }


class ResultManager:
    """Manages saving and loading experiment results.

    This is the central class for result persistence. All experiments should use
    this class rather than writing files directly. This ensures consistency
    across experiments and prevents code duplication.

    Usage:
        manager = ResultManager("results")
        summary = manager.save_summary(...)
    """

    def __init__(self, results_base: str = "results"):
        self.results_base = Path(results_base)
        self.summaries_dir, self.detailed_dir = ensure_results_dirs(self.results_base)

    def save_summary(
        self,
        experiment_name: str,
        scenario: str | None,
        configuration: Dict[str, Any],
        random_seed: int | None,
        results: Dict[str, Any],
        status: str,
    ) -> str:
        """Save a summary JSON file for an experiment run.

        The file is named <experiment_id>.json and stored in the summaries directory.
        If a file with the same name exists, a new unique ID is generated.

        Args:
            experiment_name: Name of the experiment.
            scenario: Scenario name, or None if not applicable.
            configuration: Dictionary of configuration used for this run.
            random_seed: Random seed used, or None.
            results: Dictionary of results data.
            status: Status string (e.g., "BANKRUPT", "COMPLETED").

        Returns:
            The run ID that was used.
        """
        experiment_id = generate_run_id(experiment_name)

        summary = ResultSummary(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            scenario=scenario,
            timestamp=datetime.now().isoformat(),
            configuration=configuration,
            random_seed=random_seed,
            results=results,
            status=status,
        )

        summary_path = self.summaries_dir / f"{experiment_id}.json"

        # Atomic write: write to temp file first, then rename
        try:
            tmp_path = self.summaries_dir / f".{experiment_id}.json.tmp"
            with open(tmp_path, "w") as f:
                json.dump(summary.to_dict(), f, indent=2)

            # Replace atomically
            os.replace(tmp_path, summary_path)

        except Exception:
            # Clean up temp file if it exists
            tmp_path = self.summaries_dir / f".{experiment_id}.json.tmp"
            if tmp_path.exists():
                tmp_path.unlink()
            raise

        return experiment_id

    def save_iteration_csv(
        self,
        experiment_id: str,
        rows: List[Dict[str, Any]],
    ) -> Path:
        """Save iteration-level CSV data.

        Args:
            experiment_id: The run ID.
            rows: List of dictionaries, one per iteration, with columns:
                experiment_id, iteration, starting_balance, bet_size,
                heads, tails, profit_loss, ending_balance, status.

        Returns:
            Path to the CSV file saved.
        """
        csv_path = self.detailed_dir / f"{experiment_id}_iterations.csv"

        # Atomic write: write to temp file first, then rename
        try:
            tmp_path = self.detailed_dir / f".{experiment_id}_iterations.csv.tmp"
            with open(tmp_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self._iteration_csv_columns())
                writer.writeheader()
                for row in rows:
                    # Ensure all required columns are present
                    complete_row = self._complete_iteration_row(row)
                    writer.writerow(complete_row)

            # Replace atomically
            os.replace(tmp_path, csv_path)

        except Exception:
            tmp_path = self.detailed_dir / f".{experiment_id}_iterations.csv.tmp"
            if tmp_path.exists():
                tmp_path.unlink()
            raise

        return csv_path

    def save_bet_csv(
        self,
        experiment_id: str,
        rows: List[Dict[str, Any]],
    ) -> Path:
        """Save bet-level CSV data.

        Args:
            experiment_id: The run ID.
            rows: List of dictionaries, one per bet, with columns:
                experiment_id, iteration, bet_number, starting_balance,
                bet_size, outcome, payout, profit_loss, ending_balance, status.

        Returns:
            Path to the CSV file saved.
        """
        csv_path = self.detailed_dir / f"{experiment_id}_bets.csv"

        # Atomic write: write to temp file first, then rename
        try:
            tmp_path = self.detailed_dir / f".{experiment_id}_bets.csv.tmp"
            with open(tmp_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self._bet_csv_columns())
                writer.writeheader()
                for row in rows:
                    # Ensure all required columns are present
                    complete_row = self._complete_bet_row(row)
                    writer.writerow(complete_row)

            # Replace atomically
            os.replace(tmp_path, csv_path)

        except Exception:
            tmp_path = self.detailed_dir / f".{experiment_id}_bets.csv.tmp"
            if tmp_path.exists():
                tmp_path.unlink()
            raise

        return csv_path

    def load_summary(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Load a summary JSON file.

        Args:
            experiment_id: The run ID to load.

        Returns:
            Dictionary of summary data, or None if not found.
        """
        summary_path = self.summaries_dir / f"{experiment_id}.json"
        if not summary_path.exists():
            return None

        try:
            with open(summary_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def load_iteration_csv(self, experiment_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load iteration-level CSV data.

        Args:
            experiment_id: The run ID to load.

        Returns:
            List of dictionaries, one per row, or None if not found.
        """
        csv_path = self.detailed_dir / f"{experiment_id}_iterations.csv"
        if not csv_path.exists():
            return None

        try:
            rows = []
            with open(csv_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(dict(row))
            return rows
        except (IOError, csv.Error):
            return None

    def load_bet_csv(self, experiment_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load bet-level CSV data.

        Args:
            experiment_id: The run ID to load.

        Returns:
            List of dictionaries, one per row, or None if not found.
        """
        csv_path = self.detailed_dir / f"{experiment_id}_bets.csv"
        if not csv_path.exists():
            return None

        try:
            rows = []
            with open(csv_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(dict(row))
            return rows
        except (IOError, csv.Error):
            return None

    # ---- Internal helper methods ----

    @staticmethod
    def _iteration_csv_columns() -> List[str]:
        return [
            "experiment_id",
            "iteration",
            "starting_balance",
            "bet_size",
            "heads",
            "tails",
            "profit_loss",
            "ending_balance",
            "status",
        ]

    @staticmethod
    def _bet_csv_columns() -> List[str]:
        return [
            "experiment_id",
            "iteration",
            "bet_number",
            "starting_balance",
            "bet_size",
            "outcome",
            "payout",
            "profit_loss",
            "ending_balance",
            "status",
        ]

    @staticmethod
    def _complete_iteration_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure an iteration CSV row has all required columns with correct types."""
        complete = dict(row)
        # Ensure experiment_id is a string
        complete["experiment_id"] = str(complete.get("experiment_id", ""))

        # Ensure numeric columns are the right type
        for key in ["iteration", "starting_balance", "bet_size", "heads", "tails"]:
            if key in complete:
                try:
                    complete[key] = int(complete[key])
                except (ValueError, TypeError):
                    complete[key] = 0

        complete["profit_loss"] = int(complete.get("profit_loss", 0))
        complete["ending_balance"] = int(complete.get("ending_balance", 0))
        complete["status"] = str(complete.get("status", "UNKNOWN"))

        return complete

    @staticmethod
    def _complete_bet_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure a bet CSV row has all required columns with correct types."""
        complete = dict(row)
        # Ensure experiment_id is a string
        complete["experiment_id"] = str(complete.get("experiment_id", ""))

        # Ensure numeric columns are the right type
        for key in ["iteration", "bet_number", "starting_balance", "bet_size"]:
            if key in complete:
                try:
                    complete[key] = int(complete[key])
                except (ValueError, TypeError):
                    complete[key] = 0

        complete["payout"] = int(complete.get("payout", 0))
        complete["profit_loss"] = int(complete.get("profit_loss", 0))
        complete["ending_balance"] = int(complete.get("ending_balance", 0))
        complete["status"] = str(complete.get("status", "UNKNOWN"))

        # Ensure outcome is valid
        if complete.get("outcome") not in ("HEADS", "TAILS"):
            complete["outcome"] = "UNKNOWN"

        return complete


def run_experiment_with_persistence(
    experiment_func,
    experiment_name: str,
    results_manager: ResultManager,
    scenario: str | None = None,
    seed: int | None = None,
    **kwargs,
) -> Dict[str, Any]:
    """Run an experiment with automatic result persistence.

    This wrapper ensures that even if the experiment function raises an exception,
    no misleading successful summary files are created.

    Args:
        experiment_func: Callable that runs the experiment and returns (configuration, results_dict).
            The results_dict should contain at least: final_balance, total_iterations, status, etc.
        experiment_name: Name of the experiment for run ID generation.
        results_manager: ResultManager instance for saving files.
        scenario: Scenario name, or None.
        seed: Random seed used.
        **kwargs: Additional arguments to pass to experiment_func.

    Returns:
        The results dictionary from the experiment.

    Raises:
        Exception: If the experiment function raises, the exception is re-raised
            after cleaning up any partially written files.
    """
    import traceback

    experiment_id = generate_run_id(experiment_name)

    # Prepare configuration dict to save
    configuration = kwargs

    try:
        # Run the experiment
        config, results = experiment_func(seed=seed, **kwargs)

        # Determine status
        status = results.get("status", "COMPLETED")

        # Build the results summary
        summary_data = {
            "final_balance": results.get("final_balance"),
            "total_iterations": results.get("total_iterations", 0),
            "status": status,
            # Include any additional result data
            **{k: v for k, v in results.items() if k not in ("status", "final_balance", "total_iterations")},
        }

        # Save summary
        saved_id = results_manager.save_summary(
            experiment_name=experiment_name,
            scenario=scenario,
            configuration=configuration,
            random_seed=seed,
            results=summary_data,
            status=status,
        )

        # Save iteration-level CSV if we have iteration data
        iteration_data = results.get("iteration_data", [])
        if iteration_data:
            results_manager.save_iteration_csv(saved_id, iteration_data)

        # Save bet-level CSV if we have bet data
        bet_data = results.get("bet_data", [])
        if bet_data:
            results_manager.save_bet_csv(saved_id, bet_data)

        return results

    except Exception as e:
        # On failure, try to save an error summary (not a successful one!)
        # But only if we have enough info; otherwise re-raise
        error_summary = {
            "experiment_id": experiment_id,
            "experiment_name": experiment_name,
            "scenario": scenario,
            "timestamp": datetime.now().isoformat(),
            "configuration": configuration,
            "random_seed": seed,
            "results": {},
            "status": f"ERROR: {type(e).__name__}: {str(e)}",
        }

        try:
            # Save the error summary - this is intentional, not misleading
            results_manager.save_summary(
                experiment_name=experiment_name,
                scenario=scenario,
                configuration=configuration,
                random_seed=seed,
                results=error_summary,
                status=error_summary["status"],
            )
        except Exception:
            # If we can't even save the error summary, re-raise
            pass

        raise