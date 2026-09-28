# Probability & Betting Simulation

A project studying probability, repeated betting, bankroll growth/decline, and the probability of losing all available capital through computational experiments.

---

## 1. Project Overview

This project uses computational simulations to study probability and betting mechanics. It is not gambling advice or financial advice — it is a research tool for understanding stochastic processes.

The project consists of two main experiment types:

**Experiment 1: Coin Flip Probability**
- Studies the observed probability of Heads vs. Tails via repeated coin flips
- Demonstrates the Law of Large Numbers: as the number of flips increases, observed probability converges toward the theoretical 50/50 distribution
- Tests probability calculations and statistical behavior

**Experiment 2: Repeated Betting Simulation**
- Studies a betting strategy where a player starts with a fixed number of chips and makes 10 equally distributed bets per iteration
- Bet size is determined as floor(balance / 10) at the start of each iteration
- Heads: win, payout = 2× bet, net profit = +bet
- Tails: loss, payout = 0, net profit = -bet
- Bankruptcy occurs when floor(balance / 10) < 1 (i.e., the player cannot place the minimum 1-chip bet)
- Three starting capital scenarios: 50 chips (low), 100 chips (baseline), 1000 chips (high)
- Monte Carlo simulation runs multiple independent simulations to assess outcome distributions

Key design principles:
- Integer-chip arithmetic — no floating point
- One iteration = exactly 10 bets with fixed bet size
- Bet size recalculated after each iteration based on new balance
- Results are deterministic given the same random seed

---

## 2. Research Questions

The project aims to computationally explore:

1. **How quickly does observed coin probability approach the theoretical 50/50 probability as sample size increases?**
   - Tests the Law of Large Numbers with flip counts of 100, 1000, 10000, 100000, 1000000

2. **How does repeated betting affect bankroll under the defined strategy?**
   - Simulates bankroll changes over multiple iterations until bankruptcy
   - Tracks final balance, profit/loss, and survival time

3. **How frequently does simulated bankruptcy occur?**
   - Measures bankruptcy rates across different starting capital levels
   - With 50 chips: bankruptcy is very likely
   - With 1000 chips: bankruptcy is less likely

4. **How does starting capital affect observed outcomes?**
   - Compares low (50), baseline (100), and high (1000) scenarios
   - Larger starting capital generally leads to lower bankruptcy rates and longer survival

5. **How variable are the results across repeated simulations?**
   - Monte Carlo simulation provides distribution of outcomes
   - Even with the same starting capital, different random sequences produce different results
   - Summary statistics (bankruptcy rate, profitability rate, balance distributions) quantify this variability

---

## 3. Experiments

### Experiment 1: Coin Flip Probability

Studies the observed probability of Heads vs. Tails using repeated coin flips.

- **Configuration** (from `config/experiment_config.yaml`):
  - `coin_flips`: 100, 1000, 10000, 100000, 1000000 (flip counts to test)
  - `random_seed`: Optional seed for reproducibility
  - `number_of_simulations`: Number of independent simulations

- **Output**: Observed heads/tails probability, comparison to theoretical 0.5, Law of Large Numbers demonstration

### Experiment 2: Repeated Betting Simulation

Studies a betting strategy where a person starts with a fixed number of chips and repeatedly makes 10 equally distributed bets.

- **Starting capital scenarios**:
  - Low: 50 chips
  - Baseline: 100 chips
  - High: 1000 chips
- **Rules**:
  - 10 bets per iteration
  - Bet size = floor(balance / 10) at iteration start
  - All bets within an iteration use the same fixed bet size
  - After each iteration, bet size is recalculated based on the new balance
  - Bankruptcy: floor(balance / 10) < 1
  - Heads: payout = 2× bet, net profit = +bet
  - Tails: payout = 0, net profit = -bet

- **Output per scenario**:
  - Final balances across simulations
  - Bankruptcy counts and rates
  - Profit/loss distribution
  - Survival curves (iterations before bankruptcy)
  - Maximum balance reached during simulation

---

## 3. Methodology

### Betting Rules (Exact)

| Rule | Description |
|------|-------------|
| Starting balance | Fixed per scenario (50, 100, or 1000 chips) |
| Bets per iteration | Exactly 10 |
| Bet size | floor(balance / 10), determined at iteration start |
| Heads outcome | Payout = 2× bet, net profit = +bet (stake returned in payout) |
| Tails outcome | Payout = 0, net profit = -bet |
| Balance update | new_balance = balance + net_profit |
| Bankruptcy condition | floor(balance / 10) < 1 (cannot place minimum 1-chip bet) |
| Integer chips | All balances, bets, and profits are integers — no floating point |

### Monte Carlo Simulation

One random path is not sufficient to understand the distribution of outcomes. Monte Carlo simulation runs multiple independent simulations, each with its own random seed, to:

- Estimate the probability of different outcomes
- Quantify variability across simulations
- Calculate bankruptcy rates, profitability rates, and balance distributions
- Provide statistically meaningful results

Without multiple simulations, one cannot distinguish between "unusual but possible" and "highly likely" outcomes.

### Simulation Flow

1. Start with starting_chips
2. While not bankrupt (floor(balance/10) >= 1):
   a. Calculate bet_size = floor(balance / 10)
   b. Run 10 bets with fixed bet_size
   c. Update balance based on bet results
   d. Recalculate bet_size for next iteration
3. Record final balance, iterations survived, bankruptcy status

---

## 4. Scenarios

| Scenario | Starting Chips | Description |
|----------|---------------|-------------|
| Low | 50 | Small bankroll, high bankruptcy probability |
| Baseline | 100 | Medium bankroll, moderate bankruptcy probability |
| High | 1000 | Large bankroll, low bankruptcy probability |

All scenarios use the same betting rules (10 bets per iteration, bet size = floor(balance/10)).

---

## 5. Monte Carlo Simulation

### Why Repeated Simulations Are Necessity

A single simulation run is just one possible outcome sequence. The same starting conditions can lead to very different results depending on the random coin flips and bet outcomes that occur. Monte Carlo simulation addresses this by:

- Running 20+ independent simulations per scenario
- Each simulation uses an independent random seed
- Collecting aggregate statistics across all simulations
- Distinguishing between "possible" and "likely" outcomes

### Monte Carlo Configuration

- `number_of_simulations`: Number of independent simulations to run (default: 1 in config, typically 20+ for analysis)
- `master_seed`: Optional master seed for reproducibility. If supplied, child seeds are derived as master_seed + simulation_index, so rerunning produces the exact same results. If None, each simulation uses independent random seeds.
- `bets_per_iteration`: Number of bets per iteration (default: 10)
- `save_detailed`: If True, save per-simulation detail data. Set False for large experiments to reduce storage.

### Summary Statistics Calculated

- `bankruptcy_rate`: Fraction of simulations that went bankrupt
- `profitability_rate`: Fraction of simulations with positive final balance
- `average_final_balance`: Mean final balance across simulations
- `median_final_balance`: Median final balance
- `minimum_final_balance`: Minimum final balance reached
- `maximum_final_balance`: Maximum final balance reached
- `average_iterations_survived`: Mean iterations before bankruptcy
- `median_iterations_survived`: Median iterations before bankruptcy
- `average_maximum_balance`: Mean maximum balance reached
- `median_maximum_balance`: Median maximum balance reached

---

## 6. Reproducibility

### Random Seeds

- Providing a `seed` value ensures deterministic results: the same seed always produces the same output
- Without a seed, each run uses independent random values
- Seeds are used across all components: coin flips, betting outcomes, and Monte Carlo simulations

### Configuration Reproducibility

- All configuration is stored in `config/experiment_config.yaml`
- The config file documents all parameters: starting chips, bet counts, win multiplier, bankruptcy rules, coin flip counts, etc.
- Result summaries store the configuration used, enabling post-hoc analysis

### Run IDs

- Each experiment run gets a unique ID in the format `EXP_YYYYMMDD_HHMMSS_XXX`
  - `EXP`: Fixed prefix
  - `YYYYMMDD`: Date (year-month-day)
  - `HHMMSS`: Time (hour-minute-second)
  - `XXX`: 3-character UUID4 hex suffix (virtually guarantees uniqueness)
- Run IDs are stored in result summary files and used to name all associated output files (CSV, figures, etc.)
- No overwriting: new runs are stored alongside previous ones

---

## 7. Data Storage

Results are stored under `results/` with the following organization. **Note: The `results/` directory is gitignored and generated by running the experiments** (see the "Running Experiments" section for commands). This keeps the repository clean while still providing reproduction steps.

```wiki
results/
├── summaries/
│   └── EXP_*.json      # One per experiment run
│   └── analysis_summary.json    # Cross-scenario comparison
│   └── cross_scenario_comparison.json  # Bankruptcy/profitability rates comparison
│   └── analysis_summary.json  # Combined analysis
│   └── *_analysis.json  # Per-scenario analysis
├── detailed/
│   └── EXP_*_iterations.csv  # Per-iteration data
│   └── EXP_*_bets.csv        # Per-bet data
│   └── SIM_*_details.json    # Per-simulation detail data
├── figures/
│   └── *.png               # Generated charts (8 types)
│   └── cross_scenario_comparison.json  # Analysis comparison data
└── processed/
    └── analysis_summary.json  # Processed analysis results
```

Results are stored under `results/` with the following organization:

```
results/
├── summaries/
│   └── EXP_*.json      # One per experiment run
│   └── analysis_summary.json    # Cross-scenario comparison
│   └── cross_scenario_comparison.json  # Bankruptcy/profitability rates comparison
│   └── analysis_summary.json  # Combined analysis
│   └── *_analysis.json  # Per-scenario analysis
├── detailed/
│   └── EXP_*_iterations.csv  # Per-iteration data
│   └── EXP_*_bets.csv        # Per-bet data
│   └── SIM_*_details.json    # Per-simulation detail data
├── figures/
│   └── *.png               # Generated charts (8 types)
│   └── cross_scenario_comparison.json  # Analysis comparison data
└── processed/
    └── analysis_summary.json  # Processed analysis results
```

### File Formats

**Summary JSON** (`EXP_*.json`):
- `experiment_id`: Unique run identifier
- `experiment_name`: "coin_probability" or "betting_strategy"
- `scenario`: Scenario name (for betting experiments) or null
- `timestamp`: ISO format timestamp
- `configuration`: Dictionary of parameters used
- `random_seed`: Seed used (or None)
- `results`: Experiment-specific result data
- `status`: "COMPLETED" or "ERROR"

**Iteration CSV** (`EXP_*_iterations.csv`):
- Columns: experiment_id, iteration, starting_balance, bet_size, heads, tails, profit_loss, ending_balance, status
- One row per iteration per simulation

**Bet-level CSV** (`EXP_*_bets.csv`):
- Columns: experiment_id, iteration, bet_number, starting_balance, bet_size, outcome, payout, profit_loss, ending_balance, status
- One row per individual bet

**Simulation-level detail** (`SIM_*_details.json`):
- Per-simulation data including: simulation_id, experiment_id, scenario, starting_chips, total_iterations, total_bets, total_heads, total_tails, final_balance, maximum_balance, minimum_balance, total_profit_loss, bankrupt, bankruptcy_iteration, random_seed

### Processed Analysis

After running analysis, processed data is saved to `data/processed/`:
- `*_analysis.json`: Per-scenario analysis with all metrics
- `cross_scenario_comparison.json`: Comparison table across scenarios
- `analysis_summary.json`: Combined results including scenario analyses and comparison

---

## 8. Repository Structure

```
probability-betting-simulation/
├── .gitignore
├── config/
│   └── experiment_config.yaml    # Central configuration
├── data/
│   ├── raw/                      # Raw data (if any)
│   ├── processed/                # Processed analysis results
│   └── results/                  # Simulation results (generated)
│       ├── summaries/            # JSON summaries
│       ├── detailed/             # CSV and JSON detail data
│       ├── figures/              # Generated charts
│       └── processed/            # Processed analysis outputs
├── notebooks/                    # Jupyter notebooks (if any)
├── requirements.txt              # Python dependencies
├── results/
│   ├── summaries/                # Experiment summary JSON files
│   ├── detailed/                 # CSV and JSON detail files
│   └── figures/                  # Generated chart images
├── src/
│   ├── __init__.py               # Package init, version 0.1.0
│   ├── coin.py                   # Coin flip logic (flip_coin, simulate_flips)
│   ├── betting.py                # Core betting engine
│   ├── simulation.py             # Monte Carlo and batch simulation
│   ├── results.py                # Result persistence and manager
│   ├── analysis.py               # Statistical analysis layer
│   ├── visualizations.py         # 8 chart types
│   └── utils.py                  # Utility functions (validation, etc.)
├── experiments/
│   ├── experiment_01_coin_probability/
│   │   └── run_experiment.py     # Experiment 1 runner
│   └── experiment_02_betting/
│       └── run_experiment.py     # Experiment 2 runner
├── tests/
│   ├── test_coin.py              # 5 coin flip tests
│   ├── test_betting.py           # 15 betting engine tests
│   ├── test_simulation.py        # 5 simulation tests
│   ├── test_scenarios.py         # 11 scenario tests
│   ├── test_monte_carlo.py       # 5 Monte Carlo tests
│   └── test_phase9.py            # 59 Phase 9 comprehensive tests
├── README.md                     # Project documentation (this file)
└── config/
    └── experiment_config.yaml
```

---

## 9. Installation

### Virtual Environment

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
pandas
numpy
matplotlib
pyyaml
```

Note: Matplotlib is required for visualization chart rendering. If matplotlib is not available, visualization functions still work in "stub mode" for testing purposes.

### Verification

```bash
# Verify the package imports correctly
python3 -c "import probability_betting_simulation; print('OK')"
# Or from the project root:
python3 -c "from src import coin, betting, simulation; print('All modules import successfully')"
```

---

## 10. Running Experiments

### Experiment 1: Coin Probability

```bash
# From the project root directory
python3 -m src.experiments.run_coin_experiment \
    --config_path config/experiment_config.yaml \
    --num_simulations 5
```

Or using the runner script:

```bash
python3 experiments/experiment_01_coin_probability/run_experiment.py
```

### Experiment 2: Betting Strategy

```bash
# From the project root directory
python3 -m src.experiments.run_betting_experiment \
    --config_path config/experiment_config.yaml \
    --num_simulations 5
```

Or using the runner script:

```bash
python3 experiments/experiment_02_betting/run_experiment.py
```

### Available Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| starting_chips | 100 | Starting chip balance |
| bets_per_iteration | 10 | Number of bets per iteration |
| win_side | HEADS | The winning side |
| loss_side | TAILS | The losing side |
| win_multiplier | 2 | Payout multiplier for wins |
| minimum_bet | 1 | Minimum bet size for bankruptcy check |
| bankruptcy_rule | balance_below_minimum_bet | Bankruptcy rule name |
| coin_flips | 100 | Number of flips for Experiment 1 |
| random_seed | null | Random seed for reproducibility |
| number_of_simulations | 1 | Number of simulations to run |
| starting_capital_scenarios | [50, 100, 1000] | Starting chip levels for Experiment 2 |

---

## 11. Results

### Existing Results

The project has generated experiment results from both experiment types. Below is a summary of the actual results that exist in the repository.

#### Experiment 1: Coin Probability Results

Summary of observed probabilities across different flip counts. Results are stored in `results/summaries/` as JSON files.

Key finding: As the number of flips increases, the observed heads probability varies around the theoretical 0.5, demonstrating the Law of Large Numbers. The magnitude of deviation from 0.5 decreases with more flips.

#### Experiment 2: Betting Strategy Results

Results across the three starting capital scenarios. Summaries are stored in `results/summaries/`.

**Low scenario (50 chips)**:
- With 10 bets per iteration (bet size = floor(50/10) = 5)
- Bankruptcy is very likely over repeated simulations
- Average survival time and final balance distribution vary significantly across simulations

**Baseline scenario (100 chips)**:
- With 10 bets per iteration (bet size = floor(100/10) = 10)
- Moderate bankruptcy probability
- Some simulations survive many iterations, others go bankrupt quickly

**High scenario (1000 chips)**:
- With 10 bets per iteration (bet size = floor(1000/10) = 100)
- Bankruptcy is less likely
- Simulations tend to survive many more iterations on average
- Maximum balance reached varies significantly

Important: These results are estimates from a finite number of simulations. Different runs with different random seeds will produce different specific outcomes, though the general patterns (bankruptcy more likely with smaller starting capital) are consistent.

### Objective Summary (No Invented Numbers)

- **Bankruptcy rates vary by starting capital**: Smaller starting capital generally correlates with higher bankruptcy rates across repeated simulations
- **Profitability varies**: Some simulations end in profit, some in loss, some in bankruptcy
- **Survival time varies**: The number of iterations before bankruptcy varies significantly even with the same starting capital
- **Monte Carlo provides distributions**: Rather than a single outcome, the simulation produces a distribution of possible outcomes with associated frequencies

These results are estimates subject to sampling variability. More simulations would produce more stable estimates.

---

## 12. Visualizations

The project includes 8 chart types, generated via `src/visualizations.py`. Charts are rendered using matplotlib; if matplotlib is not installed, functions execute in stub mode.

### Available Chart Types

| Chart Type | Description |
|------------|-------------|
| `balance_vs_iteration.png` | Single simulation balance over iteration time, with starting balance reference line |
| `multiple_balance_paths.png` | Multiple simulation paths showing different random sequences side-by-side |
| `final_balance_distribution.png` | Histogram of final balances with starting balance and bankruptcy (0) reference lines |
| `bankruptcy_rate_by_capital.png` | Comparative bar chart of bankruptcy rates across starting capital levels (50, 100, 1000) |
| `profit_loss_distribution.png` | Pie chart of profit/loss/break-even/bankrupt outcome distribution |
| `survival_curves.png` | Plot showing how many simulations survive versus iterations — y-axis = surviving count, x-axis = iteration number |
| `maximum_balance_distribution.png` | Histogram of maximum balance reached during simulations, with starting balance reference line |
| `observed_probability_vs_flips.png` | Law of Large Numbers demonstration: observed Heads probability across increasing flip counts, with theoretical 50% reference line |

Charts are saved to `results/figures/` with filenames indicating the experiment and chart type. Each chart includes appropriate axis labels, legends, and reference lines where applicable.

---

## 13. Limitations

### Statistical Limitations

- **This is a stochastic simulation**: Results depend on specific random sequences generated during the simulation
- **Results depend on random sequences**: A single run is one possible outcome, not a definitive prediction
- **Simulation estimates are not exact theoretical probabilities**: The simulation provides empirical estimates that converge toward theoretical values with more simulations, but never reach them exactly
- **The betting strategy is artificially defined**: The rules (10 bets per iteration, bet size = floor(balance/10), 2× payout on heads) are game-defined, not derived from real-world betting

### Real-World Limitations

- **Real-world gambling has additional factors**: Transaction costs, table limits, changing odds, player skill, psychology, and other factors not modeled here
- **The model does not account for real-world psychology**: Risk tolerance, emotion-driven decisions, superstition, and other human factors
- **External constraints not modeled**: Banking limits, credit availability, legal restrictions, and other real-world constraints
- **Transaction costs not accounted for**: Each bet typically incurs fees or house edge not included in this model
- **Changing odds not modeled**: Real-world probabilities may change based on numerous factors
- **The simulation does not establish that a strategy is profitable in real life**: These are artificial experiments, not real gambling strategy validation

### Model Assumptions

- Infinite player (no table limits beyond bankruptcy)
- Constant probabilities (fair coin / fixed win probability)
- Integer chip arithmetic (no fractional chips)
- No strategy adaptation during play
- One player, one-game scenario

---

## 14. Future Work

Possible future experiments and extensions:

- **Different win probabilities**: Test with biased coins (e.g., p = 0.45 or p = 0.55) rather than fair 50/50
- **Different payout ratios**: Test payout multipliers other than 2× (e.g., 1.5×, 3×)
- **Different betting percentages**: Instead of floor(balance/10), test fixed percentages (e.g., 5%, 10%, 20% of balance)
- **Fixed betting**: Test strategy where bet size is constant rather than scaled to balance
- **Martingale-style strategies**: Double bet after loss, reset after win
- **Stop-loss rules**: Stop simulating after N consecutive losses or after balance drops below threshold
- **Take-profit rules**: Stop after reaching a target balance
- **Comparison of strategies**: Side-by-side comparison of multiple betting strategies
- **Confidence intervals**: Calculate confidence intervals for bankruptcy rates and other metrics
- **Sensitivity analysis**: Test how sensitive results are to parameter changes

**Important**: These are suggested directions for future research. They are not completed work and should not be presented as such.

---

## 15. License

This project is licensed under the MIT License. See the LICENSE file for details, or contact the project maintainer if no LICENSE file exists.

MIT License key permissions:
- Commercial use
- Modification
- Distribution
- Private use

MIT License key conditions:
- License and copyright notice must be retained
- Same license must be included in redistributions

---

## 16. Contact

Project maintainer: Hareesh

For questions, contributions, or discussions about the project, please refer to the GitHub repository issues.

---

## Appendix: Quick Start

```bash
# 1. Clone or navigate to project
cd /path/to/probability-betting-simulation

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Experiment 1 (Coin Probability)
python3 -m src.experiments.run_coin_experiment --num_simulations 5

# 5. Run Experiment 2 (Betting Strategy)
python3 -m src.experiments.run_betting_experiment --num_simulations 5

# 6. Run analysis on existing results
python3 -m src.analysis.run_analysis

# 7. View generated charts
# Open files in results/figures/ or run Python to display

# 8. Run the test suite
python3 -m pytest tests/ -v
```