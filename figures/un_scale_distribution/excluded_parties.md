# Zero-Rated Parties and the Division-by-Zero Problem

## Issue

Three CBD Parties have a 0% share on the UN Scale of Assessments (2027) because they are not UN member states and therefore do not contribute to the UN budget:

| Party | Status | WB Income Group | SIDS | Land Area (km²) | CBD Budget Share |
|-------|--------|----------------|------|-----------------|-----------------|
| State of Palestine | UN non-member observer state | Lower middle income | No | 6,020 | 0.014% |
| Cook Islands | Free association with New Zealand | High income | Yes | 236 | 0.001% |
| Niue | Free association with New Zealand | High income | Yes | 260 | 0.001% |

All three are eligible CBD Parties under the model's filter (High income excluded, SIDS preserved). All three have 0% on the UN Scale. The IUSAF formula (`1 / un_share`) requires dividing by zero for these parties, which is mathematically undefined.

---

## Model Behaviour

The model's `raw_inversion` logic in `calculator.py` handles this by excluding zero-share parties from the IUSAF weight computation:

```python
mask = calc_df["eligible"] & (calc_df["un_share"] > 0) & (calc_df["un_share"].notna())
```

Zero-share parties receive `iusaf_share = 0.0` by default. This is mathematically correct but creates an asymmetry in allocation outcomes.

### Allocation under pure IUSAF (no blending, 200M fund)

| Party | IUSAF Share | TSAC Share | Final Share | Allocation (USD) |
|-------|-------------|------------|-------------|------------------|
| State of Palestine | 0.0000 | 0.0001 | 0.0000 | 0.00 |
| Cook Islands | 0.0000 | 0.000003 | 0.0000 | 0.00 |
| Niue | 0.0000 | 0.000003 | 0.0000 | 0.00 |

All three receive effectively zero under pure IUSAF.

### Allocation under blended formula (beta=0.15, gamma=0.10, 200M fund)

| Party | IUSAF | TSAC | SOSAC | Final Share | Allocation (USD) |
|-------|-------|------|-------|-------------|------------------|
| State of Palestine | 0 | 0.0023 | **0** | 0.000012 | **0.00** |
| Cook Islands | 0 | 0.000003 0.026 | 0.0026 | **0.51** |
| Niue | 0 | 0.000003 | 0.026 | 0.0026 | **0.51** |

---

## The Political Problem

The asymmetry creates a three-tier outcome among zero-rated Parties:

1. **Cook Islands & Niue** (SIDS) — IUSAF = 0, but SOSAC provides an equal-slice pathway (~0.51 USD each at 200M fund). Small but non-zero.

2. **State of Palestine** (not SIDS) — IUSAF = 0, SOSAC = 0 (not SIDS-eligible), only a negligible TSAC component from land area (6,020 km²). Receives effectively **zero** allocation under any parameter setting.

The median allocation among eligible Parties is ~0.83 USD. Palestine receives 0.0023 USD — approximately **0.3% of the median**. It is an eligible Party on paper but structurally excluded from meaningful allocation by the mathematics of the model.

This is not a policy choice but a mathematical consequence: `1 / 0` is undefined, and Palestine lacks the SIDS flag that would provide an alternative pathway through SOSAC.

---

## Possible Approaches for Discussion

1. **Minimum floor** — Apply a small minimum allocation floor (e.g., 0.001%) to all eligible Parties, ensuring no eligible Party receives zero regardless of UN share.

2. **CBD Budget Scale as proxy** — All three parties contribute to the CBD budget on their own scale. Use the CBD Scale (where Palestine = 0.014%, Cook Islands/Niue = 0.001%) as a substitute for the UN Scale when `un_share == 0`.

3. **Band inversion default** — Under `band_inversion` mode, parties with `un_share == 0` already receive a band weight (Band 1). This naturally resolves the zero-division issue. If band inversion becomes the default mode, the problem is addressed structurally.

4. **Explicit SOSAC expansion** — Extend SOSAC eligibility beyond SIDS to include all zero-rated Parties, ensuring no eligible Party falls through all three components.

5. **Flag as known limitation** — Document that zero-rated non-SIDS parties receive near-zero allocation, and that this is a known consequence of the inversion mechanism requiring policy guidance.

---

## Current Status

This issue is documented for discussion. No code changes have been made. The model's current behaviour (iusaf_share = 0 for zero-share parties) is mathematically correct but may require policy input on whether a floor or proxy mechanism is appropriate.
