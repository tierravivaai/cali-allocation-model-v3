---
output:
  word_document: default
  html_document: default
---
# Break Points Analysis: Exploratory Data Analysis & Visualization

> **Note**: This is exploratory analysis on the `middle-dist` branch. Do not merge to main.

## Objective

Identify precise break points where TSAC and SOSAC overlays overtake the IUSAF baseline, and create visualizations showing how different parameter choices affect allocation outcomes.

---

## Model Structure

The allocation formula:

```
Final Share = IUSAF + TSAC + SOSAC (weights sum to 100%)
```

Where:
- **IUSAF**: Inverted UN Scale (band-weighted or raw inversion)
- **TSAC**: Terrestrial Stewardship Allocation Component (proportional to land area)
- **SOSAC**: SIDS Ocean Stewardship Allocation Component (equal share among SIDS)

---

## Known Balance Points (from existing analysis)

| Position | Description | TSAC | SOSAC | Key Characteristic |
|----------|-------------|------|-------|---------------------|
| Strict | China TSAC/IUSAF ≤ 1.0 | 1.5% | 3% | IUSAF dominant for all Parties |
| Bounded | Brazil TSAC/IUSAF ≤ 1.0 | 3.5% | 3% | IUSAF dominant for Band 5 Parties |
| Even | Minimises Gini (design constraint: Spearman > 0.85) | 5.0% | 3% | Gini minimum |

---

## Research Questions

1. **TSAC Overturn Point**: At what β value does TSAC become the dominant driver of allocations (TSAC component > IUSAF component for key Parties)?

2. **SOSAC Overturn Point**: At what γ value does SOSAC become the dominant driver for SIDS (SOSAC component > IUSAF component)?

3. **Decision Boundaries**: What are the lower and upper bounds for policy-relevant parameter choices?

---

## Scenarios to Analyze

| Scenario | TSAC | SOSAC | Description |
|----------|------|-------|-------------|
| Pure IUSAF | 0% | 0% | Baseline - pure inverted UN scale |
| Strict | 1.5% | 3% | Balance Point A - IUSAF dominance preserved |
| Bounded | 3.5% | 3% | Balance Point B - Brazil at threshold |
| Even | 5.0% | 3% | Balance Point C - Gini minimum |
| TSAC Overturn | TBD | 0% | TSAC overtakes IUSAF as driver |
| SOSAC Overturn | 0% | TBD | SOSAC overtakes IUSAF for SIDS |

---

## Methodology

### Computing Crossover Points

**TSAC Crossover**: Binary search on TSAC values to find where:
- `max(TSAC_component / IUSAF_component) = 1.0` for any Party
- Focus on China (binding constraint due to large land area, low IUSAF base)

**SOSAC Crossover**: Binary search on SOSAC values to find where:
- `max(SOSAC_component / IUSAF_component) = 1.0` for any SIDS Party
- Focus on SIDS with lowest IUSAF bases (Cuba, Singapore identified)

### Metrics

For each scenario, compute:
- Gini coefficient (distributional equality)
- Spearman rank correlation vs Pure IUSAF (structural preservation)
- Band 1 per-Party allocation
- SIDS total allocation
- LDC total allocation
- Number of Parties where overlay exceeds IUSAF

---

## Outputs

1. **analysis.py** - Python script computing all results
2. **scenario_results/** - CSV files for each scenario
3. **figures/** - Visualization outputs (SVG format)

### Visualizations

1. `break_point_timeline.svg` - Component ratios vs parameter values
2. `party_distribution_heatmap.svg` - Allocations by Party across scenarios
3. `decision_boundaries.svg` - Multi-panel summary with metrics

---

## Results Summary (for Reviewers)

### THE KEY INSIGHT

**The stewardship debate centers on approximately $40-60 million of a $1 billion fund (4-6%). The remaining 94-96% of allocations are not in dispute.**

This is critical context for negotiations:

| Metric | Value | Implication |
|--------|-------|-------------|
| Amount in play | $40-60m | Only 4-6% of total fund |
| Amount undisputed | $940-960m | 94-96% stable |
| Parties with < $0.5m transfer | 73% | Most see minimal change |
| Parties with > $1m transfer | 4% | Only 6 parties |

**Perspective**: A $1 million transfer represents 0.1% of the fund — equivalent to 0.1 cents on a dollar. Most transfers are smaller than this.

**Reframing for Negotiations**: If IUSAF is accepted as the equitable baseline for allocations, then the negotiation question becomes: *"How should we allocate the $40-60 million stewardship pool?"* 

This reframes the debate from a fundamental dispute over allocation methodology to a practical question about the appropriate use of a relatively small adjustment pool. The core equity structure (IUSAF) remains stable — the discussion is about margins.

### Two Types of Model Overturn

**Critical distinction**: There are two fundamentally different ways the model can "overturn":

| Overturn Type | Threshold | Meaning |
|---------------|-----------|---------|
| **Simple Overturn** | TSAC+SOSAC > 50% | Stewardship weights exceed IUSAF weights |
| **Order Overturn** | **TSAC ≈ 3%** | IUSAF band ordering breaks down |

**Simple Overturn** is a mathematical threshold where stewardship components collectively exceed 50% of the allocation weight. This is far outside current policy ranges.

**Order Overturn** is when the IUSAF band structure is subverted — when a lower band (Band 6: China) receives more per-party allocation than a higher band (Band 5: Brazil, India, Mexico). **This occurs at TSAC ≈ 2.95%** — much earlier than simple overturn.

### Order Overturn Analysis

Under Pure IUSAF, mean per-party allocation decreases monotonically:
```
Band 1 > Band 2 > Band 3 > Band 4 > Band 5 > Band 6
```

**When does this ordering break?**

| TSAC Level | Band 6 mean | Band 5 mean | Order Preserved? |
|------------|-------------|-------------|------------------|
| 0% (Pure IUSAF) | $2.21m | $4.13m | YES |
| 2.5% | $5.15m | $5.44m | YES (barely) |
| **3.0%** | **$5.74m** | **$5.70m** | **NO** - Band 6 overtakes Band 5 |
| 5.0% (Even) | $8.09m | $6.75m | NO - Clearly overturned |

**Order Overturn Threshold: TSAC ≈ 2.95%**

At this point:
- China (Band 6) receives more per-party than Brazil, India, Mexico (Band 5)
- The IUSAF equity ordering is subverted
- This is **17× lower** than the simple overturn threshold (50%)

### Current Scenarios vs Order Overturn

| Scenario | TSAC | Band Order | Position |
|----------|------|------------|----------|
| Strict | 1.5% | **Preserved** | Below order overturn |
| **Bounded** | **3.5%** | **Overturned** | **Above order overturn** |
| Even | 5.0% | Clearly overturned | Well above order overturn |

**Policy Implication**: Bounded scenario (TSAC=3.5%) already inverts the IUSAF band structure. Only Strict (TSAC=1.5%) preserves the monotonic ordering established by the inverted UN scale.

### Amount in Play at Different Fund Sizes

| Fund Size | Strict (4.3%) | Bounded (5.1%) | Even (6.0%) | Undisputed (94%) |
|-----------|---------------|----------------|--------------|------------------|
| $50m | $2.1m | $2.6m | $3.0m | $47.0m |
| $200m | $8.5m | $10.3m | $12.0m | $188.0m |
| $500m | $21.3m | $25.8m | $29.9m | $470.0m |
| $1 billion | $42.6m | $51.5m | $59.9m | $940.0m |
| $2 billion | $85.2m | $103.0m | $119.8m | $1,880.0m |

**Key point**: At any fund size, approximately **94% of allocations are stable** under the IUSAF baseline. The percentages remain constant; only the dollar amounts scale proportionally.

---

### Model-Level Overturn Points

**Key Principle**: The Cali Fund should allocate resources "in a fair, equitable, transparent, accountable manner". The following thresholds identify when stewardship components (TSAC/SOSAC) overtake the IUSAF equity baseline as the dominant driver of allocations.

**Allocation Formula**: 
`Final Share = IUSAF + TSAC + SOSAC` (weights sum to 100%)

| Overturn Type | Threshold | Condition |
|---------------|-----------|-----------|
| TSAC overtakes IUSAF | TSAC > IUSAF | **TSAC > ~48.5%** (at SOSAC=3%) |
| SOSAC overtakes IUSAF | SOSAC > IUSAF | **SOSAC > ~47.5%** (at TSAC=5%) |
| **Combined stewardship overtakes IUSAF** | TSAC + SOSAC > IUSAF | **TSAC + SOSAC > 50%** |

### Key Threshold: TSAC + SOSAC = 50%

This is the **model-level overturn point** where:
- The combined weight of TSAC and SOSAC equals the IUSAF weight
- Stewardship components collectively contribute 50% of allocations
- The model transitions from "IUSAF-driven" to "stewardship-driven"

**Current Position** (TSAC=5%, SOSAC=3%): IUSAF = 92% — IUSAF remains strongly dominant

**Negotiation Implications**:
- Below 50% combined: IUSAF (inverted UN scale) remains the primary equity basis
- Above 50% combined: Stewardship (land area + SIDS status) becomes the primary allocation driver
- At 50%: Equal contribution from equity and stewardship perspectives

### Decision Boundary Summary

| Boundary | TSAC | SOSAC | IUSAF | Interpretation |
|----------|------|-------|-------|----------------|
| **Lower: Strict Balance** | 1.5% | 3% | 95.5% | All Parties have IUSAF > TSAC component |
| **Upper: Model Overturn** | TSAC+SOSAC > 50% | | < 50% | Stewardship overtakes IUSAF as model driver |
| **Current Position** | 5% | 3% | 92% | IUSAF strongly dominant |

### Scenario Comparison

| Scenario | TSAC | SOSAC | IUSAF | Gini | Spearman | Band 1 ($m) | SIDS ($m) | LDC ($m) | Other ($m) | Total ($m) |
|----------|------|-------|-------|------|----------|-------------|-----------|----------|-----------|------------|
| Pure IUSAF | 0% | 0% | 100% | 0.0873 | 1.0000 | $8.53m | $304.6m | $339.9m | $414.0m | $1000.0m |
| Strict | 1.5% | 3% | 95.5% | 0.0933 | 0.9514 | $8.69m | $321.1m | $333.9m | $406.3m | $1000.0m |
| Bounded | 3.5% | 3% | 93.5% | 0.0851 | 0.9167 | $8.53m | $315.4m | $332.3m | $412.5m | $1000.0m |
| Even | 5.0% | 3% | 92.0% | 0.0829 | 0.8520 | $8.41m | $311.0m | $331.1m | $417.2m | $1000.0m |

**Note on the Spearman 0.85 threshold**: The 0.85 Spearman threshold used to constrain the Gini-minimum point is a design parameter, not an empirically derived boundary. Empirical analysis found no observable structural change at ρ = 0.85; the clearest breakpoint is the band-order overturn at ρ ≈ 0.93 (TSAC = 3.0%). See `docs/spearman-threshold-assessment.md` for full assessment. This threshold will be replaced by a multi-criterion approach (Option D) in a future branch. Figures that visualised the 0.85 threshold as a meaningful boundary have been moved to `deprecated/spearman-0.85-threshold/`.

**Notes**:
- Band 1 shows per-party allocation (average)
- SIDS and LDC overlap (some Parties are both); Other excludes double-counting
- Total confirms allocations sum to $1 billion

### Transfer Scale: Perspective for Negotiations

**Key Insight**: The stewardship adjustments involve relatively small transfers of money.

| Scenario | Amount 'In Play' | % of Fund | Largest Transfer | Mean % Change |
|----------|------------------|-----------|------------------|---------------|
| Strict | $42.6m | 4.3% | $1.7m (China) | 4.6% |
| Bounded | $51.5m | 5.2% | $4.1m (China) | 6.4% |
| Even | $59.9m | 6.0% | $5.8m (China) | 7.8% |

**"Amount In Play"** = Sum of all transfers (both gains and losses). This represents the total amount being reallocated from the Pure IUSAF baseline.

**At Even Scenario (TSAC=5%, SOSAC=3%):**
- Only **6%** of the fund is being transferred
- **94%** of allocations remain unchanged from the Pure IUSAF baseline
- **73 parties (51%)** see less than 5% change in their allocation
- **Only 6 parties** see transfers larger than $1m

**Perspective: What do these numbers mean?**

| Transfer Size | As % of \$1bn Fund | Perspective |
|---------------|-------------------|-------------|
| \$1 million | 0.1% | Equivalent to 0.1 cents on a dollar |
| \$0.5 million | 0.05% | Half of 0.1 cents on a dollar |
| \$0.1 million | 0.01% | One-hundredth of a cent on a dollar |

**For Negotiations**: The stewardship debate centers on reallocating approximately **\$40-60 million** of a **\$1 billion fund** (4-6%). The remaining 94-96% of allocations are not disputed. Most parties see changes of less than \$0.5 million in their indicative allocation.

### Allocation Transfers by Band

| Band | Pure IUSAF | Strict | Bounded | Even |
|------|------------|--------|---------|------|
| Band 1 (≤0.001%) | $264.3m | +$5.2m | +$0.3m | -$3.5m |
| Band 2 (0.001-0.01%) | $435.9m | -$6.5m | -$9.1m | -$11.0m |
| Band 3 (0.01-0.1%) | $187.6m | -$3.0m | -$3.6m | -$4.1m |
| Band 4 (0.1-1.0%) | $97.2m | +$0.6m | +$3.3m | +$5.3m |
| Band 5 (1.0-10.0%) | $12.8m | +$2.0m | +$5.1m | +$7.5m |
| Band 6 (>10.0%) | $2.3m | +$1.7m | +$4.1m | +$5.8m |
| **TOTAL** | **$1000.0m** | **$0.0m** | **$0.0m** | **$0.0m** |

**Key Insight**: TSAC transfers allocation from Bands 2-3 (mid-tier UN contributors) to Bands 4-6 (large land area countries). The transfer is approximately $15m at Even scenario.

### Individual Party Transfers (Band 2-3)

**Band 2: Largest Transfers**
| Party | Transfer | Notes |
|-------|----------|-------|
| Montenegro | -$0.58m | Largest loss |
| Eswatini | -$0.58m | Large loss |
| D.R. Congo | +$0.86m | Largest gain (large land area) |
| Sudan | +$0.60m | Gains from land area |

**Band 3: Largest Transfers**
| Party | Transfer | Notes |
|-------|----------|-------|
| Lebanon | -$0.49m | Largest loss |
| El Salvador | -$0.49m | Large loss |
| Algeria | +$1.02m | Largest gain (large land area) |
| Libya | +$0.62m | Gains from land area |

**Pattern**: Losers are countries with small land area relative to UN share. Gainers are countries with large land area (TSAC reward).

### Visualizations

Four visualizations showing allocation transfers and perspective:
1. `transfer_scale_perspective.svg` - Shows scale of transfers (key perspective graphic)
2. `band_transfers_diverging.svg` - Diverging bars showing gains/losses by band
3. `band_composition_stacked.svg` - Stacked bars showing band composition per scenario
4. `band_transfers_flow.svg` - Flow diagram showing transfers between bands

1. **Transparency Threshold**: At TSAC + SOSAC = 50%, the model shifts from "IUSAF-equity-driven" to "stewardship-driven". This is a clear, explainable boundary for negotiations.

2. **Current Position**: The default (TSAC=5%, SOSAC=3%) gives IUSAF=92%, meaning IUSAF contributes 92% of the allocation weight — firmly in the "equity-driven" space.

3. **Negotiation Space**: 
   - **Conservative**: TSAC+SOSAC < 20% — IUSAF remains strongly dominant (IUSAF > 80%)
   - **Moderate**: TSAC+SOSAC = 20-40% — Significant stewardship recognition but IUSAF still dominant (IUSAF = 60-80%)
   - **Aggressive**: TSAC+SOSAC > 40% — Approaching model overturn (IUSAF < 60%)
   - **Overturn**: TSAC+SOSAC > 50% — Stewardship overtakes equity (IUSAF < 50%)

---

## Technical Notes

- Uses existing `calculate_allocations()` from `src/cali_model/calculator.py`
- Binary search tolerance: 0.01%
- All allocations based on $1 billion fund size
- High-income countries excluded (except SIDS)
- Band inversion mode for IUSAF
- **Verification**: `test_totals.py` confirms all scenarios sum to $1 billion (±$10,000 rounding tolerance)

## Files Generated

```
band-analysis/break-points/
├── readme.md                    # This documentation
├── analysis.py                  # Main analysis script
├── update_figures.py             # Figure generation script
├── test_all_calculations.py      # Comprehensive verification tests
├── figures/
│   ├── transfer_scale_summary.svg   # KEY: Amount in play at different fund sizes
│   ├── band_transfers.svg           # Band-level gains/losses by scenario
│   ├── scenario_comparison.svg      # Key metrics across scenarios
│   ├── negotiation_space.svg       # Model-level thresholds
│   └── party_distribution_heatmap.svg  # Heatmap of allocations by scenario
└── scenario_results/
    ├── pure_iusaf.csv
    ├── strict.csv
    ├── bounded.csv
    └── even.csv
```

---

*Generated on 2026-04-08 - Exploratory analysis for `middle-dist` branch*
