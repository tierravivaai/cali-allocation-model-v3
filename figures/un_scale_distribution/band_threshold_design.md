# IUSAF Band Threshold Design: Log10 Progression Rationale

## Current design

The IUSAF band thresholds follow a **log10 progression** — each boundary is 10× the previous one:

| Band | Threshold range | Weight |
|------|----------------|--------|
| Band 1 | ≤ 0.001% | 1.50 |
| Band 2 | 0.001–0.01% | 1.30 |
| Band 3 | 0.01–0.1% | 1.10 |
| Band 4 | 0.1–1% | 0.95 |
| Band 5 | 1–10% | 0.75 |
| Band 6 | > 10% | 0.40 |

Band 6 was introduced to separate China (~20%) from Brazil, India, Mexico (~1–1.4%). See `config/un_scale_bands.yaml` for the full design notes.

## Why log10

1. **Intuitive** — Each band is a clear order of magnitude. Negotiators and readers can grasp "0.001% to 0.01%" more readily than "0.003% to 0.042%".
2. **Matches the distribution** — UN Scale shares genuinely span 4+ orders of magnitude (0.001% to 20%). A linear split would place 90% of parties in a single band.
3. **Natural scale for inversion** — The IUSAF formula is `1 / un_share`. In log-space, inversion is a sign reversal, so log10-spaced bands treat the inversion symmetrically.
4. **No subjective judgement calls** — The boundaries are determined by the data's own orders of magnitude, not by where an analyst decides to draw lines.
5. **Institutional alignment** — The 0.001% boundary coincides with the UN's own minimum assessment rate. The 0.01% boundary aligns with the UN LDC ceiling. No other progression shares this property.

## Alternative approaches considered

### Quantile-based (equal group sizes)

Split so each band contains roughly the same number of parties (~24 per band for 142 eligible).

| Pro | Con |
|-----|-----|
| Equal group sizes | Bands lose interpretive meaning — a range of "0.003–0.007%" is not negotiable language |
| No band dominates by count | Thresholds shift every time the Party list changes |
| | Does not align with any UN institutional categories |

### Jenks natural breaks

Statistical optimisation to find natural clustering in the distribution (minimising within-band variance, maximising between-band variance).

| Pro | Con |
|-----|-----|
| Captures actual gaps in the data | Thresholds become arbitrary numbers (e.g., 0.003%, 0.042%, 0.8%) |
| Data-driven | Not intuitive — cannot be explained as "order of magnitude" |
| | Thresholds shift with every UN reassessment as the distribution changes |
| | No institutional grounding |

### UN official categories

Use the UN's own breakpoints: minimum rate (0.001%), LDC ceiling (0.01%), low-income threshold.

| Pro | Con |
|-----|-----|
| Grounded in UN practice | Only 2–3 official breakpoints — insufficient for 6 bands |
| Defensible in negotiations | Would require inventing additional thresholds for the upper bands |
| | Upper bands (1%, 10%) have no UN institutional counterpart |

### Shifted log10

Same 10× ratio but offset, e.g., 0.002%, 0.02%, 0.2%, 2%, 20%.

| Pro | Con |
|-----|-----|
| Reduces exact-threshold cases at 0.001% and 0.01% | Less intuitive — "0.002%" has no institutional meaning |
| | Creates new edge cases at different values |
| | Loses alignment with UN minimum rate (0.001%) and LDC ceiling (0.01%) |

## The exact-threshold problem

Under the current log10 boundaries, **39 parties sit exactly on 0.001% or 0.01%** (28 at 0.001%, 11 at 0.01%). Under the model's rule (`min_threshold < share <= max_threshold`), these parties remain in the lower band, but any upward revision would move them.

This is sometimes cited as a weakness of log10 thresholds. However:

- Shifting thresholds (e.g., to 0.002%) moves some exact-threshold parties but creates new edge cases at different values.
- The 0.001% and 0.01% boundaries coincide with the UN's own minimum rate and LDC ceiling, so the exact-threshold clustering reflects a real feature of the UN assessment structure, not an artefact of the band design.
- Historical analysis (`band-analysis/historical_band_mobility.md`) shows that exact-threshold status does not automatically imply near-term band movement — it indicates sensitivity to design, not instability.

## On the weights

The band weights (1.50, 1.30, 1.10, 0.95, 0.75, 0.40) are a **policy lever**, not a mathematical necessity. The only hard constraint is **monotonicity**: every party in a lower-numbered band must receive more than every party in a higher-numbered band.

The key design choice is the **gradient** — how steeply weights fall from Band 1 to Band 6:

| Gradient | Band 1 weight | Band 6 weight | Ratio (Band 1 / Band 6) | Character |
|----------|-------------|-------------|------------------------|-----------|
| Compressed | 1.30 | 0.60 | 2.17× | More equal between bands; smaller inversion effect |
| **Current** | **1.50** | **0.40** | **3.75×** | **Moderate gradient** |
| Steep | 1.80 | 0.20 | 9.00× | Strong inversion effect; Band 1 receives far more than Band 6 |

The current gradient (3.75×) was chosen so that Band 1 LDCs receive approximately twice what Band 5 countries (Brazil, India, Mexico) receive, and approximately 3.75× what China receives. The Band 6 weight of 0.40 places China at ~53% of the Band 5 per-country allocation, reflecting the ~18-fold difference in their UN assessments while preserving a meaningful non-zero floor.

Any monotonic weight sequence is defensible; the specific values are a matter for negotiation, not mathematical proof.

## Source

- Band configuration: `config/un_scale_bands.yaml`
- Threshold stability analysis: `band-analysis/band_crossover_risk.md`
- Historical mobility: `band-analysis/historical_band_mobility.md`
- Near-term movement: `band-analysis/near_term_band_movement_note.md`
