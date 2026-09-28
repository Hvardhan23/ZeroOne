"""Professional visualization module for the Probability & Betting Simulation project.

Creates publication-quality charts visualizing simulation results.

Note: matplotlib must be installed (pip install matplotlib) for charts to render.
If seaborn is available, charts use a style compatible with it.

CHARTS:
1. balance_vs_iteration - Single simulation balance over time
2. multiple_balance_paths - Multiple simulation paths
3. final_balance_distribution - Histogram of final balances
4. bankruptcy_rate_by_capital - Comparative bar chart
5. profit_loss_distribution - Outcome distribution pie chart
6. survival_curves - Iterations before bankruptcy
7. maximum_balance_distribution - Peak balance distribution
8. observed_probability_vs_theoretical - Law of Large Numbers demo
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

HAS_MATPLOTLIB = False
HAS_SEABORN = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.style as mpl_style
    try:
        import seaborn as sns
        mpl_style.use('seaborn-v0_8')
        HAS_SEABORN = True
    except ImportError:
        pass
    HAS_MATPLOTLIB = True
except ImportError:
    pass


def _get_figures_dir():
    """Get the figures directory, creating it if needed."""
    project_figures = Path("results/figures")
    project_figures.mkdir(parents=True, exist_ok=True)
    return project_figures


def _create_figure(figsize=(8, 6)):
    if HAS_MATPLOTLIB:
        import matplotlib.pyplot as plt
        return plt.subplots(figsize=figsize)
    class _StubAxes:
        def plot(self, *a, **k): pass
        def set_xlabel(self, *a, **k): pass
        def set_ylabel(self, *a, **k): pass
        def set_title(self, *a, **k): pass
        def legend(self, *a, **k): pass
        def grid(self, *a, **k): pass
        def set_ylim(self, *a, **k): pass
        def set_xlim(self, *a, **k): pass
        def axhline(self, *a, **k): pass
        def axvline(self, *a, **k): pass
        def bar(self, *a, **k):
            class _Bar:
                def get_x(self): return 0
                def get_width(self): return 0.8
                def get_height(self): return 1.0
            # Return one bar per data point; default to 1 if can't determine
            n = 1
            if a and len(a) > 0:
                try:
                    n = max(len(a[0]), 1)
                except Exception:
                    pass
            return [_Bar() for _ in range(n)]
        def text(self, *a, **k): pass
        def pie(self, *a, **k): pass
        def hist(self, *a, **k): pass
    class _StubFigure:
        def __init__(self):
            self._axes = _StubAxes()
        @property
        def gca(self):
            return self._axes
        def savefig(self, *a, **k): pass
        def close(self): pass
    return None, _StubAxes()


def _save_figure(fig, experiment_id, filename, figures_dir):
    safe_name = f"{experiment_id}_{filename}" if experiment_id else filename
    safe_name = safe_name.replace(" ", "_")
    fp = Path(figures_dir) / safe_name
    if fp.exists():
        import time
        ts = int(time.time())
        base, ext = os.path.splitext(safe_name)
        fp = Path(figures_dir) / f"{base}_{ts}{ext}"
    if HAS_MATPLOTLIB:
        fig.savefig(str(fp), dpi=150, bbox_inches="tight")
    return fp


def balance_vs_iteration(balance_history, starting_balance, experiment_id="", title_suffix=""):
    """Plot single simulation balance over iteration time.
    X: Iteration, Y: Balance (chips), includes starting balance reference."""
    fig, ax = _create_figure((10, 6))
    it = list(range(1, len(balance_history) + 1))
    ax.plot(it, balance_history, "b-", linewidth=2, label="Balance")
    ax.axhline(y=starting_balance, color="r", linestyle="--", linewidth=2,
               label=f"Starting Balance ({starting_balance} chips)")
    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Balance (chips)", fontsize=12)
    title = f"Balance vs Iteration{title_suffix}"
    if experiment_id:
        title += f" (Run: {experiment_id})"
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    return _save_figure(fig, experiment_id, "balance_vs_iteration.png", _get_figures_dir())


def multiple_balance_paths(balance_histories, starting_balance, labels=None, experiment_id="", title_suffix=""):
    """Plot multiple simulation paths showing different random sequences."""
    fig, ax = _create_figure((10, 6))
    if labels is None:
        labels = [f"Path {i+1}" for i in range(len(balance_histories))]
    for i, history in enumerate(balance_histories):
        it = list(range(1, len(history) + 1))
        ax.plot(it, history, linewidth=1.5, label=labels[i])
    ax.axhline(y=starting_balance, color="gray", linestyle=":", linewidth=2,
               label=f"Starting Balance ({starting_balance} chips)")
    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Balance (chips)", fontsize=12)
    title = "Multiple Balance Paths" + (f" {title_suffix}" if title_suffix else "")
    if experiment_id:
        title += f" (Run: {experiment_id})"
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10, loc="best")
    ax.grid(True, alpha=0.3)
    return _save_figure(fig, experiment_id, "multiple_balance_paths.png", _get_figures_dir())


def final_balance_distribution(final_balances, starting_balance, experiment_id="", title_suffix=""):
    """Histogram of final balances with starting balance reference line."""
    fig, ax = _create_figure((10, 6))
    ax.hist(final_balances, bins="auto", color="steelblue", edgecolor="white", alpha=0.8,
            label="Final Balance")
    ax.axvline(x=starting_balance, color="red", linestyle="--", linewidth=2,
               label=f"Starting Balance ({starting_balance} chips)")
    ax.axvline(x=0, color="black", linestyle=":", linewidth=2,
               label="Bankruptcy (0 chips)")
    ax.set_xlabel("Final Balance (chips)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    title = f"Final Balance Distribution{title_suffix}"
    if experiment_id:
        title += f" (Run: {experiment_id})"
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    return _save_figure(fig, experiment_id, "final_balance_distribution.png", _get_figures_dir())


def bankruptcy_rate_by_capital(capital_data, title_suffix=""):
    """Comparative bar chart of bankruptcy rates across starting capitals."""
    fig, ax = _create_figure((10, 6))
    capitals = list(capital_data.keys())
    rates = list(capital_data.values())
    bars = ax.bar(capitals, rates, color="salmon", alpha=0.8, edgecolor="darkred")
    ax.set_ylim(0, 1.1)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{rate:.1%}", ha="center", fontsize=12)
    ax.set_ylabel("Bankruptcy Rate", fontsize=12)
    ax.set_title(f"Bankruptcy Rate by Starting Capital{title_suffix}", fontsize=14)
    ax.grid(True, alpha=0.3, axis="y")
    return _save_figure(fig, "", "bankruptcy_rate_by_capital.png", _get_figures_dir())


def profit_loss_distribution(outcome_counts, title_suffix=""):
    """Pie chart of profit/loss/break_even/bankrupt distribution."""
    fig, ax = _create_figure((10, 6))
    outcomes = ["profit", "break_even", "loss", "bankrupt"]
    counts = [outcome_counts.get(k, 0) for k in outcomes]
    visible_labels = []
    visible_counts = []
    for k, c in zip(outcomes, counts):
        if c > 0:
            visible_labels.append(k)
            visible_counts.append(c)
    if HAS_SEABORN:
        import seaborn as sns
        colors = sns.color_palette("pastel")[len(visible_labels):len(visible_labels)+1]
    else:
        colors = ["#4CAF50", "#FFC107", "#F44336", "#9E9E9E"][:len(visible_labels)]
    ax.pie(visible_counts, labels=visible_labels,
           autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
           colors=colors, startangle=90, textprops={"fontsize": 11})
    ax.set_title(f"Profit/Loss/Break-even Distribution{title_suffix}", fontsize=14)
    return _save_figure(fig, "", "profit_loss_distribution.png", _get_figures_dir())


def survival_curves(iteration_data, experiment_id="", title_suffix=""):
    """Plot how long simulations survive before bankruptcy."""
    fig, ax = _create_figure((10, 6))
    max_it = max(iteration_data) if iteration_data else 1
    surv = [sum(1 for it in iteration_data if it >= i) for i in range(1, max_it + 1)]
    iters = list(range(1, max_it + 1))
    ax.plot(iters, surv, "b-", linewidth=2, label="Surviving Simulations")
    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Number of Surviving Simulations", fontsize=12)
    title = "Survival Curves: Iterations Before Bankruptcy"
    if title_suffix:
        title += f" {title_suffix}"
    if experiment_id:
        title += f" (Run: {experiment_id})"
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    median_s = int(max(iteration_data)) if iteration_data else 0
    ax.axvline(x=median_s, color="red", linestyle="--", linewidth=2,
               label=f"Median: {median_s} iterations")
    ax.legend(fontsize=10)
    return _save_figure(fig, experiment_id, "survival_curves.png", _get_figures_dir())


def maximum_balance_distribution(max_balances, starting_balance, experiment_id="", title_suffix=""):
    """Histogram of maximum balance reached during simulations."""
    fig, ax = _create_figure((10, 6))
    ax.hist(max_balances, bins="auto", color="green", edgecolor="white", alpha=0.8,
            label="Maximum Balance")
    ax.axvline(x=starting_balance, color="red", linestyle="--", linewidth=2,
               label=f"Starting Balance ({starting_balance} chips)")
    ax.set_xlabel("Maximum Balance Reached (chips)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    title = f"Maximum Balance Distribution{title_suffix}"
    if experiment_id:
        title += f" (Run: {experiment_id})"
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    return _save_figure(fig, experiment_id, "maximum_balance_distribution.png", _get_figures_dir())


def observed_probability_vs_theoretical(flip_counts, observed_probs, theoretical_prob=0.5,
                                        experiment_id="", title_suffix=""):
    """Law of Large Numbers: observed Heads probability vs. theoretical 50%."""
    fig, ax = _create_figure((10, 6))
    ax.plot(flip_counts, observed_probs, "bo-", linewidth=2, markersize=8,
            label="Observed Heads Probability")
    ax.axhline(y=theoretical_prob, color="red", linestyle="--", linewidth=2,
               label=f"Theoretical Probability ({theoretical_prob:.0%})")
    ax.set_xlabel("Number of Flips", fontsize=12)
    ax.set_ylabel("Heads Probability", fontsize=12)
    title = "Observed Probability vs. Number of Flips"
    if title_suffix:
        title += f" {title_suffix}"
    if experiment_id:
        title += f" (Run: {experiment_id})"
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=1)
    return _save_figure(fig, experiment_id, "observed_probability_vs_flips.png", _get_figures_dir())
