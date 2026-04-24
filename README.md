# Cali Fund Allocation Model (Inverted UN Scale Option)

An interactive policy-support tool for biodiversity fund allocation under the CBD Cali Fund. The model uses the inverted UN Scale of Assessments (IUSAF) with optional stewardship overlays (TSAC, SOSAC) to compute indicative allocations for CBD Parties.

## The Formula

**Final Share = (1 − β − γ) × IUSAF + β × TSAC + γ × SOSAC**

- **IUSAF**: Inverted UN Scale — the equity base, tilted towards lower-income and LDC countries.
- **TSAC**: Terrestrial Stewardship — proportional to land area (km²).
- **SOSAC**: SIDS Ocean Stewardship — equal-share pool for eligible SIDS.
- **β, γ**: User-adjustable overlay weights. **The central policy question is where to set the balance between the equity base and the stewardship overlays.**

→ Full methodology: [reference/methodology.md](reference/methodology.md)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main negotiation app
streamlit run src/app.py

# Run the sensitivity/robustness app
streamlit run src/sensitivity.py

# Run the experimental banded TSAC variant (terrestrial branch)
streamlit run src/banded_app.py --server.port 8502
```

## Repository Structure

```
├── src/                          # Application and model code
│   ├── app.py                    # Main Streamlit negotiation app
│   ├── sensitivity.py            # Sensitivity analysis & reporting app
│   ├── banded_app.py             # Experimental banded TSAC variant (terrestrial branch)
│   └── cali_model/              # Core calculation library
│       ├── calculator.py         # calculate_allocations() and aggregation functions
│       ├── data_loader.py         # DuckDB-based ETL (raw data → base_df)
│       ├── balance_analysis.py   # Fine sweeps, Gini-minimum identification
│       ├── sensitivity_metrics.py # Gini, Spearman, component ratios
│       ├── sensitivity_scenarios.py # Scenario definitions and two-way grids
│       └── reporting.py          # Markdown/CSV export generation
│
├── tests/                        # Pytest suite (178+ tests)
│   ├── test_logic.py             # Party count, inversion, allocation sums
│   ├── test_band_inversion.py    # Band assignment and weight validation
│   ├── test_tsac_sosac.py       # Component blending and isolation
│   ├── test_totals.py            # Aggregation (region, income, LDC, SIDS)
│   ├── test_floor_ceiling.py     # Constraint redistribution
│   ├── test_equality_mode.py    # Equality mode switching
│   ├── test_tiny_scenarios.py   # Fund conservation at extreme sizes
│   ├── test_negotiator_dashboard.py # Baseline comparisons
│   ├── test_ui_reset.py         # Preset and reset behaviour
│   └── ...                       # 16 more test modules
│
├── scripts/                      # Standalone generation scripts
│   ├── generate_balance_point_rankings.py  # Balance-point tables
│   ├── generate_optiond_tables.py         # Option D threshold tables
│   ├── generate_tsac_section_draft.py      # TSAC section Word output
│   ├── rank_change_scenarios.py            # Rank-change panel figures
│   ├── csv_to_word_lib.py                 # Word table generation utility
│   └── ...                                 # Cross-check and export scripts
│
├── config/                       # Model configuration
│   └── un_scale_bands.yaml       # 6-band UN scale weights
│
├── data-raw/                     # Source data (CSV/XLSX)
│   ├── UNGA_scale_of_assessment.csv   # UN Scale 2025–2027
│   ├── cbd_cop16_budget_table.csv     # CBD Party list (source of truth)
│   ├── manual_name_map.csv           # Party name concordance
│   ├── CLASS_2025_10_07.xlsx         # World Bank income groups
│   └── ...                           # Land area, EU, UNSD regions
│
├── model-tables/                 # Generated output tables (CSV, DOCX, MD)
├── iplc-developed/               # IPLC developed-country analysis
│   ├── specification.md           # Option 1 & 2 specification
│   ├── iplc-integration-options.md # Structural options (A–D)
│   ├── test_structural_validation.py # 40 structural validation tests
│   └── validation_analysis.md    # Why Option 1 ≈ Option 2
│
├── sensitivity-reports/          # Generated sensitivity outputs
├── band-analysis/                 # Break-point analysis
├── reference/                     # Detailed documentation
│   ├── methodology.md             # Formula, bands, balance points
│   ├── data-sources.md            # Data pipeline and sources
│   └── validation.md              # Test suite and integrity checks
│
├── requirements.txt               # Python dependencies
├── change_log.md                  # Versioned change history
└── AGENTS.md                     # AI agent instructions
```

## Application Layers

### `app.py` — Main Negotiation App

The primary interactive interface for exploring policy scenarios.

**Features:**
- Adjustable fund size ($2m–$10bn), IPLC split (50–80%), TSAC (0–15%), SOSAC (0–10%)
- Five negotiation presets: Equality, Inverted UN Scale, Terrestrial Stewardship, Oceans Stewardship, Gini-minimum point
- Band-based inversion (default) or raw inversion mode
- High-income country exclusion (off by default for equality start)
- Optional floor and ceiling constraints
- **Negotiation Dashboard**: increases/decreases vs baseline, group impact charts, per-country waterfall, stewardship scenario comparison
- Multi-perspective tabs: By Party, By Region, By Income Group, LDC, SIDS, Inversion Comparison
- Plain-language and technical explanation toggles
- Blend warnings when stewardship weights become strong or overriding

### `sensitivity.py` — Sensitivity & Robustness App

Dedicated parameter-sweep and reporting interface for reviewers and statisticians.

**Features:**
- Coarse (TSAC×SOSAC, 11×16 = 176 scenarios) and fine (21×21 = 441 scenarios) grids
- Per-scenario Gini coefficient, Spearman ρ vs pure IUSAF, band-order preservation, TSAC/IUSAF ratios
- Balance-point identification (Gini-minimum subject to structural constraints)
- Integrity checks export (`integrity_checks.csv`)
- Markdown summary generation
- Named balance-point scenarios: `gini_minimum`, `band_order_overturn`, `stewardship_forward`

### `banded_app.py` — Experimental Banded TSAC Variant

**Available on the `terrestrial` branch only.** A parallel app using `tsac_mode="banded"` (log₁₀ land-area bands with geometric_base_2 weights) instead of linear land area. Extended sliders (0–30%), three balance-point presets (Strict, Gini-minimum, Boundary), and a Spearman-based overlay warning. See [banded_app_spec_v3.md](../banded_app_spec_v3.md) for details.

## Balance Points (v4.0)

The v4.0 methodology replaces the arbitrary Spearman ρ ≥ 0.85 threshold with **band-order preservation** (Band 5 mean > Band 6 mean) plus a Spearman safety floor of 0.80. Key reference points at SOSAC=3%:

| Point | TSAC | Gini | Spearman ρ | Definition |
|-------|------|------|-----------|-----------|
| Gini-minimum | 2.5% | 0.0886 | 0.945 | Lowest Gini preserving band order |
| Band-order overturn | 3.0% | — | 0.93 | Band 6 overtakes Band 5 |
| Stewardship-forward | 5.0% | — | — | Exploratory reference |

→ Full stewardship design: [reference/methodology.md](reference/methodology.md)

## Data Sources

| Source | Purpose |
|--------|---------|
| UN Scale of Assessments (2025–2027) | Assessed budget shares per Party |
| CBD COP16 Budget Table | Source of truth for 196 CBD Parties |
| UNSD M49 | Region, sub-region classifications |
| World Bank Income Classification | Income group labels |
| World Bank Land Area (FAOSTAT) | Terrestrial stewardship weights |

→ Full data pipeline: [reference/data-sources.md](reference/data-sources.md)

## Testing

```bash
# Run full test suite (178+ tests)
pytest tests/ -v

# Run IPLC structural validation (40 tests)
pytest iplc-developed/test_structural_validation.py -v

# Run with coverage
pytest tests/ --cov=src/cali_model --cov-report=term-missing
```

→ Full test catalog: [reference/validation.md](reference/validation.md)

## Branch Structure

| Branch | Status | Description |
|--------|--------|-------------|
| `main` | Active | Production code, 178+ tests, app.py + sensitivity.py |
| `terrestrial` | Parked | Banded TSAC variant (banded_app.py), calibration harness, v4.2 sensitivity reports |

Archived/deleted branches: `iplc` (merged to main), `optiond` (merged to main as v4.0).

## IPLC Developed-Country Analysis

The `iplc-developed/` directory contains a paper-exercise calculating IPLC allocations for 9 developed countries (Australia, Canada, Denmark, Finland, Japan, New Zealand, Norway, Russia, Sweden) under two hypothetical scenarios:

- **Option 1**: Raw equality for all Parties, filtered to the 9 countries (IPLC ≈ 2.30% of fund).
- **Option 2**: Banded IUSAF with the 9 countries added to Bands 4–5 (IPLC ≈ 2.11% of fund).

The closeness of these results is structurally expected: Band 4 countries gain relative to equality while Band 5 countries lose, and the effects partially cancel. See [iplc-developed/validation_analysis.md](iplc-developed/validation_analysis.md).

Four structural integration options (A–D) are analysed in [iplc-developed/iplc-integration-options.md](iplc-developed/iplc-integration-options.md). Option D (unified pool with State-component return) is recommended.

## Version History

See [change_log.md](change_log.md) for the full versioned history. Key milestones:

- **v3**: 6-band IUSAF, Gini reporting, balance-point analysis, 138 tests
- **v4.0**: Band-order preservation replaces Spearman 0.85 threshold, gini_optimal → gini_minimum rename
- **v4.1**: Balance-point ranking tables, IPLC developed-country tables, DuckDB fix
- **v4.2**: Banded TSAC app, calibration harness, v4 sensitivity reports (terrestrial branch)
- **v4.2.1**: DuckDB StringDtype fix on main, IPLC structural validation (40 tests)

## Use of AI

The code base is written in Python using Factory AI Droid as the development harness. Current main coding model: GLM-5 (Z.ai). High-level reasoning through Opus 4.6–4.7 and GPT-5.4 Codex. Code planning and automated peer review uses GPT-5 Codex, Claude Opus 4.6, and Gemini Pro. Independent review sessions with clean context are preferred. The responsible human is Dr. Paul Oldham.
