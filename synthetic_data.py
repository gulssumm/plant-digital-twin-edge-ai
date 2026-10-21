"""
Multi-Regime Bio-Signal Simulation Generator for the Plant Digital Twin.

Replicates the 50 Hz signal generation equations defined in the Arduino firmware
(sketch.ino) across alternating chronological regimes (Normal, Environmental Stress,
and Physical Trauma) so that chronological train/test splits (shuffle=False)
contain all three operational states in both partitions.
"""

import numpy as np
import pandas as pd

RANDOM_SEED = 42
NUM_STEPS = 1000
OUTPUT_CSV = "plant_dataset_1.csv"


def generate_chronological_dataset(num_steps=NUM_STEPS, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    signals = []
    labels = []

    for i in range(num_steps):
        # Training partition 
        if i < 200:
            state = 0  # Normal baseline state
        elif i < 350:
            state = 1  # Environmental stress episode 1
        elif i < 400:
            state = 2  # Physical trauma impulse 1
        elif i < 600:
            state = 0  # Recovery / normal baseline state
        elif i < 750:
            state = 1  # Environmental stress episode 2
        elif i < 800:
            state = 2  # Physical trauma impulse 2

        # Held-out test partition (final 20%: steps 800..999)
        elif i < 860:
            state = 0  # Test regime: Normal
        elif i < 930:
            state = 1  # Test regime: Environmental stress
        elif i < 960:
            state = 2  # Test regime: Physical trauma
        else:
            state = 0  # Post-trauma recovery baseline

        # Slow circadian baseline drift matching sketch.ino: 500 + sin(t * 0.02) * 50
        baseline = 500.0 + np.sin(i * 0.02) * 50.0

        if state == 0:
            sig = (
                baseline
                + np.sin(i * 0.1) * 30.0
                + np.sin(i * 0.05) * 20.0
                + rng.uniform(-15.0, 15.0)
            )
        elif state == 1:
            sig = (
                baseline
                + np.sin(i * 0.4) * 80.0
                + np.cos(i * 0.15) * 60.0
                + rng.uniform(-50.0, 40.0)
            )
        else:
            sig = (
                baseline
                + np.sin(i * 1.5) * 120.0
                + rng.uniform(-150.0, 350.0)
            )

        signals.append(sig)
        labels.append(state)

    df = pd.DataFrame({"Signal": signals, "Label": labels})
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} chronological bio-signal samples to '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    generate_chronological_dataset()