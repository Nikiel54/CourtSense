#!/usr/bin/env python
"""
HCA calibration sweep.

Splits:
  Train  : 1978-79 through 2020-21  (~46 400 games)
  Val    : 2021-22  (used to pick best HCA)
  Test   : 2022-23  (untouched — reported in BENCHMARKS.md)

For each HCA candidate we build ratings from scratch on the train split,
then do a rolling evaluation on the val split (predict before updating),
and report Brier score.  Accuracy is shown for reference but Brier is the
optimisation objective because it is continuous and distinguishes probability
calibration that accuracy cannot.
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.append(str(ROOT / "backend" / "app"))

from ml.data_cleaning import NBADataProcessor
from ml.elo_system import EloSystem


# ---------------------------------------------------------------------------
# helpers (duplicated from benchmark.py to keep this script self-contained)
# ---------------------------------------------------------------------------

def brier_score(y_true, y_pred):
    return float(np.mean((np.array(y_pred) - np.array(y_true)) ** 2))

def log_loss(y_true, y_pred, eps=1e-15):
    p = np.clip(np.array(y_pred), eps, 1 - eps)
    y = np.array(y_true)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))

def accuracy(y_true, y_pred):
    return float(np.mean((np.array(y_pred) >= 0.5).astype(int) == np.array(y_true)))


def rolling_eval(hca, train_df, eval_df):
    """Full retrain from scratch with given HCA, then rolling eval on eval_df."""
    elo = EloSystem(k_factor=20, hca=hca)

    for _, g in train_df.iterrows():
        elo.update_ratings(
            team_home_id=int(g["team_id_home"]),
            team_away_id=int(g["team_id_away"]),
            home_score=int(g["pts_home"]),
            away_score=int(g["pts_away"]),
            game_date=g["game_date"],
        )

    y_true, y_pred = [], []
    for _, g in eval_df.iterrows():
        pred = elo.predict(int(g["team_id_home"]), int(g["team_id_away"]))
        actual = 1 if g["pts_home"] > g["pts_away"] else 0
        y_true.append(actual)
        y_pred.append(pred["home_win_probability"])
        elo.update_ratings(
            team_home_id=int(g["team_id_home"]),
            team_away_id=int(g["team_id_away"]),
            home_score=int(g["pts_home"]),
            away_score=int(g["pts_away"]),
            game_date=g["game_date"],
        )

    return y_true, y_pred


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

data_path = str(ROOT / "backend" / "data" / "raw" / "game.csv")
processor = NBADataProcessor(data_path=data_path)
df = processor.load_and_clean_data()

FACTOR = 10000
df["actual_year"] = df["season_id"] % FACTOR
modern = df[
    (df["season_id"] >= 2 * FACTOR + 1978) & (df["season_id"] < 30000)
].copy().sort_values("game_date")

# Three-way split
train = modern[modern["actual_year"] < 2021]
val   = modern[modern["actual_year"] == 2021]
test  = modern[modern["actual_year"] == 2022]

print(f"Train : {len(train):>6,} games  (1978-79 to 2020-21)")
print(f"Val   : {len(val):>6,} games  (2021-22)")
print(f"Test  : {len(test):>6,} games  (2022-23, untouched)\n")

# ---------------------------------------------------------------------------
# sweep
# ---------------------------------------------------------------------------

hca_candidates = np.arange(40, 105, 5)   # 40, 45, ..., 100
results = {}

print(f"{'HCA':>5}  {'Brier':>8}  {'Log-Loss':>9}  {'Accuracy':>9}")
print("-" * 40)

for hca in hca_candidates:
    y_true, y_pred = rolling_eval(float(hca), train, val)
    bs  = brier_score(y_true, y_pred)
    ll  = log_loss(y_true, y_pred)
    acc = accuracy(y_true, y_pred)
    results[float(hca)] = {"brier": bs, "log_loss": ll, "accuracy": acc}
    print(f"{hca:>5.0f}  {bs:>8.4f}  {ll:>9.4f}  {acc:>9.4f}")

best_hca = min(results, key=lambda h: results[h]["brier"])
print(f"\nBest HCA (min Brier on val): {best_hca:.0f}  "
      f"(Brier={results[best_hca]['brier']:.4f})")

# Save sweep table
out = {
    "sweep": {str(int(h)): v for h, v in results.items()},
    "best_hca": best_hca,
}
out_path = ROOT / "hca_sweep_results.json"
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"Sweep results saved to {out_path}")
