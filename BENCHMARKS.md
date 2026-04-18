# CourtSense — Benchmarks

## Final Numbers (v3 — HCA=40)

**Protocol**: Three-way split, no leakage.

| Split | Seasons | Games |
|---|---|---|
| Train | 1978-79 to 2021-22 | 47,601 |
| Val *(HCA tuning only)* | 2021-22 | 1,230 |
| **Test** *(reported below, never touched during tuning)* | **2022-23** | **1,230** |

### Test-set metrics — 2022-23 (1,230 games, home win rate 58.0 %)

| Metric | CourtSense v3 (HCA=40) | CourtSense v1 (HCA=100) | Baseline: Always-Home | Baseline: Coin-Flip |
|---|---|---|---|---|
| **Accuracy** | 61.71 % | 62.93 % | 58.05 % | 50.00 % |
| **Brier Score** ↓ | 0.2357 | 0.2302 | 0.2435 | 0.2500 |
| **Log-Loss** ↓ | 0.6724 | 0.6561 | 0.6801 | 0.6931 |

**v3 beats both baselines on every metric.** v1 (un-calibrated HCA=100) beats v3 on
this specific test season — explained below.

---

## HCA Calibration

### Why calibrate HCA?

The original system hardcodes home-court advantage at **100 Elo points**.  An
NBA home team wins roughly 58 % of games; the 100-point bump overshoots the
historical signal.  We swept HCA on the held-out 2021-22 validation season
(never touching 2022-23) to find the Brier-optimal value.

### Validation sweep (2021-22, 1,230 games)

Training state at start of each sweep: ratings built on 1978-79 → 2020-21.
Rolling evaluation: predict before each game, update after.

| HCA | Brier (val) | Log-Loss (val) | Accuracy (val) |
|---|---|---|---|
| 40 | **0.2269** | **0.6524** | 0.6431 |
| 45 | 0.2269 | 0.6528 | 0.6423 |
| 50 | 0.2271 | 0.6534 | 0.6447 |
| 55 | 0.2272 | 0.6541 | 0.6447 |
| 60 | 0.2275 | 0.6550 | 0.6447 |
| 65 | 0.2278 | 0.6561 | 0.6472 |
| 70 | 0.2281 | 0.6574 | 0.6423 |
| 75 | 0.2285 | 0.6588 | 0.6415 |
| 80 | 0.2290 | 0.6605 | 0.6423 |
| 85 | 0.2296 | 0.6623 | 0.6463 |
| 90 | 0.2302 | 0.6643 | 0.6480 |
| 95 | 0.2308 | 0.6665 | 0.6472 |
| 100 | 0.2316 | 0.6689 | 0.6504 |

Fine-grained search (step 1, range 32–49) confirmed the minimum at **HCA = 40**
(Brier 0.22690).  The curve is monotonically decreasing from HCA=0 through 40,
then monotonically increasing.  The trough is shallow: HCA=35 and HCA=45 both
sit within 0.00004 Brier of the minimum, so this parameter is not
high-leverage — the signal is real but small.

### Why v3 (HCA=40) is slightly worse on the test season

The validation improvement was **Δ Brier = −0.0047** (HCA=100 → HCA=40 on
2021-22).  On the 2022-23 test season the direction reversed: HCA=40 scores
Brier 0.2357 vs HCA=100's 0.2302, a degradation of 0.0055.

This is within normal year-to-year variance of HCA.  The 2021-22 season
(first full post-COVID season with crowds) appears to have had a lower
effective home edge than 2022-23.  Because the validation improvement was
marginal and home advantage varies inter-seasonally, the calibration did not
generalise.  This is an honest result: 2022-23 was never seen during tuning.

A more robust fix would be to treat HCA as a rolling estimate updated each
season rather than a single static value.

---

## Held-out Season Evaluation (v1, original run)

**Methodology**: Train on 1978-79 through 2021-22 (47,601 games).
Rolling evaluation on 2022-23 (1,230 games) with HCA=100.

| Metric | CourtSense v1 | Baseline: Always-Home | Baseline: Coin-Flip |
|---|---|---|---|
| **Accuracy** | **62.93 %** | 58.05 % | 50.00 % |
| **Brier Score** ↓ | **0.2302** | 0.2435 | 0.2500 |
| **Log-Loss** ↓ | **0.6561** | 0.6801 | 0.6931 |

*Test set: 1,230 games. Home win rate in 2022-23: 58.0 %.*

---

## How to reproduce

```bash
# Full audit + final benchmark
python benchmark.py

# HCA calibration sweep (writes hca_sweep_results.json)
python calibrate_hca.py
```

