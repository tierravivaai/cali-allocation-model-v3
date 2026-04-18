---
output:
  word_document: default
  html_document: default
---
# Rationale for the IUSAF Allocation Model Components

## Mandate and Component Order

COP Decision 16/2 (Annex, paras 1 and 18) establishes that the Cali Fund shall allocate resources in a "fair, equitable, transparent, accountable and gender-responsive manner" and, in particular, that:

> "Funding should support the realization of the objectives of the Convention in developing country Parties, **in particular the least developed countries and small island developing States**, and Parties with economies in transition, especially the conservation and sustainable use of biodiversity, including through the delivery of activities described in **national biodiversity strategies and action plans**."

This single sentence contains three distinct mandates, each of which corresponds to a component of the allocation formula:

`Final Share = (1 - β - γ) × IUSAF + β × TSAC + γ × SOSAC`

The components are ordered as the mandate itself orders them:

1. **IUSAF** — responds to the mandate for developing country Parties, in particular LDCs. The inversion of the UN Scale of Assessments naturally directs funding to those with the lowest economic capacity.
2. **SOSAC** — responds to the "in particular… small island developing States" clause. A targeted adjustment for SIDS, designed and calculated first.
3. **TSAC** — responds to the mandate for "activities described in national biodiversity strategies and action plans," which implicates terrestrial stewardship responsibilities proportional to geographic scale. Designed and calculated second; has the larger quantitative impact on the model.

The design sequence follows the mandate: IUSAF establishes the equity base, SOSAC addresses the SIDS-specific clause, and TSAC addresses the stewardship/NBSAP clause. This ordering also reflects the historical development of the model — SOSAC was introduced before TSAC because the SIDS clause is more precisely targeted than the stewardship mandate.

---

## 1. IUSAF: Inverted UN Scale of Assessment Foundation

The UN Scale of Assessments allocates UN budget contributions proportional to economic capacity. Inverting this scale (1 / un_share) produces a distribution that favours the poorest countries — directly satisfying the mandate for developing country Parties and, in particular, LDCs.

Raw inversion creates extreme concentration. Band-based inversion (IUSAF) groups Parties into six share bands and assigns weights that smooth the distribution while preserving the equity direction. The band weights are:

| Band | UN Share Range | Weight | n Parties |
|------|---------------|--------|-----------|
| Band 1 | ≤ 0.001% | 1.50 | ~31 |
| Band 2 | 0.001% – 0.01% | 1.30 | ~34 |
| Band 3 | 0.01% – 0.1% | 1.10 | ~28 |
| Band 4 | 0.1% – 1.0% | 0.95 | ~18 |
| Band 5 | 1.0% – 10.0% | 0.75 | 3 |
| Band 6 | > 10.0% | 0.40 | 1 (China) |

IUSAF is the dominant component of the allocation formula. At the Gini-minimum setting (TSAC = 5%, SOSAC = 3%), IUSAF contributes 92% of the allocation weight.

**Key insight from raw inversion**: Biodiversity-rich middle-income countries and SIDS have very low shares on the UN Scale — because the scale measures economic capacity, not stewardship responsibility. This insight motivated the introduction of SOSAC and TSAC as corrective overlays.

### SIDS Distribution Across Bands

Of the 39 eligible SIDS Parties, the majority (22 of 39) fall into Band 1 (UN share ≤ 0.001%), meaning they already receive the highest IUSAF allocation per Party. However, 17 SIDS fall into Bands 2–4, where their IUSAF allocations are progressively lower:

| Band | UN Share Range | n SIDS | Avg IUSAF Allocation (USD M) | SOSAC Impact at SOSAC = 3% |
|------|---------------|--------|------------------------------|------------------------|
| Band 1 | ≤ 0.001% | 22 | 8.53 | 9.0% of IUSAF |
| Band 2 | 0.001% – 0.01% | 11 | 7.39 | 10.4% of IUSAF |
| Band 3 | 0.01% – 0.1% | 4 | 6.25 | 12.3% of IUSAF |
| Band 4 | 0.1% – 1.0% | 2 | 5.40 | 14.2% of IUSAF |

This distribution is significant for the SOSAC rationale: the 17 SIDS in Bands 2–4 receive lower IUSAF allocations and therefore benefit proportionally more from the SOSAC uplift. At SOSAC = 3%, SOSAC constitutes 10–14% of the IUSAF baseline for these SIDS — crossing the double-digit threshold that marks a substantive recognition. For the 22 Band 1 SIDS, SOSAC approaches but does not quite reach 10% of IUSAF (9.0%), which is appropriate given that their IUSAF allocations are already the highest.

---

## 2. SOSAC: SIDS Ocean Stewardship Allocation Component

### Mandate Basis

The COP mandate specifies "in particular… small island developing States." SOSAC operationalises this clause by directing a configurable weight toward all eligible SIDS on an equal-share basis.

### Design Logic

SOSAC allocates its weight equally among eligible SIDS Parties (1/n, where n = number of eligible SIDS) rather than proportionally to marine area or EEZ size. This design choice rests on three grounds:

1. **Simplicity and transparency**: Equal shares avoid the contestable calculations and data-quality issues inherent in EEZ or marine-area measurement.
2. **Equity among SIDS**: An equal-share approach prevents larger archipelagic SIDS from capturing disproportionate SOSAC weight at the expense of smaller island states — consistent with the model's equity foundations.
3. **Policy legibility**: Negotiators can understand and verify the SOSAC allocation without specialised geographic data.

### Why SOSAC = 3%

The fund size is USD 1,000 M and there are 39 eligible SIDS. At each integer percentage:

| SOSAC | SOSAC Pool (USD M) | Per SIDS (USD M) | SOSAC as % of IUSAF (Band 1) | SOSAC as % of IUSAF (Band 2+) |
|---|---|---|---|---|
| 1% | 10.0 | 0.256 | 3.0% | 3.5–4.7% |
| 2% | 20.0 | 0.513 | 6.0% | 6.9–9.5% |
| **3%** | **30.0** | **0.769** | **9.0%** | **10.4–14.2%** |
| 4% | 40.0 | 1.026 | 12.0% | 13.9–19.0% |
| 5% | 50.0 | 1.282 | 15.0% | 17.4–23.7% |

At SOSAC = 1% and SOSAC = 2%, the SOSAC component represents less than 10% of the IUSAF baseline for every SIDS band. The uplift is present but arguably too modest to constitute a substantive recognition of the "in particular" mandate.

**SOSAC = 3% is the minimum integer percentage at which SOSAC first reaches a double-digit share of IUSAF (~10%) for SIDS Parties in Bands 2 and above, and approaches 10% even for Band 1 SIDS (9.0%).** This is the minimum integer threshold at which the SOSAC uplift can be characterised as a meaningful — while still clearly modest and non-dominant — recognition of SIDS stewardship responsibilities.

### Constraint Verification

At SOSAC = 3%:

- **IUSAF dominance**: With TSAC = 5% and SOSAC = 3%, combined stewardship is 8%. IUSAF contributes 92% — firmly in the "equity-driven" space.
- **Far from overturn**: The SOSAC analytical balance point is approximately SOSAC ≈ 17.4%. The current setting is 5.8× below this threshold.

### Effect on Country Rankings

SOSAC at 3% does not merely add a token amount — it produces a substantive but modest change in the country rankings. The Spearman rank correlation between pure IUSAF and SOSAC-only (TSAC = 0%, SOSAC = 3%) is ρ = 0.977, which is well above the model's 0.85 threshold for "recognisably the same rank order." However, 39 parties (all SIDS) experience a rank shift relative to pure IUSAF.

The mechanism is as follows: under pure IUSAF, the 22 Band 1 SIDS are tied at identical allocations (USD 8.53M each). The equal-share SOSAC increment of USD 0.769M breaks some of these ties by pushing SIDS above non-SIDS parties that were previously at the same IUSAF level. The rank changes are concentrated among SIDS and their immediate neighbours in the ranking; non-SIDS parties are unaffected in their relative ordering.

This ranking effect is contextually relevant: it demonstrates that SOSAC = 3% is large enough to be visible in the allocation rankings, not just in the allocation amounts. The double-digit SOSAC/IUSAF threshold and the ranking shift are complementary signals that SOSAC = 3% constitutes a substantive — while still clearly modest and non-dominant — recognition.

The ranking impact across all scenarios with SOSAC = 3% is:

| Scenario | Spearman ρ vs Pure IUSAF | Parties with Changed Rank |
|----------|-------------------------|--------------------------|
| Pure IUSAF (reference) | 1.000 | 0 |
| SOSAC only (TSAC = 0%, SOSAC = 3%) | 0.977 | 39 |
| Strict (TSAC = 1.5%, SOSAC = 3%) | 0.951 | 136 |
| Bounded (TSAC = 3.5%, SOSAC = 3%) | 0.917 | 138 |
| Gini-minimum (TSAC = 5%, SOSAC = 3%) | 0.852 | 137 |

The Spearman rank correlation (ρ) measures how closely the country ranking under a given scenario matches the ranking under pure IUSAF. A value of ρ = 1.000 means the rankings are identical (as for pure IUSAF compared with itself). A value of ρ = 0.852 means the rankings remain recognisably similar but have visibly diverged. The model uses ρ > 0.85 as the threshold below which the rank order is no longer considered recognisably the same as the IUSAF baseline.

The ranking impact of SOSAC alone (ρ = 0.977) is substantially smaller than the impact of TSAC at any non-zero setting. This confirms that SOSAC acts as a modest uplift while TSAC is the primary driver of ranking departure from pure IUSAF.

### Characterisation

SOSAC = 3% is the **minimum integer percentage that provides a substantively meaningful SIDS uplift** while preserving IUSAF as the dominant allocation base. It is not analytically "optimal" — it does not minimise Gini, maximise Spearman, or satisfy a balance-point condition. Its grounding is:

1. The COP 16/2 "in particular" mandate for SIDS;
2. The double-digit SOSAC/IUSAF threshold as the minimum integer for substantive recognition;
3. The demonstrable ranking impact (ρ = 0.977) confirming that SOSAC is visible, not merely nominal;
4. The preservation of IUSAF dominance (92% of formula weight) and structural integrity of the model.

---

## 3. TSAC: Terrestrial Stewardship Allocation Component

> **REVIEW NEEDED — Sensitivity Analysis Setups**: The TSAC sensitivity analysis operates under two setups: (a) isolated TSAC with SOSAC = 0%, and (b) TSAC in context with SOSAC = 3%. Threshold values differ between these setups and must not be conflated. The primary analysis (setup b) uses verified data from `tsac_fine_sweep.csv`. Setup (a) requires a dedicated sweep to verify provisional threshold values previously derived from ad hoc runs. See the "Sensitivity Analysis Setups" subsection below for details.

### Mandate Basis

The COP mandate references "activities described in national biodiversity strategies and action plans." Under the Global Biodiversity Framework, Parties have adopted goals and targets and are preparing NBSAPs to implement them. Terrestrial stewardship responsibilities are correlated with geographic scale — larger land areas entail greater stewardship responsibilities and implementation costs for NBSAPs.

TSAC operationalises this mandate by allocating a configurable weight proportional to FAOSTAT land area among eligible Parties.

### Design Logic

TSAC uses the widely available FAOSTAT land-area dataset (AG.LND.TOTL.K2) as its scaling variable. Land area is:

- **Objective and verifiable**: Available from a standard international dataset, not subject to the definitional disputes that affect marine-area measurements.
- **Correlated with stewardship scope**: Larger territories generally entail greater biodiversity stewardship responsibilities and higher NBSAP implementation costs.
- **Simple and transparent**: The proportional allocation is straightforward to compute and explain.

### Why TSAC = 5% (Gini-minimum Setting)

The TSAC weight was determined analytically through a fine-grained sweep (0.5 pp intervals, 0–10%, SOSAC = 3%). The sweep identified three key balance points:

| Point | TSAC | Condition Satisfied | Characterisation |
|-------|---|----|-----------|
| Strict | 1.5% | TSAC/IUSAF ≤ 1.0 for all Parties including China (Band 6) | IUSAF dominant for every Party |
| Bounded | 3.5% | TSAC/IUSAF ≤ 1.0 for Band 5 Parties (Brazil, India, Mexico); exceeded for Band 6 (China) | IUSAF dominant except China |
| Gini-minimum | 5.0% | Minimises Gini coefficient while keeping Spearman > 0.85 vs pure IUSAF | Most equal distribution; does not satisfy balance condition |

The Gini-minimum point (TSAC = 5%) is the default setting in the application. It produces the most equal per-Party distribution measurable by the Gini coefficient, while maintaining a Spearman rank correlation above 0.85 with pure IUSAF — meaning the rank order is recognisably the same as the IUSAF baseline.

**Note**: The Gini-minimum point does not satisfy the TSAC/IUSAF balance condition for China (ratio ≈ 2.87×) or Brazil (ratio ≈ 1.36×). It should not be characterised as a "balanced" setting in that sense. It is the default because it minimises statistical inequality, not because it preserves component dominance.

### Impact Hierarchy

TSAC has a larger quantitative impact on the model than SOSAC because:

- TSAC scales across all eligible Parties (not just SIDS), redistributing weight proportional to land area.
- Large countries (China, Brazil, India, Kazakhstan, Argentina, DRC) receive significant TSAC increments that can shift their rank positions.
- At TSAC = 5%, the TSAC-driven rank changes for large-area countries are the primary source of departure from pure IUSAF.

This is consistent with the mandate structure: the "in particular" SIDS clause is a targeted, bounded recognition (SOSAC), while the NBSAP/stewardship mandate has broader structural implications across all Parties (TSAC).

### Sensitivity Analysis Setups

The TSAC sensitivity analysis uses two distinct setups that must not be conflated:

| Setup | TSAC | SOSAC | Purpose | Source |
|-------|------|-------|---------|--------|
| **a) Isolated TSAC** | Varied 0–10% | 0% | Pure TSAC effect without SOSAC interaction | Not yet generated; previous values from ad hoc runs |
| **b) TSAC in context** | Varied 0–10% | 3% | TSAC effect at the operational SOSAC setting | `sensitivity-reports/v3-sensitivity-reports/tsac_fine_sweep.csv` |

Setup (b) is the primary analysis because it reflects the operational formula where SOSAC = 3%. Setup (a) is useful for understanding TSAC's intrinsic effect in isolation. The threshold values differ between the two setups because SOSAC contributes additional weight to SIDS allocations, slightly shifting the balance points.

> **REVIEW NEEDED**: A dedicated isolated-TSAC sweep (SOSAC = 0%) should be generated to provide verified threshold values for setup (a). The values cited below for the isolated setup are provisional and require confirmation. The existing `tsac_fine_sweep.csv` was generated with SOSAC = 3% and therefore belongs to setup (b) only.

### Effect on Country Rankings (Setup b: SOSAC = 3%)

The TSAC fine sweep (0.5 pp intervals, TSAC 0–10%, SOSAC = 3%) identifies the following thresholds:

**1. China Component Overturn (TSAC ≈ 2.0%)**

At TSAC ≈ 2.0%, the TSAC component equals the IUSAF component for China — meaning China's allocation is equally driven by its land area and its (inverted) UN Scale share. Beyond this point, TSAC dominates for China. This is 25× lower than the simple model overturn threshold (TSAC + SOSAC = 50%).

**2. Brazil Component Overturn (TSAC ≈ 4.0%)**

At TSAC ≈ 4.0%, the TSAC component equals the IUSAF component for Brazil — the first Band 5 Party where TSAC overtakes IUSAF. At this point, both China and Brazil have TSAC-dominant allocations.

**3. Gini-Minimum / Spearman Boundary (TSAC = 5.0%)**

At TSAC = 5.0% (the Gini-minimum setting), the Spearman rank correlation drops to ρ = 0.852 — the threshold currently used as the constraint for the Gini-optimal point identification. This threshold is a design parameter, not an empirically derived breakpoint; no observable structural change in the allocation rankings occurs at or near ρ = 0.85. See `docs/spearman-threshold-assessment.md` for a full assessment. The Gini coefficient reaches its minimum (0.0829) at this point. This is the point of maximum statistical equality and maximum rank departure simultaneously.

**4. Spearman Below Threshold (TSAC > 5.5%)**

At TSAC = 5.5%, the Spearman correlation drops below 0.85 (ρ = 0.822), crossing the design-parameter threshold used in the Gini-optimal constraint. Beyond this point, the allocation rankings diverge further from pure IUSAF. No structural discontinuity marks this boundary — see `docs/spearman-threshold-assessment.md`.

**5. Rank Re-stabilisation (TSAC > ~8%)**

At higher TSAC levels, the Spearman correlation continues to decline rather than re-stabilising (ρ = 0.666 at TSAC = 10%). The non-monotonic re-stabilisation described in earlier analysis (ρ rising back to ~0.950 at TSAC ≈ 9.2%) was observed in the isolated-TSAC setup (a) and does not appear in the contextual sweep (b) with SOSAC = 3%.

The full ranking trajectory at SOSAC = 3% (setup b):

| TSAC | SOSAC | IUSAF % | Spearman ρ | China TSAC/IUSAF | Brazil TSAC/IUSAF | What Happens |
|------|-------|---------|-----------|-----------------|------------------|--------------|
| 0% | 3% | 97% | 0.977 | 0.00 | 0.00 | SOSAC only — modest rank shift among SIDS |
| 1.5% | 3% | 95.5% | 0.951 | 0.83 | 0.39 | Strict — IUSAF dominant for all Parties |
| **2.0%** | **3%** | **95.0%** | **0.948** | **1.11** | **0.53** | **China component overturn — TSAC ≥ IUSAF for China** |
| **4.0%** | **3%** | **93.0%** | **0.898** | **2.27** | **1.08** | **Brazil component overturn — TSAC ≥ IUSAF for Brazil** |
| **5.0%** | **3%** | **92.0%** | **0.852** | **2.87** | **1.36** | **Gini-minimum — Spearman at 0.85 boundary** |
| 5.5% | 3% | 91.5% | 0.822 | 3.17 | 1.51 | Spearman below 0.85 threshold |
| 10.0% | 3% | 87.0% | 0.666 | 6.07 | 2.88 | Rank order no longer recognisably IUSAF-driven |

The ranking trajectory is monotonic within setup (b): Spearman declines steadily as TSAC increases. The policy-relevant range lies between the strict point (TSAC = 1.5%) and the Gini-minimum (TSAC = 5.0%), where the ranking is in active transition from IUSAF-driven to TSAC-influenced but remains recognisably similar to the IUSAF baseline.

### Effect on Country Rankings (Setup a: SOSAC = 0%)

> **REVIEW NEEDED**: The following thresholds are provisional, derived from earlier ad hoc runs. A dedicated isolated-TSAC sweep (SOSAC = 0%) should be generated to verify these values.

The isolated-TSAC analysis (SOSAC = 0%) was used in earlier working papers to understand TSAC's intrinsic effect. The key provisional thresholds are:

**1. Order Overturn (TSAC ≈ 2.95%)**

At TSAC ≈ 2.95%, the IUSAF band ordering is first subverted: China (Band 6, lowest IUSAF weight) receives a higher per-party allocation than Brazil, India, and Mexico (Band 5). Under pure IUSAF, the allocation ordering is strictly monotonic: Band 1 > Band 2 > Band 3 > Band 4 > Band 5 > Band 6. At the order overturn point, Band 6 overtakes Band 5. This is 17× lower than the simple model overturn threshold (TSAC + SOSAC = 50%).

| TSAC Level | Band 6 mean (China) | Band 5 mean (Brazil, India, Mexico) | Order Preserved? |
|------------|---------------------|-------------------------------------|------------------|
| 0% (Pure IUSAF) | USD 2.21M | USD 4.13M | YES |
| 2.5% | USD 5.15M | USD 5.44M | YES (barely) |
| **~2.95%** | **~USD 5.40M** | **~USD 5.40M** | **NO — Band 6 overtakes Band 5** |
| 5.0% (Gini-minimum) | USD 8.09M | USD 6.75M | NO — clearly overturned |

**2. TSAC Component Overturn (TSAC ≈ 9.2%)**

At TSAC ≈ 9.2%, the TSAC component overtakes the IUSAF component for China. In the isolated setup, the Spearman correlation paradoxically rises back to ρ ≈ 0.950 at this point — the ranking re-stabilises around a land-area-driven order rather than fluctuating in the transition zone between IUSAF-driven and TSAC-driven regimes. This non-monotonic pattern is specific to the isolated setup and does not appear when SOSAC = 3%.

---

## Combined Stewardship Position

At the Gini-minimum setting (TSAC = 5%, SOSAC = 3%):

| Component | Weight | Share of Formula |
|-----------|--------|-----------------|
| IUSAF | 92% | Dominant equity base |
| TSAC | 5% | Stewardship correction |
| SOSAC | 3% | SIDS-specific recognition |
| **Total stewardship** | **8%** | **Modest overlay on IUSAF** |

This position is 42 percentage points below the model overturn threshold (TSAC + SOSAC = 50%) and well within the "conservative" negotiation zone (TSAC + SOSAC < 20%).

---

## Threshold Summary

### SOSAC Thresholds (SOSAC sweep: TSAC = 0%)

| Threshold | Value | Condition |
|-----------|-------|-----------|
| SOSAC meaningful uplift | SOSAC ≥ 3% | SOSAC ≥ 10% of IUSAF for Band 2+ SIDS |
| SOSAC ranking impact | SOSAC = 3% | Spearman ρ = 0.977 vs pure IUSAF; 39 parties shift rank |
| SOSAC balance point | SOSAC ≈ 17.4% | SOSAC overtakes IUSAF for most-affected SIDS |

### TSAC Thresholds — Setup b: SOSAC = 3% (primary, verified)

| Threshold | Value | Condition |
|-----------|-------|-----------|
| China component overturn | TSAC ≈ 2.0% | TSAC/IUSAF ≥ 1.0 for China (Band 6) |
| Brazil component overturn | TSAC ≈ 4.0% | TSAC/IUSAF ≥ 1.0 for Brazil (Band 5) |
| TSAC balance (strict) | TSAC ≈ 1.5% | TSAC/IUSAF ≤ 1.0 for all Parties |
| TSAC balance (bounded) | TSAC ≈ 3.5% | TSAC/IUSAF ≤ 1.0 for Band 5 Parties |
| Gini-minimum | TSAC = 5.0% | Minimises Gini, Spearman = 0.852 |
| Spearman below threshold | TSAC = 5.5% | Spearman < 0.85 vs pure IUSAF |

### TSAC Thresholds — Setup a: SOSAC = 0% (provisional, review needed)

> **REVIEW NEEDED**: These values are from ad hoc runs and require verification via a dedicated isolated-TSAC sweep.

| Threshold | Value | Condition |
|-----------|-------|-----------|
| Order overturn | TSAC ≈ 2.95% | Band 6 mean > Band 5 mean (China > Brazil) |
| TSAC component overturn | TSAC ≈ 9.2% | TSAC/IUSAF ≥ 1.0 for China; Spearman re-stabilises at ~0.950 |

### General Thresholds

| Threshold | Value | Condition |
|-----------|-------|-----------|
| Model overturn | TSAC + SOSAC = 50% | Stewardship overtakes IUSAF as dominant driver |

---

## Supporting Analysis and Data Sources

The analysis in this document draws on the following sensitivity analysis reports, datasets, and working documents within this repository. Readers seeking the underlying calculations or wishing to reproduce the results should consult these sources.

### Sensitivity Analysis Reports

| Document | Location | Content |
|----------|----------|---------|
| Break-Points Analysis | `band-analysis/break-points/readme.md` | Full analysis of TSAC and SOSAC overturn points, order overturn, balance points, and negotiation space |
| V3 Sensitivity Reports | `sensitivity-reports/v3-sensitivity-reports/` | Scenario brief, comparative report, technical annex, and balance-point summary |
| Balance-Point Summary | `sensitivity-reports/v3-sensitivity-reports/balance_point_summary.md` | Identified balance points (strict, bounded, Gini-minimum) with component ratios |

### Scenario Datasets

| Dataset | Location | Content |
|---------|----------|---------|
| Pure IUSAF baseline | `band-analysis/break-points/scenario_results/pure_iusaf.csv` | IUSAF-only allocation for 142 eligible Parties |
| Strict scenario | `band-analysis/break-points/scenario_results/strict.csv` | TSAC = 1.5%, SOSAC = 3% |
| Bounded scenario | `band-analysis/break-points/scenario_results/bounded.csv` | TSAC = 3.5%, SOSAC = 3% |
| Gini-minimum scenario | `band-analysis/break-points/scenario_results/even.csv` | TSAC = 5%, SOSAC = 3% |
| TSAC overturn scenario | `band-analysis/break-points/scenario_results/tsac_overturn.csv` | TSAC ≈ 1.8%, SOSAC = 3% (China component overturn with SOSAC active) |
| SOSAC overturn scenario | `band-analysis/break-points/scenario_results/sosac_overturn.csv` | TSAC = 0%, SOSAC ≈ 17.4% |
| TSAC fine sweep (SOSAC = 3%) | `sensitivity-reports/v3-sensitivity-reports/tsac_fine_sweep.csv` | TSAC 0–10% at 0.5 pp intervals, SOSAC held at 3% |
| SOSAC fine sweep (TSAC = 0%) | `sensitivity-reports/v3-sensitivity-reports/sosac_fine_sweep.csv` | SOSAC 0–10% at 0.5 pp intervals, TSAC held at 0% |
| IUSAF ranked by country | `model-tables/iusaf-ranked-country-16042026.csv` | All Parties ranked by IUSAF allocation with bands |
| IUSAF by UN region | `model-tables/iusaf-unregion-15042026.csv` | Regional allocation summary |
| IUSAF by SIDS/LDC panel | `model-tables/iusaf-sids-panel-16042026.csv`, `iusaf-ldc-panel-16042026.csv` | SIDS and LDC group allocations |

### Source Data

| Dataset | Location | Description |
|---------|----------|-------------|
| FAOSTAT Land Area | `data-raw/API_AG.LND.TOTL.K2_DS2_en_csv_v2_749/` | World Bank land area indicator (AG.LND.TOTL.K2) |
| Country Overlay | `data-raw/country_overlay.csv` | CBD Party status, WB income group, land area, EU membership |
| UN Scale of Assessments | `data-raw/un_scale.csv` | UN scale shares for 2025–2027 assessment period |
| UN Classifications | `data-raw/un_classifications.csv` | UN M49 regions, sub-regions, LDC/SIDS/LLDC designations |
| CBD COP16 Budget Table | `data-raw/cbd_cop16_budget_table.csv` | CBD contribution table (authoritative Party list) |
| Band Configuration | `config/un_scale_bands.yaml` | IUSAF band thresholds and weights |

### Working Papers and Figures

| Resource | Location | Content |
|----------|----------|---------|
| Order Overturn Figure | `band-analysis/break-points/figures/order_overturn.svg` | Visualisation of the order overturn threshold |
| Negotiation Space Figure | `band-analysis/break-points/figures/negotiation_space.svg` | All scenarios plotted in conservative zone |
| Break-Points Analysis Script | `band-analysis/break-points/analysis.py` | Python script that computes all balance points and scenarios |
| Break-Points Figure Script | `band-analysis/break-points/update_figures.py` | Generates all break-point visualisations |
| Break-Points Tests | `band-analysis/break-points/test_all_calculations.py` | Verification of all threshold calculations |
| AHTEG Report Structure | `docs/ahteg-report-structure.md` | Outline for the AHTEG presentation of the model |
| Spearman Threshold Assessment | `docs/spearman-threshold-assessment.md` | Origin, empirical assessment, and options for the 0.85 threshold |
| IUSAF Technical Note | `docs/CBD_AHEGF_IUSAF_technical_note.docx` | Technical note submitted to the AHTEG |
| IUSAF Explainer | `docs/Cali_Fund_IUSAF_explainer.docx` | Plain-language explainer of the model |
