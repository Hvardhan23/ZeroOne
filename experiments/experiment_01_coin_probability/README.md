# Experiment 1: Coin Probability

## Objective

Study the observed probability of Heads vs Tails using repeated coin flips.
Compare observed frequency with the theoretical probability of 50% for each outcome.

## Theory

For a fair coin, the theoretical probability of Heads is 0.5 and Tails is 0.5.
Each flip is an independent Bernoulli trial with p=0.5 for each outcome.
The Law of Large Numbers states that as the number of flips increases,
the observed proportion will converge toward the theoretical probability.

This experiment tests this convergence across multiple scales:
- 100 flips (small sample)
- 1,000 flips (moderate sample)
- 10,000 flips (large sample)
- 100,000 flips (very large sample)
- 1,000,000 flips (extremely large sample)

## Methodology

1. Configure the number of flips from experiment_config.yaml
2. Simulate coin flips using a proper random number generator with optional seed
3. Count observed Heads and Tails
4. Calculate observed probabilities: Heads / total_flips, Tails / total_flips
5. Compare against theoretical probability of 0.5 for each
6. Record probability differences (observed - theoretical)

Parameters are read from config/experiment_config.yaml:
- coin_flip_counts: List of flip counts to test
- random_seed: Optional seed for reproducibility

## Parameters

| Parameter | Value | Description |
|---|---|---|
| experiment_name | coin_probability | Name of the experiment |
| coin_flip_counts | [100, 1000, 10000, 100000, 1000000] | Flip counts to test |
| random_seed | null | Optional seed for reproducibility |
| number_of_simulations | 1 | Number of independent simulations per count |

## Output

### Summary Output (printed to console)

```
Experiment ID: <unique-id>
Total flips: 100
Heads: 52
Tails: 48
Observed Heads probability: 0.5200
Observed Tails probability: 0.4800
Theoretical Heads probability: 0.5
Theoretical Tails probability: 0.5
Heads probability difference: 0.0200
Tails probability difference: -0.0200
```

### Summary Result (JSON file)

Saved under `data/results/<experiment_id>.json`:

```json
{
    "experiment_id": "...",
    "experiment_name": "Coin Flip Probability",
    "timestamp": "...",
    "total_flips": 100,
    "heads": 52,
    "tails": 48,
    "heads_probability": 0.52,
    "tails_probability": 0.48,
    "theoretical_heads_probability": 0.5,
    "theoretical_tails_probability": 0.5,
    "heads_probability_difference": 0.02,
    "tails_probability_difference": -0.02
}
```

### Detailed Result (CSV file)

Saved under `data/results/<experiment_id>_detailed.csv`:

```
experiment_id,flip_number,outcome
<id>,1,HEADS
<id>,2,TAILS
<id>,3,HEADS
...
```

Each row represents one flip, with the flip number and outcome.

## Reproducibility

- If a random seed is supplied in the configuration, the experiment is deterministic
- The same seed will always produce the same results
- Each flip count uses seed + index to avoid collisions between different counts
- If seed is null, normal random behavior applies and results vary between runs

## Limitations

- This is a simulation/experiment and does NOT attempt to predict real-world gambling outcomes
- Finite experiments cannot prove the probability is exactly 50%; they only observe convergence
- Very small sample sizes (100 flips) may show significant deviations from 0.5
- Results are specific to the random number generator implementation
- Each flip is assumed to be independent and identically distributed