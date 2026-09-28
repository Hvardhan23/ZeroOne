"""Coin flip simulation for Experiment 1: Coin Probability."""

import random
from typing import Literal

CoinSide = Literal["HEADS", "TAILS"]


def flip_coin(seed: int | None = None) -> CoinSide:
    """Flip a coin and return the result.

    Args:
        seed: Optional random seed for reproducibility. If provided,
              seeds the RNG for this call only (does not modify global state).

    Returns:
        Either "HEADS" or "TAILS".
    """
    if seed is not None:
        random.seed(seed)
    return random.choice(["HEADS", "TAILS"])


def simulate_flips(
    num_flips: int,
    seed: int | None = None,
) -> dict[str, int]:
    """Simulate a series of coin flips.

    Args:
        num_flips: Number of flips to simulate.
        seed: Optional random seed for reproducibility. If provided,
              the same seed will always produce the same results.

    Returns:
        Dictionary with counts of HEADS and TAILS.
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    heads = 0
    tails = 0
    outcomes = []

    for _ in range(num_flips):
        result = rng.choice(["HEADS", "TAILS"])
        outcomes.append(result)
        if result == "HEADS":
            heads += 1
        else:
            tails += 1

    return {
        "HEADS": heads,
        "TAILS": tails,
        "outcomes": outcomes,
    }