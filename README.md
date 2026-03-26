# Cali Fund Allocation Model (Inverted UN Scale Option)

This interactive tool illustrates how Cali Fund allocations would be distributed if based on the **latest UN Scale of Assessments (2025-2027)**, inverted to reflect relative need.

## Features
- **Adjustable Fund Size**: Scale the annual Cali Fund from $0.002bn ($2m) to $10.0bn. Scenario steps at 50, 200, 500, 1 billion
- **IPLC Component**: Set the percentage for Indigenous Peoples & Local Communities (50% to 80%).
- **Multi-perspective views**:
    - Detailed Party-level table.
    - Regional aggregations (UNSD M49).
    - Share by WB Income Group.
    - Developmental groupings (LDC, SIDS).
- **High Income Filter**: Ability to toggle High Income countries out of the allocation pool (off by default on initial load for true-equality start).
- **Transparency**: Toggle "Raw Inversion and Explanation" to see plain language and technical summaries of the methodology.
- **TSAC & SOSAC Components**: Blended allocation formula incorporating land area (TSAC) and SIDS-specific structural adjustment (SOSAC).
- **Stewardship Controls**: Initial load defaults to true equality (`TSAC=0`, `SOSAC=0`). The Gini-Optimal Point preset uses TSAC `0.05` and SOSAC `0.03`, with UI ranges capped at TSAC `0.15` and SOSAC `0.10` so IUSAF remains the dominant base.
- **Blend Warnings**: Live status plus threshold warnings when combined stewardship weights become strong (`>0.15`) or potentially overriding (`>0.20`).
- **Negotiation Dashboard**: Advanced visualizations including increases and decreases analysis, group impact charts, country-level waterfalls, and a selected-country stewardship scenario comparison chart with an equality reference line.

## Installation & Setup

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the applications**:
   ```bash
   streamlit run app.py
   streamlit run sensitivity.py
   ```

`app.py` is the main negotiation/policy interface. `sensitivity.py` is a dedicated robustness-testing and reporting app for parameter sweeps, diagnostics, threshold checks, and markdown/CSV exports including `integrity_checks.csv`.

## Methodology
The allocation sequence is now applied in this order:

1. **Raw inversion (IUSAF raw)**
   - Each eligible Party’s UN assessed share is inverted (`1/share`) and normalised.
   - This is the raw sovereign-capacity baseline and is included for
   transparency.

2. **Banded inversion (IUSAF default)**
   - As an alternative to raw inversion, Parties are grouped into UN-share bands.
   - Band weights are then normalised to form the IUSAF base.
   - This reduces sensitivity to very small share differences while preserving an inverted-capacity logic.
   - This is the default IUSAF baseline

3. **Stewardship adjustments (TSAC and SOSAC)**
   - **TSAC (Terrestrial Stewardship Allocation Component)**: proportional to land area (km²).
   - **SOSAC (SIDS Ocean Stewardship Allocation Component)**: equal-share pool across eligible SIDS.
   - These adjustments are blended on top of the selected IUSAF base using user-adjustable weights ($\beta$ for TSAC and $\gamma$ for SOSAC).

Final share formula:
> **Final Share = (1 - $\beta$ - $\gamma$) * IUSAF + $\beta$ * TSAC + $\gamma$ * SOSAC**

### Stewardship Slider Design
- **Initial app defaults**: TSAC `0.00`, SOSAC `0.00` (true equality start).
- **Gini-Optimal Point preset values**: TSAC `0.05`, SOSAC `0.03`.
- **Allowed range**: TSAC `0.00` to `0.15`; SOSAC `0.00` to `0.10`; step `0.01`.
- **Design intent**: TSAC and SOSAC recognise stewardship and special circumstances, while IUSAF remains the dominant sovereign-capacity base.
- **UI safeguards**:
  - Live blend status is always shown.
  - Mild warning when `TSAC + SOSAC > 0.15`.
  - Strong warning when `TSAC + SOSAC > 0.20`.
  - Hard stop if `TSAC + SOSAC >= 1.0`.

## Data Sources
- **UN Scale of Assessments**: General assembly resolution 79/225.
- **Regions**: UNSD M49 standard.
- **Income Class**: World Bank Country and Lending Groups.
- **Land Area**: World Bank indicator `AG.LND.TOTL.K2` (Land area in sq. km).

## Floor Calculation (Minimum Share per Eligible Country)

Floors and ceilings are currently unused in the model. They 
are provided as options to be used only if necessary. 

### Purpose
The floor sets a minimum percentage of the total fund that each eligible country must receive under the allocation model.

It is designed to prevent extremely small allocations that may be operationally insignificant, particularly when the fund size is large and the inverted UN scale produces very small shares for some countries.

### How It Works
- The model first calculates each eligible country’s share using the inverted UN scale of assessment.
- If a country’s share falls below the selected floor percentage, it is raised to that minimum level.
- The remaining available funds are then redistributed proportionally across the other eligible countries so that total allocations still sum to 100% of the fund.

The floor applies only to eligible countries as defined by the model settings (e.g. exclusion of high-income countries if selected).

### Mathematical Constraint
The maximum feasible floor is determined dynamically by:
> **Maximum floor (%) = 100 ÷ number of eligible countries**

This ensures that the combined minimum shares do not exceed the total fund.
For example:
- If 150 countries are eligible, the maximum feasible floor is 0.67%.
- If 100 countries are eligible, the maximum feasible floor is 1.00%.

The slider is automatically limited to this value to ensure the model remains internally consistent.

### Interpretation
The floor does not represent entitlement or guaranteed disbursement.
It is a modelling parameter that illustrates how a minimum allocation rule would alter the distribution of resources under the inverted UN framework.

## Ceiling Calculation (Maximum Share per Eligible Country)

Floors and ceilings are currently unused in the model. They 
are provided as options to be used only if necessary. 

### Purpose
The ceiling sets a maximum percentage of the total fund that any eligible country may receive.

It is designed to limit concentration of funding among countries with very small UN assessment shares (which receive higher allocations under the inverted model).

### How It Works
- The model first calculates each eligible country’s share using the inverted UN scale.
- If a country’s share exceeds the selected ceiling percentage, it is reduced to that maximum level.
- The remaining funds are redistributed proportionally among the other eligible countries.
- Total allocations always sum to 100% of the fund.

The ceiling applies only to eligible countries under the current model settings.

### Interpretation
The ceiling does not impose a political cap or entitlement rule.
It is a scenario-setting tool that allows users to explore how limiting concentration affects overall distribution patterns.

Lower ceilings produce more even distributions.
Higher ceilings allow stronger differentiation under the inverted UN scale.

### Combined Effect of Floor and Ceiling
When both are enabled:
- Countries below the floor are lifted upward.
- Countries above the ceiling are reduced.
- Remaining funds are redistributed proportionally.
- The total allocation always remains equal to the total fund.

These parameters are illustrative modelling controls intended to explore distributional outcomes under different policy assumptions.

## Validation and Data Integrity

The model undergoes rigorous automated validation to ensure statistical accuracy and completeness. For statisticians and developers, the following checks are enforced on every update:

### 1. Party Count & Alignment
The model is validated against the **CBD COP16 Budget Table** (`cbd_cop16_budget_table.csv`) as the primary source of truth for CBD Parties.
- **Validation Rule**: Exactly **196 Parties** (including the European Union) must be present and correctly mapped.
- **Location**: `tests/test_logic.py` -> `test_cbd_party_count` and `test_budget_table_alignment`.

### 1b. IUSAF Inversion Logic (Raw and Banded)
The model validates both inversion routes used for the IUSAF baseline.
- **Validation Rule (raw inversion path)**: Default inversion path remains numerically consistent in full-allocation tests (sum integrity and eligibility behavior).
- **Validation Rule (banded inversion path)**: Every eligible Party receives a valid band and band weight, and band-based IUSAF shares normalise correctly.
- **Validation Rule (mode consistency)**: Baseline comparisons respect the selected `un_scale_mode`.
- **Location**: `tests/test_tiny_scenarios.py`, `tests/test_band_inversion.py`, and `tests/test_negotiator_dashboard.py::test_un_scale_mode_consistency_in_baseline`.

### 1c. TSAC & SOSAC Component Integrity
New tests verify the blending of the three allocation components.
- **Validation Rule**: `Sum(Final Share) = 1.0`.
- **Validation Rule**: Isolation tests (e.g. if $\gamma=1.0$, only SIDS receive funds).
- **Location**: `tests/test_tsac_sosac.py`.

### 2. Metadata Completeness
Every record is checked to ensure no missing values for regional or economic classifications.
- **Validation Rule**: 100% of Parties must have an assigned **UN Region**, **WB Income Group**, and **LDC/SIDS status**.
- **Location**: `tests/test_logic.py` -> `test_metadata_completeness` and `test_strict_data_integrity`.

### 3. Allocation Consistency
The mathematical core ensures that the sum of individual allocations matches the user-defined fund size precisely.
- **Validation Rule**: `Sum(State Component + IPLC Component) = Total Fund Size`.
- **Location**: `tests/test_logic.py` -> `test_allocation_sums_to_fund_size` and `test_tiny_scenarios.py`.

### 4. Constraint Validation (Floor/Ceiling)
The model supports user-defined floor and ceiling constraints on individual party shares.
- **Validation Rule**: All eligible parties must receive a share within `[floor, ceiling]` while maintaining a total sum of 100%. The model handles iterative redistribution of shares when constraints are applied.
- **Dynamic Floor Check**: The UI automatically limits the maximum floor percentage to `100 / n_eligible` to prevent mathematical impossibility.
- **Location**: `tests/test_floor_ceiling.py`.

### 5. Cross-Reference Mapping
A systematic mapping layer (`manual_name_map.csv`) standardizes Party names across UN, World Bank, and CBD datasets.
- **Illustration of the Join Strategy**:
  ```sql
  SELECT 
      COALESCE(mapped.name, raw.name) as party,
      COALESCE(regions.name, fallback_regions.name) as region
  FROM parties
  LEFT JOIN name_map ON raw.name = name_map.party_raw
  LEFT JOIN unsd_regions ON mapped.name = unsd_regions.country
  ```
- **Location**: `logic/data_loader.py` -> `get_base_data()`.

## Testing
To run the validation suite locally:
```bash
python3 -m pytest
```
