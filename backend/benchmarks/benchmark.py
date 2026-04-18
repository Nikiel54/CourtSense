#!/usr/bin/env python
"""
CourtSense Elo benchmarking — held-out season evaluation.

Trains on all regular-season games up to (not including) the held-out
season, then evaluates rolling predictions on that season.  After each
game the ratings are updated with the true result, mirroring how the
live system operates.

Usage:
    python benchmark.py
"""

import sys
import math
import json
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.append(str(ROOT / "backend" / "app"))

from ml.data_cleaning import NBADataProcessor
from ml.elo_system import EloSystem


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def accuracy(y_true, y_pred_prob):
    pred = (np.array(y_pred_prob) >= 0.5).astype(int)
    return float(np.mean(pred == np.array(y_true)))


def brier_score(y_true, y_pred_prob):
    return float(np.mean((np.array(y_pred_prob) - np.array(y_true)) ** 2))


def log_loss(y_true, y_pred_prob, eps=1e-15):
    p = np.clip(np.array(y_pred_prob), eps, 1 - eps)
    y = np.array(y_true)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def rolling_evaluate(train_df, test_df):
    """
    Train Elo on train_df, then predict each game in test_df before
    updating ratings with the true result.

    Returns (y_true, y_pred_home_win_prob).
    """
    elo = EloSystem(k_factor=20, base_elo=1300)

    print(f"  Training on {len(train_df):,} games …")
    for _, g in train_df.iterrows():
        elo.update_ratings(
            team_home_id=int(g["team_id_home"]),
            team_away_id=int(g["team_id_away"]),
            home_score=int(g["pts_home"]),
            away_score=int(g["pts_away"]),
            game_date=g["game_date"],
        )

    print(f"  Evaluating on {len(test_df):,} held-out games …")
    y_true, y_pred = [], []

    for _, g in test_df.iterrows():
        pred = elo.predict(
            team_home_id=int(g["team_id_home"]),
            team_away_id=int(g["team_id_away"]),
        )
        actual = 1 if g["pts_home"] > g["pts_away"] else 0
        y_true.append(actual)
        y_pred.append(pred["home_win_probability"])

        # Update ratings so future predictions use current form
        elo.update_ratings(
            team_home_id=int(g["team_id_home"]),
            team_away_id=int(g["team_id_away"]),
            home_score=int(g["pts_home"]),
            away_score=int(g["pts_away"]),
            game_date=g["game_date"],
        )

    return y_true, y_pred


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data_path = str(ROOT / "backend" / "data" / "raw" / "game.csv")
    processor = NBADataProcessor(data_path=data_path)
    df = processor.load_and_clean_data()

    FACTOR = 10000
    df["actual_year"] = df["season_id"] % FACTOR

    # Modern regular-season games only
    modern = df[
        (df["season_id"] >= 2 * FACTOR + 1978) & (df["season_id"] < 30000)
    ].copy().sort_values("game_date")

    seasons = sorted(modern["actual_year"].unique())
    held_out_year = int(seasons[-1])           # 2022  →  2022-23 season
    prev_year     = int(seasons[-2])

    print(f"Held-out season : {held_out_year}-{held_out_year + 1}")
    print(f"Training seasons: 1978-79 through {prev_year}-{prev_year + 1}\n")

    train = modern[modern["actual_year"] < held_out_year]
    test  = modern[modern["actual_year"] == held_out_year]

    y_true, y_pred = rolling_evaluate(train, test)

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # --- CourtSense metrics ---
    acc = accuracy(y_true, y_pred)
    bs  = brier_score(y_true, y_pred)
    ll  = log_loss(y_true, y_pred)

    # --- Baselines ---
    home_rate = float(y_true.mean())   # empirical home win rate in test set

    # Baseline A: always predict home team wins (fixed prob = home_rate)
    base_acc  = max(home_rate, 1 - home_rate)   # pick whichever label dominates
    base_bs   = brier_score(y_true, np.full_like(y_pred, home_rate))
    base_ll   = log_loss(y_true, np.full_like(y_pred, home_rate))

    # Baseline B: 50-50 (random / coin flip)
    coin_acc  = 0.5
    coin_bs   = brier_score(y_true, np.full_like(y_pred, 0.5))
    coin_ll   = log_loss(y_true, np.full_like(y_pred, 0.5))

    # --- Print ---
    w = 28
    print(f"\n{'='*50}")
    print(f"{'METRIC':<{w}} {'COURTSENSE':>10}  {'HOME-ALWAYS':>12}  {'COIN-FLIP':>10}")
    print(f"{'-'*50}")
    print(f"{'Accuracy':<{w}} {acc:>10.4f}  {base_acc:>12.4f}  {coin_acc:>10.4f}")
    print(f"{'Brier Score (lower=better)':<{w}} {bs:>10.4f}  {base_bs:>12.4f}  {coin_bs:>10.4f}")
    print(f"{'Log-Loss (lower=better)':<{w}} {ll:>10.4f}  {base_ll:>12.4f}  {coin_ll:>10.4f}")
    print(f"{'='*50}")
    print(f"\nTest set: {len(y_true)} games  |  home win rate: {home_rate:.3f}\n")

    return {
        "held_out_season": f"{held_out_year}-{held_out_year+1}",
        "n_train": len(train),
        "n_test": len(y_true),
        "home_win_rate_in_test": round(home_rate, 4),
        "courtsense": {
            "accuracy": round(acc, 4),
            "brier_score": round(bs, 4),
            "log_loss": round(ll, 4),
        },
        "baseline_home_always": {
            "accuracy": round(base_acc, 4),
            "brier_score": round(base_bs, 4),
            "log_loss": round(base_ll, 4),
        },
        "baseline_coin_flip": {
            "accuracy": round(coin_acc, 4),
            "brier_score": round(coin_bs, 4),
            "log_loss": round(coin_ll, 4),
        },
    }


if __name__ == "__main__":
    results = main()
    out_path = ROOT / "benchmark_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")
