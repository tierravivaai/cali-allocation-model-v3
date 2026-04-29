import pandas as pd
import yaml
from pathlib import Path

def load_band_config():
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "un_scale_bands.yaml"
    if not config_path.exists():
        return None
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def assign_un_band(un_share, config):
    if config is None or "bands" not in config:
        return None, 1.0
    
    # Ensure un_share is float
    try:
        val = float(un_share)
    except (ValueError, TypeError):
        val = 0.0

    for band in config["bands"]:
        min_t = float(band.get("min_threshold", -999999.0))
        max_t = float(band.get("max_threshold", 999999.0))
        
        # Band logic: (min_t < share <= max_t)
        if val > min_t and val <= max_t:
            return band.get("label"), float(band.get("weight", 1.0))
    
    # Fallback for 0.0 if not caught (should be caught by id: 1)
    if val == 0.0:
        # Manually return Band 1 if it exists
        for band in config["bands"]:
            if band.get("id") == 1:
                return band.get("label"), float(band.get("weight", 1.50))
            
    return None, 1.0

def _apply_floor_ceiling_shares(weights: pd.Series, floor: float, cap: float) -> pd.Series:
    w = weights.fillna(0.0).clip(lower=0.0)
    idx = w.index.tolist()
    n = len(idx)

    if n == 0:
        return pd.Series(dtype=float)

    floor = max(0.0, float(floor))
    cap = min(1.0, float(cap))

    if floor > cap:
        floor = cap

    if floor * n > 1.0:
        return pd.Series(1.0 / n, index=idx)

    if cap * n < 1.0:
        return pd.Series(1.0 / n, index=idx)

    fixed_low = set()
    fixed_high = set()

    while True:
        free = [i for i in idx if i not in fixed_low and i not in fixed_high]

        remaining = 1.0 - floor * len(fixed_low) - cap * len(fixed_high)
        remaining = max(0.0, remaining)

        shares = pd.Series(0.0, index=idx)

        if fixed_low:
            shares.loc[list(fixed_low)] = floor

        if fixed_high:
            shares.loc[list(fixed_high)] = cap

        if free:
            denom = w.loc[free].sum()
            if denom <= 0:
                shares.loc[free] = remaining / len(free)
            else:
                shares.loc[free] = remaining * (w.loc[free] / denom)

        new_low = set(shares.loc[free][shares.loc[free] < floor - 1e-12].index)
        new_high = set(shares.loc[free][shares.loc[free] > cap + 1e-12].index)

        if not new_low and not new_high:
            s = shares.sum()
            return shares / s if s > 0 else shares

        fixed_low |= new_low
        fixed_high |= new_high

def calculate_allocations(
    df,
    fund_size,
    iplc_share_pct,
    show_raw_inversion=False,
    exclude_high_income=False,
    floor_pct=0.0,
    ceiling_pct=None,
    tsac_beta=0.15,
    sosac_gamma=0.10,
    high_income_mode="exclude_except_sids",
    equality_mode=False,
    un_scale_mode="raw_inversion"
):
    # Filter out parties with 0 share for inversion logic (except for display later)
    # But for Cali Fund, we need to invert the non-zero ones.
    
    calc_df = df.copy()
    
    # Initialize extra columns
    calc_df["un_band"] = None
    calc_df["un_band_weight"] = 1.0

    # 1. Define eligibility
    # Rule (recommended): If exclude_high_income == True and mode is "exclude_except_sids", 
    # then: Parties are excluded if income_group == "High income" AND is_sids == False.
    if exclude_high_income:
        if high_income_mode == "exclude_except_sids":
             calc_df["eligible"] = calc_df["is_cbd_party"] & ~( (calc_df["WB Income Group"] == "High income") & (calc_df["is_sids"] == False) )
        else: # "exclude_all"
             calc_df["eligible"] = calc_df["is_cbd_party"] & (calc_df["WB Income Group"] != "High income")
    else:
        calc_df["eligible"] = calc_df["is_cbd_party"]

    # 1b. Equality Mode
    if equality_mode:
        final_eligible_mask = calc_df["eligible"]
        n_eligible = int(final_eligible_mask.sum())
        calc_df["final_share"] = 0.0
        if n_eligible > 0:
            calc_df.loc[final_eligible_mask, "final_share"] = 1.0 / n_eligible
        
        # Zero out components for display/transparency
        calc_df["iusaf_share"] = calc_df["final_share"]
        calc_df["tsac_share"] = 0.0
        calc_df["sosac_share"] = 0.0
        effective_alpha = 1.0
        effective_beta = 0.0
        effective_gamma = 0.0
    else:
        # IUSAF Calculation
        calc_df["iusaf_share"] = 0.0
        # Include all eligible countries, even if un_share is 0 (for band inversion)
        if un_scale_mode == "band_inversion":
            mask = calc_df["eligible"] & (calc_df['un_share'].notna())
        else:
            mask = calc_df["eligible"] & (calc_df['un_share'] > 0) & (calc_df['un_share'].notna())
        
        eligible_idx = calc_df.index[mask]

        if len(eligible_idx) > 0:
            if un_scale_mode == "band_inversion":
                config = load_band_config()
                for idx in eligible_idx:
                    share_val = float(calc_df.loc[idx, "un_share"])
                    band_label, band_weight = assign_un_band(share_val, config)
                    calc_df.loc[idx, "un_band"] = band_label
                    calc_df.loc[idx, "un_band_weight"] = band_weight
                
                weights = calc_df.loc[eligible_idx, "un_band_weight"]
                calc_df.loc[eligible_idx, "iusaf_share"] = weights / weights.sum()
            else: # raw_inversion
                calc_df.loc[mask, 'un_share_fraction'] = calc_df.loc[mask, 'un_share'] / 100.0
                calc_df.loc[mask, 'inv_weight'] = 1.0 / calc_df.loc[mask, 'un_share_fraction']
                
                weights = calc_df.loc[eligible_idx, "inv_weight"]
                calc_df.loc[eligible_idx, "iusaf_share"] = weights / weights.sum()

        # 2. Compute TSAC Share (Land Area)
        calc_df["tsac_share"] = 0.0
        tsac_eligible_mask = calc_df["eligible"] & (calc_df["land_area_km2"] > 0)
        if tsac_eligible_mask.any():
            la_sum = calc_df.loc[tsac_eligible_mask, "land_area_km2"].sum()
            calc_df.loc[tsac_eligible_mask, "tsac_share"] = calc_df.loc[tsac_eligible_mask, "land_area_km2"] / la_sum

        # 3. Compute SOSAC Share (SIDS)
        calc_df["sosac_share"] = 0.0
        sosac_eligible_mask = calc_df["eligible"] & calc_df["is_sids"]
        n_sids = int(sosac_eligible_mask.sum())
        if n_sids > 0:
            calc_df.loc[sosac_eligible_mask, "sosac_share"] = 1.0 / n_sids

        # 4. Handle Blending and Fallback
        beta = float(tsac_beta)
        gamma = float(sosac_gamma)
        
        # Regression check: if weights are zero, use old logic (no TSAC/SOSAC component)
        if beta == 0.0 and gamma == 0.0:
            calc_df["final_share"] = calc_df["iusaf_share"]
            effective_alpha = 1.0
            effective_beta = 0.0
            effective_gamma = 0.0
        else:
            # Fallback if no SIDS
            effective_beta = beta
            effective_gamma = gamma
            effective_alpha = 1.0 - beta - gamma
            
            if n_sids == 0 and gamma > 0:
                # Fallback: reallocate to IUSAF
                effective_alpha += gamma
                effective_gamma = 0.0
                # log warning (implied in UI)
                
            # Compute Final Share
            calc_df["final_share"] = (
                effective_alpha * calc_df["iusaf_share"] + 
                effective_beta * calc_df["tsac_share"] + 
                effective_gamma * calc_df["sosac_share"]
            )
        
        # Normalize
        final_eligible_mask = calc_df["eligible"]
        if final_eligible_mask.any():
            s = calc_df.loc[final_eligible_mask, "final_share"].sum()
            if s > 0:
                calc_df.loc[final_eligible_mask, "final_share"] = calc_df.loc[final_eligible_mask, "final_share"] / s

        # 5. Apply Floor and Ceiling to Final Share if enabled
        if (floor_pct > 0 or ceiling_pct is not None) and final_eligible_mask.any():
            floor = float(floor_pct) / 100.0
            cap = 1.0 if ceiling_pct is None else float(ceiling_pct) / 100.0
            
            constrained_shares = _apply_floor_ceiling_shares(
                calc_df.loc[final_eligible_mask, "final_share"],
                floor=floor,
                cap=cap
            )
            calc_df.loc[final_eligible_mask, "final_share"] = constrained_shares

    # Rename final_share back to inverted_share for compatibility if needed, 
    # but the instruction said to use final_share. Let's provide both.
    calc_df["inverted_share"] = calc_df["final_share"]
    
    calc_df['total_allocation'] = calc_df['final_share'] * fund_size
    calc_df['iplc_component'] = calc_df['total_allocation'] * (iplc_share_pct / 100.0)
    calc_df['state_component'] = calc_df['total_allocation'] - calc_df['iplc_component']
    
    # Component amounts for transparency
    calc_df['component_iusaf_amt'] = (effective_alpha * calc_df["iusaf_share"] * fund_size) / 1_000_000.0
    calc_df['component_tsac_amt'] = (effective_beta * calc_df["tsac_share"] * fund_size) / 1_000_000.0
    calc_df['component_sosac_amt'] = (effective_gamma * calc_df["sosac_share"] * fund_size) / 1_000_000.0

    # Convert to millions for display
    for col in ['total_allocation', 'iplc_component', 'state_component']:
        calc_df[col] = calc_df[col] / 1_000_000.0
        
    return calc_df

def aggregate_by_region(df, region_col='region'):
    # We count all CBD parties that are eligible for the calculation
    # Even if they have 0 allocation (e.g. they had 0 UN share or are the EU entity)
    # BUT we only show those that are "eligible" based on the current toggle (e.g. not HI if excluded)
    mask = df['is_cbd_party'] & df['eligible']
    
    agg_sums = df[mask].groupby(region_col, dropna=False)[['total_allocation', 'state_component', 'iplc_component']].sum()
    agg_counts = df[mask].groupby(region_col, dropna=False)['party'].count()
    
    agg = agg_sums.merge(agg_counts, left_index=True, right_index=True).reset_index()
    agg = agg.rename(columns={'party': 'Countries (number)'})
    
    # Filter to only show groups that have at least one party
    return agg[agg['Countries (number)'] > 0]

def aggregate_eu(df):
    ms_df = df[df['is_eu_ms']]
    eu_party = df[df['party'] == 'European Union']
    
    combined = pd.concat([ms_df, eu_party])
    total_row = combined[['total_allocation', 'state_component', 'iplc_component']].sum()
    total_row['party'] = 'EU Member States + European Union (total)'
    total_row['Countries (number)'] = len(combined)
    
    return combined, total_row

def aggregate_special_groups(df):
    # Count all CBD parties in these groups that are eligible
    mask = df['is_cbd_party'] & df['eligible']
    
    ldc_df = df[df['is_ldc'] & mask]
    sids_df = df[df['is_sids'] & mask]
    
    ldc_sum = ldc_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    ldc_sum['Countries (number)'] = len(ldc_df)
    
    sids_sum = sids_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    sids_sum['Countries (number)'] = len(sids_df)
    
    return ldc_sum, sids_sum

def aggregate_by_income(df):
    # Count all CBD parties that are eligible
    mask = df['is_cbd_party'] & df['eligible']
    
    agg_sums = df[mask].groupby('WB Income Group', dropna=False)[['total_allocation', 'state_component', 'iplc_component']].sum()
    agg_counts = df[mask].groupby('WB Income Group', dropna=False)['party'].count()
    
    agg = agg_sums.merge(agg_counts, left_index=True, right_index=True).reset_index()
    agg = agg.rename(columns={'party': 'Countries (number)'})
    
    return agg[agg['Countries (number)'] > 0]

def add_total_row(df, label_col, label="Total"):
    """Adds a summary 'Total' row to an aggregated dataframe."""
    if df.empty:
        return df
        
    numeric_cols = df.select_dtypes(include=['number']).columns
    total_row = df[numeric_cols].sum()
    
    # Create the new row as a dictionary
    row_dict = {col: total_row[col] for col in numeric_cols}
    row_dict[label_col] = label
    
    # Fill in any missing columns with empty string or appropriate default
    for col in df.columns:
        if col not in row_dict:
            row_dict[col] = ""
            
    return pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)

def get_stewardship_blend_feedback(tsac_beta: float, sosac_gamma: float) -> dict:
    stewardship_total = float(tsac_beta) + float(sosac_gamma)

    if stewardship_total == 0.0:
        return {
            "stewardship_total": stewardship_total,
            "status_text": "Current blend: no stewardship recognition.",
            "warning_level": "none",
            "warning_text": None,
            "dominance_text": "Current blend: IUSAF remains the dominant allocation base."
        }

    if stewardship_total <= 0.15:
        return {
            "stewardship_total": stewardship_total,
            "status_text": "Current blend: modest stewardship recognition.",
            "warning_level": "none",
            "warning_text": None,
            "dominance_text": "Current blend: IUSAF remains the dominant allocation base."
        }

    if stewardship_total <= 0.20:
        return {
            "stewardship_total": stewardship_total,
            "status_text": "Current blend: strong stewardship recognition.",
            "warning_level": "mild",
            "warning_text": "Stewardship adjustments are becoming strong. TSAC and SOSAC may now be materially reshaping outcomes rather than simply recognising stewardship and special circumstances.",
            "dominance_text": None
        }

    return {
        "stewardship_total": stewardship_total,
        "status_text": "Current blend: stewardship adjustments may be overriding the IUSAF base.",
        "warning_level": "strong",
        "warning_text": "Warning: TSAC and SOSAC now account for a large enough share of the formula that stewardship adjustments may be overriding the IUSAF base. This may reduce fairness, transparency and intelligibility between Parties.",
        "dominance_text": None
    }

def get_outcome_warning_feedback(results_df: pd.DataFrame, fund_size_usd: float):
    eligible_df = results_df[results_df["eligible"]].copy()
    n_eligible = len(eligible_df)
    if n_eligible == 0:
        return None

    equal_share_m = (float(fund_size_usd) / n_eligible) / 1_000_000.0
    if equal_share_m <= 0:
        return None

    below_equality_share = (eligible_df["total_allocation"] < equal_share_m).mean()
    median_pct_of_equality = (eligible_df["total_allocation"].median() / equal_share_m) * 100.0

    cond_a = below_equality_share > 0.60
    cond_b = median_pct_of_equality < 90.0

    if not cond_a and not cond_b:
        return None

    if cond_a and cond_b:
        message = (
            "Outcome warning: more than 60% of eligible countries are below the equality reference, "
            "and the median eligible country is receiving less than 90% of the equality reference. "
            "This suggests the current blend may be politically difficult to defend as broadly fair."
        )
    elif cond_a:
        message = (
            "Outcome warning: more than 60% of eligible countries are below the equality reference. "
            "This suggests the current blend may be politically difficult to defend as broadly fair."
        )
    else:
        message = (
            "Outcome warning: the median eligible country is receiving less than 90% of the equality reference. "
            "This suggests stewardship adjustments may be pulling the model away from a broadly acceptable sovereign baseline."
        )

    top_10_share_pct = (
        eligible_df.nlargest(min(10, n_eligible), "total_allocation")["total_allocation"].sum()
        / eligible_df["total_allocation"].sum()
        * 100.0
    )

    return {
        "message": message,
        "equal_share_m": equal_share_m,
        "below_equality_share": float(below_equality_share),
        "median_pct_of_equality": float(median_pct_of_equality),
        "top_10_share_pct": float(top_10_share_pct),
    }
