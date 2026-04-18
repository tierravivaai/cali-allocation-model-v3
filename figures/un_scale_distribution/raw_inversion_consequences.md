# Raw Inversion Consequences: Concentration of IUSAF Shares

## The Claim

> "90 Parties to the Convention are assessed under the 0.001 per cent and that under raw inversion, each of those Parties would receive approximately 1.07 per cent of the fund, collectively absorbing over 96 per cent of the total."

## Verification

The claim is **substantially correct** but requires a clarification: the 90 Parties are assessed at **≤ 0.01%** (not 0.001% exactly). They span Band 1 (≤ 0.001%) and Band 2 (0.001–0.01%).

### Party counts

| Assessment range | 142 eligible Parties | 193 UN member states |
|-----------------|---------------------|-----------------------|
| ≤ 0.001% (Band 1) | 31 (incl. 3 at 0%) | 32 |
| 0.001–0.01% (Band 2) | 59 | 59 |
| **≤ 0.01% (Bands 1+2)** | **87** | **90** |

The "90 Parties" figure corresponds to all 193 UN member states assessed at ≤ 0.01%. For the 142 eligible CBD Parties (High income excluded, SIDS preserved), the equivalent count is 87.

### IUSAF share per party

Under raw inversion (`inv_weight = 1 / (un_share / 100)`, normalised), the per-party IUSAF share varies by assessment level:

| UN share | IUSAF share per party (142 eligible) | Count | Collective |
|----------|--------------------------------------|-------|------------|
| 0.001% | 2.32% | 28 | 65.08% |
| 0.002% | 1.16% | 9 | 10.46% |
| 0.003% | 0.77% | 7 | 5.42% |
| 0.004% | 0.58% | 7 | 4.07% |
| 0.005% | 0.46% | 8 | 3.72% |
| 0.006% | 0.39% | 5 | 1.94% |
| 0.007% | 0.33% | 6 | 1.99% |
| 0.008% | 0.29% | 4 | 1.16% |
| 0.009% | 0.26% | 2 | 0.52% |
| 0.010% | 0.23% | 11 | 2.56% |

### Collective absorption

| Group | Parties | Average per-party share | Collective share |
|-------|---------|------------------------|------------------|
| 142 eligible Parties, ≤ 0.01% | 87 | 1.11% | **96.91%** |
| 193 UN members, ≤ 0.01% | 90 | 1.07% | **95.91%** |

### Conclusion

The claim is accurate in substance:

- **"90 Parties assessed at 0.001%"** — should read "≤ 0.01%". The 90 figure matches all UN member states in Bands 1 and 2.
- **"Each receives ~1.07%"** — the average across the 90 is 1.07% (193 members) or 1.11% (142 eligible). This is a weighted average; the smallest contributors (0.001%) receive 2.32% each, while those at 0.01% receive 0.23% each.
- **"Collectively absorbing over 96%"** — confirmed at 95.91% (193 members) or 96.91% (142 eligible).

## The Policy Problem

Raw inversion (`1 / un_share`) produces an extreme concentration: the smallest UN contributors — mostly LDCs and SIDS — absorb virtually the entire fund, leaving only ~3–4% for the remaining 52–55 Parties with larger UN assessments.

This is the mathematical driver for:

1. **Band inversion** — Grouping parties into bands with assigned weights moderates the extreme inversion gradient. Band 1 (weight 1.50) receives 3.75× more per party than Band 6 / China (weight 0.40), compared to the ~2,000× ratio under raw inversion.

2. **TSAC blending** — The territorial stewardship component (beta) provides an alternative allocation pathway for larger countries that would otherwise receive negligible amounts under pure IUSAF.

3. **SOSAC blending** — The SIDS equal-share component (gamma) ensures SIDS receive a baseline allocation regardless of their UN assessment, including zero-rated parties like Cook Islands and Niue.

## Source data

- UN Scale of Assessment 2027: `data-raw/UNGA_scale_of_assessment.csv`
- Band configuration: `config/un_scale_bands.yaml`
- Computation: `figures/un_scale_distribution/generate_plots.py` → `compute_raw_inversion()`
