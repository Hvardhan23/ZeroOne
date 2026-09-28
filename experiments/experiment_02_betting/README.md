# Experiment 2: Betting Strategy

## Objective

Investigate how different starting capital levels affect the simulated path of a repeated-betting strategy. The experiment runs the same betting rules across three capital scenarios (low, baseline, high) to compare outcomes.

## Three Scenarios

| Scenario | Starting Chips | Initial Bet | Description |
|----------|---------------|-------------|-------------|
| **LOW** | 50 chips | floor(50/10) = 5 chips | Small starting capital; quicker to bankruptcy |
| **BASELINE** | 100 chips | floor(100/10) = 10 chips | Standard starting capital as per default config |
| **HIGH** | 1000 chips | floor(1000/10) = 100 chips | Large starting capital; more iterations before bankruptcy |

## Exact Rules

The betting rules are consistent across all scenarios:

- **One iteration** consists of exactly 10 bets.
- **Before each iteration**, the player's current balance is divided into 10 equal betting opportunities.
- **Bet size** = floor(current_balance / 10), determined at the start of the iteration and fixed for all 10 bets within that iteration.
- **Heads (win)**: payout = 2 × bet, net profit = +bet (original stake returned as part of the payout).
- **Tails (loss)**: payout = 0, net profit = -bet.
- **Balance update**: new_balance = current_balance + net_profit.
- **Bankruptcy**: occurs when floor(balance / 10) < 1, meaning the player cannot place the minimum 1-chip bet.
- **Integer chips only**: no floating-point arithmetic; all balances and bet sizes are whole numbers.

The simulation stops when the player becomes bankrupt.

## Why Starting Capital Is Varied

The purpose is to compare how different starting capital levels affect the simulated path under the defined betting strategy. Specifically:

- A smaller starting capital (50 chips) reaches bankruptcy faster with fewer bets.
- A medium starting capital (100 chips) serves as the baseline/default scenario.
- A larger starting capital (1000 chips) allows more iterations before potential bankruptcy.

The experiment **does not** claim that higher starting capital guarantees success. It only measures outcomes under the defined strategy with integer-chip arithmetic.

## Assumptions

- The coin flip is fair: Heads and Tails each have probability 0.5.
- Each bet is independent and identically distributed.
- The random number generator is seeded for reproducibility when a seed is provided.
- Starting chip values are taken from the configuration scenarios (50, 100, 1000).
- The bet size is recalculated at the start of each new iteration based on the ending balance of the previous iteration.

## Limitations

- This is a simulation/experiment and does NOT attempt to predict real-world gambling outcomes.
- Results are specific to the integer-chip betting rule set and may not apply to other payout structures.
- A single simulation run (num_simulations=1) may not capture the full probabilistic distribution; increasing the number of simulations provides more statistical confidence.
- The experiment uses a fixed sequence of outcomes per scenario for deterministic testing; with random seeds, results will vary.
- Very small starting capitals (e.g., 1-4 chips) may bankrupt immediately without any bets being placed.

## Output

### Summary Result (JSON)

Saved under `data/results/<experiment_id>.json`:

```json
{
  "experiment_id": "betting_low_20260928_023053_1790562653",
  "experiment_name": "betting_strategy",
  "timestamp": "2026-09-28T02:30:53.123456",
  "scenarios_tested": ["low", "baseline", "high"],
  "num_simulations_per_scenario": 1,
  "bets_per_iteration": 10,
  "scenario_results": {
    "low": {
      "starting_chips": 50,
      "num_simulations": 1,
      "final_balances": [6],
      "bankruptcy_count": 0,
      "surviving_count": 1,
      "bankruptcy_rate": 0.0
    },
    "baseline": {
      "starting_chips": 100,
      "num_simulations": 1,
      "final_balances": [6],
      "bankruptcy_count": 0,
      "surviving_count": 1,
      "bankruptcy_rate": 0.0
    },
    "high": {
      "starting_chips": 1000,
      "num_simulations": 1,
      "final_balances": [8],
      "bankruptcy_count": 0,
      "surviving_count": 1,
      "bankruptcy_rate": 0.0
    }
  }
}
```

### Detailed Result (CSV)

Saved under `data/results/betting_<scenario>_<experiment_id>_detailed.csv`:

```
run_id,scenario_name,starting_chips,bet_number,iteration,outcome,net_profit,payout,ending_balance
betting_low_20260928_023053_1790562653,low,50,summary,1,6,,,6
```

Each row represents one simulation's outcome per scenario. The CSV includes:
- `run_id`: unique experiment/run ID
- `scenario_name`: low, baseline, or high
- `starting_chips`: the starting chip count for the scenario
- `bet_number`: the bet number within the iteration
- `iteration`: the iteration number
- `outcome`: HEADS or TAILS
- `net_profit`: +bet for HEADS, -bet for TAILS
- `payout`: 2×bet for HEADS, 0 for TAILS
- `ending_balance`: the balance after the bet

### Console Output

```
Experiment ID: betting_low_20260928_023053_1790562653
Scenarios: ['low', 'baseline', 'high']
Simulations per scenario: 1
Seed: None

Scenario: low
  Starting chips: 50
  Simulations: 1
  Bankruptcies: 0/1
  Bankruptcy rate: 0.0000
  Surviving: 1/1
  Final balance range: 6 to 6
  Max balance: 6
  Min balance: 6
  Total profit/loss: -44.0

Scenario: baseline
  Starting chips: 100
  Simulations: 1
  Bankruptcies: 0/1
  Bankruptcy rate: 0.0000
  Surviving: 1/1
  Final balance range: 6 to 6
  Max balance: 6
  Min balance: 6
  Total profit/loss: -94.0

Scenario: high
  Starting chips: 1000
  Simulations: 1
  Bankruptcies: 0/1
  Bankruptcy rate: 0.0000
  Surviving: 1/1
  Final balance range: 8 to 8
  Max balance: 8
  Min balance: 8
  Total profit/loss: -992.0

============================================================
COMPARISON ACROSS SCENARIOS
============================================================

LOW      | Start:    50 | Bankruptcy: 0.00% | Surviving: 1/1
BASELINE | Start:   100 | Bankruptcy: 0.00% | Surviving: 1/1
HIGH     | Start:  1000 | Bankruptcy: 0.00% | Surviving: 1/1
```

## Reproducibility

- If a random seed is supplied in the configuration, the experiment is deterministic.
- The same seed will always produce the same results.
- Each scenario uses seed + scenario_index to avoid collisions between different scenarios.
- If seed is null, normal random behavior applies and results vary between runs.

## Limitations

- This is a simulation/experiment and does NOT attempt to predict real-world gambling outcomes.
- Finite experiments cannot prove convergence to any particular probability; they only observe outcomes under the defined strategy.
- Results are specific to the integer-chip betting rule set and payout multiplier of 2x.
- The experiment measures observed frequencies, not theoretical guarantees.