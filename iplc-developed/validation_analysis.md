# IPLC Developed-Country Allocation: Validation Analysis

**Date:** 2026-04-24  
**Branch:** terrestrial  

## Concern: Option 1 and Option 2 results appear too close

At $1bn fund size with IPLC share = 50%:

| Metric | Option 1 (Equality) | Option 2 (Banded) | Difference |
|--------|---------------------|--------------------|------------|
| 9-country total | $45.92m (4.59%) | $42.19m (4.22%) | $3.73m |
| 9-country IPLC | $22.96m (2.30%) | $21.09m (2.11%) | $1.87m |
| Ratio (Opt2/Opt1) | — | 0.92 | — |

The IPLC pool differs by only ~0.19pp (2.30% vs 2.11%). This is **expected and correct**, not a bug.

## Why the two options produce similar results

### Option 1 (Raw Equality)
- All 196 CBD Parties receive an equal share: 1/196 = 0.51% each.
- Each of the 9 developed countries gets **$5.10m** total, **$2.55m** IPLC.
- Total IPLC pool: 9 × $2.55m = **$22.96m**.

### Option 2 (Banded IUSAF)
- 151 Parties are eligible (142 developing + 9 developed with overridden income).
- The 9 countries split across two bands:
  - **Band 4** (0.1%–1.0%): 5 countries (Denmark, Finland, NZ, Norway, Sweden) with weight 0.95 each → IUSAF share ≈ 0.52% each → **$5.17m** total, **$2.59m** IPLC.
  - **Band 5** (1.0%–10.0%): 4 countries (Australia, Canada, Japan, Russia) with weight 0.75 each → IUSAF share ≈ 0.41% each → **$4.08m** total, **$2.04m** IPLC.
- Total IPLC pool: 5×$2.59m + 4×$2.04m = **$21.09m**.

### Why close?
The 9 countries include both *smaller* (Band 4, who gain) and *larger* (Band 5, who lose) UN-share countries relative to equal allocation. The gains and losses partially cancel:
- Band 4 countries get **more** than equality ($5.17m vs $5.10m, +1.4%).
- Band 5 countries get **less** than equality ($4.08m vs $5.10m, −20%).

The net effect is only a ~$1.87m shift because:
1. The banding compresses variation (5 countries in Band 4 get the same weight, 4 in Band 5).
2. The 0.95 and 0.75 weights are moderate — not extreme.
3. The IPLC component halves everything, so the absolute difference is halved again.

This is precisely the design intent: banded IUSAF provides a defensible methodology, but the aggregate result for a mixed-income group of 9 countries is close to equality because their UN shares straddle the band boundary.

## Structural validation tests

The following invariants must hold regardless of fund size:

1. **IPLC + State = Total** for every country in both options.
2. **IPLC share = 50%** of total allocation for every country in both options.
3. **Fund conservation**: total allocations across all eligible Parties sum to the fund size.
4. **Scale invariance**: allocations at different fund sizes are proportional (2× fund → 2× allocation).
5. **Band assignment**: the 9 countries map correctly to Bands 4 and 5 based on their UN shares.
6. **No HI leakage**: in Option 2, only the 9 specified countries are made eligible; all other high-income CBD parties remain excluded.
7. **Option 1 > Option 2**: equality always produces a larger 9-country total than banding (because equality maximises the share of small countries, and this group includes 5 that benefit).
8. **Cali Fund percentage is constant across fund sizes** under each option.
