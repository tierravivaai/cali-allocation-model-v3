import streamlit as st
import duckdb
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from logic.data_loader import load_data, get_base_data
from logic.calculator import calculate_allocations, aggregate_by_region, aggregate_eu, aggregate_special_groups, aggregate_by_income, add_total_row, get_stewardship_blend_feedback, get_outcome_warning_feedback

st.set_page_config(page_title="Cali Fund Allocation Model (Inverted UN Scale Option)", layout="wide")

st.markdown(
    """
    <style>
    div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-weight: 700;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.4rem;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stSlider"],
    section[data-testid="stSidebar"] [data-testid="stSelectbox"],
    section[data-testid="stSidebar"] [data-testid="stCheckbox"],
    section[data-testid="stSidebar"] [data-testid="stToggle"] {
        margin-bottom: 0.35rem;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarDivider"] {
        margin: 0.4rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Cali Fund Allocation Model (Inverted UN Scale Option)")
st.markdown("""
This interactive application uses the UN Scale of Assessments (2025–2027) to model indicative shares of the Cali Fund. The model inverts assessed UN budget shares and groups countries into bands so that countries with smaller assessed shares receive proportionally larger indicative allocations. Adjustments are then made to recognise different biodiversity stewardship responsibilities in the form of a flexible Terrestrial Stewardship Allocation Component (TSAC) and SIDS Ocean Stewardship Allocation Component (SOSAC). The aim is to assist Parties with identifying the right balance points.

The IPLC component is presented as integral to the formula and is consistent with Decision 16/2. Parties may wish to note that **in practice the amount allocated to IPLCs by the formula and appropriate pathways to disbursement to IPLCS are separate considerations**. Different pathways to disbursement may be appropriate at the national, subnational or UN regional/sub-regional level and may be informed by a combination of existing experience, guiding principles and the programme of work of the Subsidiary Body on Article 8J and Other Provisions of the Convention as adopted in Decision 16/4.

All figures are illustrative modelling outputs for exploratory purposes. They do not represent entitlements or predetermined disbursements. The model has no formal status.
""")

# Initialize connection and data
if 'con' not in st.session_state:
    st.session_state.con = duckdb.connect(database=':memory:')
    load_data(st.session_state.con)
    st.session_state.base_df = get_base_data(st.session_state.con)

# Initialize widget states
if "fund_size_bn" not in st.session_state:
    st.session_state["fund_size_bn"] = 1.0
if "iplc_share" not in st.session_state:
    st.session_state["iplc_share"] = 50
if "show_raw" not in st.session_state:
    st.session_state["show_raw"] = False
if "use_thousands" not in st.session_state:
    st.session_state["use_thousands"] = False
if "exclude_hi" not in st.session_state:
    st.session_state["exclude_hi"] = False
if "enable_floor" not in st.session_state:
    st.session_state["enable_floor"] = False
if "floor_pct" not in st.session_state:
    st.session_state["floor_pct"] = 0.05
if "enable_ceiling" not in st.session_state:
    st.session_state["enable_ceiling"] = False
if "ceiling_pct" not in st.session_state:
    st.session_state["ceiling_pct"] = 1.0
if "tsac_beta" not in st.session_state:
    st.session_state["tsac_beta"] = 0.0
if "sosac_gamma" not in st.session_state:
    st.session_state["sosac_gamma"] = 0.0
if "tsac_beta_pct" not in st.session_state:
    st.session_state["tsac_beta_pct"] = int(round(st.session_state["tsac_beta"] * 100))
if "sosac_gamma_pct" not in st.session_state:
    st.session_state["sosac_gamma_pct"] = int(round(st.session_state["sosac_gamma"] * 100))
if "equality_mode" not in st.session_state:
    st.session_state["equality_mode"] = True
if "show_advanced" not in st.session_state:
    st.session_state["show_advanced"] = False
if "sort_option" not in st.session_state:
    st.session_state["sort_option"] = "Allocation (highest first)"
if "show_negotiation_dashboard" not in st.session_state:
    st.session_state["show_negotiation_dashboard"] = True
if "un_scale_mode" not in st.session_state:
    st.session_state["un_scale_mode"] = "band_inversion"

# Sidebar Controls
st.sidebar.header("Controls")

# Reset to default button
if st.sidebar.button("Reset to default"):
    st.session_state["fund_size_bn"] = 1.0
    st.session_state["iplc_share"] = 50
    st.session_state["show_raw"] = False
    st.session_state["use_thousands"] = False
    st.session_state["exclude_hi"] = False
    st.session_state["enable_floor"] = False
    st.session_state["floor_pct"] = 0.05
    st.session_state["enable_ceiling"] = False
    st.session_state["ceiling_pct"] = 1.0
    st.session_state["tsac_beta"] = 0.0
    st.session_state["sosac_gamma"] = 0.0
    st.session_state["tsac_beta_pct"] = 0
    st.session_state["sosac_gamma_pct"] = 0
    st.session_state["equality_mode"] = True
    st.session_state["show_advanced"] = False
    st.session_state["sort_option"] = "Allocation (highest first)"
    st.session_state["show_negotiation_dashboard"] = True
    st.session_state["un_scale_mode"] = "band_inversion"
    st.rerun()

st.sidebar.caption(":gray[Default is raw equality between all Parties]")

st.sidebar.markdown("**Scenario Sizes**")
marker_col1, marker_col2 = st.sidebar.columns(2)
if marker_col1.button("$50m"):
    st.session_state["fund_size_bn"] = 0.05
    st.rerun()
if marker_col2.button("$200m"):
    st.session_state["fund_size_bn"] = 0.2
    st.rerun()
if marker_col1.button("$500m"):
    st.session_state["fund_size_bn"] = 0.5
    st.rerun()
if marker_col2.button("$1bn"):
    st.session_state["fund_size_bn"] = 1.0
    st.rerun()

fund_size_bn = st.sidebar.slider(
    "Annual Cali Fund size (USD billion)",
    min_value=0.002,   # $2m
    max_value=10.0,
    step=0.001,        # $1m increments
    format="$%.3fbn",
    key="fund_size_bn"
)
st.sidebar.caption(f"= ${fund_size_bn * 1000:,.0f} million per year")

st.sidebar.divider()
st.sidebar.header("UN Scale Treatment")
un_scale_mode = st.sidebar.selectbox(
    "Calculation Method",
    options=["Raw inversion", "Band-based inversion"],
    index=0 if st.session_state["un_scale_mode"] == "raw_inversion" else 1,
    help="Choose how the UN scale is used to determine baseline weights."
)
st.session_state["un_scale_mode"] = "raw_inversion" if un_scale_mode == "Raw inversion" else "band_inversion"

# Negotiation Presets
with st.sidebar.expander("Negotiation Presets", expanded=True):
    col_p1, col_p2 = st.columns(2)
    # Row 1
    if col_p1.button("1. Equality", help="Even split between all eligible countries (Excludes HI except SIDS)"):
        st.session_state["tsac_beta"] = 0.0
        st.session_state["sosac_gamma"] = 0.0
        st.session_state["tsac_beta_pct"] = 0
        st.session_state["sosac_gamma_pct"] = 0
        st.session_state["equality_mode"] = True
        st.session_state["exclude_hi"] = True
        st.rerun()
    if col_p2.button("2. Inverted UN Scale", help="TSAC=0, SOSAC=0 (Pure IUSAF)"):
        st.session_state["tsac_beta"] = 0.0
        st.session_state["sosac_gamma"] = 0.0
        st.session_state["tsac_beta_pct"] = 0
        st.session_state["sosac_gamma_pct"] = 0
        st.session_state["exclude_hi"] = True
        st.session_state["equality_mode"] = False
        st.rerun()
    
    # Row 2
    if col_p1.button("3. Terrestrial Stewardship", help="TSAC=max, SOSAC=0"):
        st.session_state["tsac_beta"] = 0.15
        st.session_state["sosac_gamma"] = 0.0
        st.session_state["tsac_beta_pct"] = 15
        st.session_state["sosac_gamma_pct"] = 0
        st.session_state["exclude_hi"] = True
        st.session_state["equality_mode"] = False
        st.rerun()
    if col_p2.button("4. Oceans Stewardship", help="TSAC=0, SOSAC=max"):
        st.session_state["tsac_beta"] = 0.0
        st.session_state["sosac_gamma"] = 0.10
        st.session_state["tsac_beta_pct"] = 0
        st.session_state["sosac_gamma_pct"] = 10
        st.session_state["exclude_hi"] = True
        st.session_state["equality_mode"] = False
        st.rerun()
        
    # Row 3 (Full width)
    if st.button("5. Balanced", help="TSAC=0.05, SOSAC=0.03 (Default)", use_container_width=True):
        st.session_state["tsac_beta"] = 0.05
        st.session_state["sosac_gamma"] = 0.03
        st.session_state["tsac_beta_pct"] = 5
        st.session_state["sosac_gamma_pct"] = 3
        st.session_state["exclude_hi"] = True
        st.session_state["equality_mode"] = False
        st.rerun()

# Calculations Pre-setup
fund_size_usd = fund_size_bn * 1_000_000_000

exclude_hi = st.sidebar.checkbox(
    "Exclude High Income countries (except SIDS)", 
    key="exclude_hi",
    help="When enabled, High Income countries (except SIDS) receive zero allocation and the remaining allocations are rescaled so the total fund remains unchanged."
)

st.sidebar.divider()
st.sidebar.header("Stewardship Allocation Weights")

tsac_beta_pct = st.sidebar.slider(
    "Terrestrial Stewardship Allocation Component (TSAC)",
    min_value=0,
    max_value=15,
    step=1,
    format="%d%%",
    key="tsac_beta_pct",
    help="TSAC recognises stewardship responsibilities associated with larger land areas. It should normally act as a modest uplift rather than a dominant allocation driver."
)

sosac_gamma_pct = st.sidebar.slider(
    "SIDS Ocean Stewardship Allocation Component (SOSAC)",
    min_value=0,
    max_value=10,
    step=1,
    format="%d%%",
    key="sosac_gamma_pct",
    help="SOSAC recognises the special circumstances of SIDS. It should normally act as a modest uplift rather than a dominant allocation driver."
)

tsac_beta = tsac_beta_pct / 100.0
sosac_gamma = sosac_gamma_pct / 100.0
st.session_state["tsac_beta"] = tsac_beta
st.session_state["sosac_gamma"] = sosac_gamma

if tsac_beta + sosac_gamma >= 1.0:
    st.sidebar.error("Invalid blend: TSAC + SOSAC must remain below 1.0 so the IUSAF base can be computed.")
    st.stop()

stewardship_feedback = get_stewardship_blend_feedback(tsac_beta, sosac_gamma)
st.sidebar.caption(stewardship_feedback["status_text"])
if stewardship_feedback["warning_level"] == "none":
    st.sidebar.caption(stewardship_feedback["dominance_text"])
elif stewardship_feedback["warning_level"] == "mild":
    st.sidebar.warning(stewardship_feedback["warning_text"])
else:
    st.sidebar.error(stewardship_feedback["warning_text"])

# Dynamic Interpretation Boxes
tsac_amt_m = (fund_size_usd * tsac_beta) / 1_000_000
sosac_amt_m = (fund_size_usd * sosac_gamma) / 1_000_000
iusaf_weight = 1.0 - tsac_beta - sosac_gamma
iusaf_amt_m = (fund_size_usd * max(0, iusaf_weight)) / 1_000_000

# Calculate eligible SIDS count
if exclude_hi:
    eligible_sids_count = ((st.session_state.base_df["is_cbd_party"]) & (st.session_state.base_df["is_sids"]) & ~( (st.session_state.base_df["WB Income Group"] == "High income") & (st.session_state.base_df["is_sids"] == False) )).sum()
else:
    eligible_sids_count = ((st.session_state.base_df["is_cbd_party"]) & (st.session_state.base_df["is_sids"])).sum()

st.sidebar.info(
    f"**TSAC Interpretation**\n\n"
    f"With TSAC set to **{tsac_beta:.0%}**, **US${tsac_amt_m:,.2f}m** is allocated based on land surface area.\n\n"
    f"IUSAF base weight: **{iusaf_weight:.0%}** (US${iusaf_amt_m:,.2f}m)."
)

if eligible_sids_count > 0:
    if sosac_gamma > 0:
        st.sidebar.info(
            f"**SOSAC Interpretation**\n\n"
            f"With SOSAC set to **{sosac_gamma:.0%}**, **US${sosac_amt_m:,.2f}m** is reserved for SIDS. "
            f"Shared equally among **{eligible_sids_count}** eligible SIDS."
        )
    else:
        st.sidebar.info("**SOSAC Interpretation**\n\nSOSAC is set to 0%, so no SIDS-specific pool is applied.")
else:
    if sosac_gamma > 0:
        st.sidebar.info(
            f"**SOSAC Interpretation**\n\n"
            f"No eligible SIDS under current filters. The SOSAC portion (**US${sosac_amt_m:,.2f}m**) will be reallocated to the inverted UN scale (IUSAF)."
        )
    else:
        st.sidebar.info("**SOSAC Interpretation**\n\nSOSAC is set to 0%.")

st.sidebar.divider()
st.sidebar.header("Constraint Controls")

enable_floor = st.sidebar.checkbox("Enable minimum share (floor)", key="enable_floor")
if enable_floor:
    eligible_mask = st.session_state.base_df["is_cbd_party"].astype(bool)
    if exclude_hi:
        eligible_mask = eligible_mask & (st.session_state.base_df["WB Income Group"] != "High income")

    n_eligible = int(eligible_mask.sum())
    max_floor_pct = 0.0 if n_eligible <= 0 else (100.0 / n_eligible)

    floor_pct = st.sidebar.slider(
        "Minimum share per eligible country (% of total fund)",
        min_value=0.00,
        max_value=float(max_floor_pct),
        value=min(0.05, float(max_floor_pct)),
        step=0.01,
        format="%.2f",
        help=(
            "Sets a minimum percentage of the total fund for each eligible country. "
            "The maximum possible value is automatically limited to 100% divided by the number of eligible countries "
            "to ensure the model remains feasible."
        ),
        key="floor_pct"
    )

    st.sidebar.caption(
        f"Eligible countries: {n_eligible} • "
        f"Max feasible floor: {max_floor_pct:.2f}% • "
        f"Floor ≈ ${fund_size_usd * (floor_pct/100) / 1_000_000:,.2f}m per eligible country"
    )
else:
    floor_pct = 0.0

enable_ceiling = st.sidebar.checkbox("Enable maximum share (ceiling)", key="enable_ceiling")
if enable_ceiling:
    ceiling_pct = st.sidebar.slider(
        "Maximum share per eligible country (% of total fund)",
        min_value=0.10,
        max_value=5.00,
        step=0.10,
        format="%.2f",
        key="ceiling_pct"
    )
    st.sidebar.caption(
        f"≈ ${fund_size_usd * (ceiling_pct/100) / 1_000_000:,.2f}m per eligible country"
    )

    with st.sidebar.expander("More ceiling options"):
        ceiling_pct_ext = st.slider(
            "Maximum share per eligible country (% of total fund) — extended range",
            min_value=5.00,
            max_value=20.00,
            value=st.session_state.get("ceiling_pct_ext", max(5.0, 1.0)), # default 1.0
            step=0.50,
            format="%.2f",
            key="ceiling_pct_ext"
        )
        # Use the extended one if the primary one is at its max
        if ceiling_pct >= 5.0:
            ceiling_pct = ceiling_pct_ext
            
        st.caption(
            f"≈ ${fund_size_usd * (ceiling_pct/100) / 1_000_000:,.2f}m per eligible country"
        )
else:
    ceiling_pct = None

iplc_share = st.sidebar.slider(
    "Share earmarked for Indigenous Peoples & Local Communities (%)",
    min_value=50,
    max_value=80,
    help="This splits each Party’s allocation into an IPLC component and a State component. Together they equal the total.",
    key="iplc_share"
)

st.sidebar.divider()
st.sidebar.header("Helper Controls")

show_raw = st.sidebar.toggle("Show explanation with raw data", key="show_raw")

use_thousands = st.sidebar.toggle("Display small values in thousands (USD '000)", key="use_thousands")

show_advanced = st.sidebar.toggle("Show advanced component breakdown", key="show_advanced")

st.sidebar.toggle("Enable Negotiation Dashboard", key="show_negotiation_dashboard")

sort_option = st.sidebar.selectbox(
    "Sort results by",
    options=["Allocation (highest first)", "Country name (A–Z)"],
    key="sort_option"
)

results_df = calculate_allocations(
    st.session_state.base_df,
    fund_size_usd,
    iplc_share,
    show_raw,
    exclude_hi,
    floor_pct=floor_pct,
    ceiling_pct=ceiling_pct,
    tsac_beta=tsac_beta,
    sosac_gamma=sosac_gamma,
    equality_mode=st.session_state.get("equality_mode", False),
    un_scale_mode=st.session_state.get("un_scale_mode", "raw_inversion")
)

outcome_warning = get_outcome_warning_feedback(results_df, fund_size_usd)
if outcome_warning:
    st.sidebar.warning(outcome_warning["message"])

if st.session_state["un_scale_mode"] == "band_inversion":
    # Count countries per band for eligible countries
    b_counts = results_df[results_df['eligible']].groupby('un_band')['party'].count().to_dict()

    st.sidebar.info(
        "**Band-based inversion** groups countries into 6 broad UN assessment bands and applies a transparent graduated uplift, "
        "instead of mechanically inverting every small difference in the UN scale. "
        "Each country's share is proportional to its band weight. "
        "Bands 1–5 follow a smooth gradient; Band 6 separates countries with UN assessments "
        "above 10% (currently China only) to preserve the inversion principle given the "
        "18-fold difference between China's assessment and the next-largest eligible contributor. "
        "TSAC provides stewardship recognition for large-landmass countries transparently on top.\n\n"
        "**The 6 bands are:**\n"
        f"- **Band 1**: <= 0.001% UN Share ({b_counts.get('Band 1: <= 0.001%', 0)}) — weight 1.50\n"
        f"- **Band 2**: 0.001% - 0.01% ({b_counts.get('Band 2: 0.001% - 0.01%', 0)}) — weight 1.30\n"
        f"- **Band 3**: 0.01% - 0.1% ({b_counts.get('Band 3: 0.01% - 0.1%', 0)}) — weight 1.10\n"
        f"- **Band 4**: 0.1% - 1.0% ({b_counts.get('Band 4: 0.1% - 1.0%', 0)}) — weight 0.95\n"
        f"- **Band 5**: 1.0% - 10.0% ({b_counts.get('Band 5: 1.0% - 10.0%', 0)}) — weight 0.75\n"
        f"- **Band 6**: > 10.0% ({b_counts.get('Band 6: > 10.0%', 0)}) — weight 0.40"
    )

# Baseline Logic
# 1. If we are in Inverted UN Scale (beta=0, gamma=0, equality=False), 
#    the baseline should be Equality (equality=True).
# 2. If we are in any other preset (Stewardship, Balanced, etc.),
#    the baseline should be Inverted UN Scale (beta=0, gamma=0, equality=False).
# 3. If we are in Equality preset (equality=True), metrics should be 0 (baseline = current).

is_eq_mode = st.session_state.get("equality_mode", False)
is_inverted_scale = (tsac_beta == 0 and sosac_gamma == 0 and not is_eq_mode)

if is_eq_mode:
    # Equality preset selected: No baseline comparison
    results_df_baseline = results_df.copy()
    baseline_label = "Equality"
elif is_inverted_scale:
    # Inverted UN Scale selected: Compare against Equality
    results_df_baseline = calculate_allocations(
        st.session_state.base_df,
        fund_size_usd,
        iplc_share,
        False, # show_raw
        exclude_hi,
        floor_pct=floor_pct,
        ceiling_pct=ceiling_pct,
        tsac_beta=0.0,
        sosac_gamma=0.0,
        equality_mode=True,
        un_scale_mode=st.session_state.get("un_scale_mode", "raw_inversion")
    )
    baseline_label = "Equality"
else:
    # Stewardship/Balanced selected: Compare against Inverted UN Scale (IUSAF)
    results_df_baseline = calculate_allocations(
        st.session_state.base_df,
        fund_size_usd,
        iplc_share,
        False, # show_raw
        exclude_hi,
        floor_pct=floor_pct,
        ceiling_pct=ceiling_pct,
        tsac_beta=0.0,
        sosac_gamma=0.0,
        equality_mode=False,
        un_scale_mode=st.session_state.get("un_scale_mode", "raw_inversion")
    )
    baseline_label = "IUSAF"

# Merge baseline for comparison
comparison_df = results_df[['party', 'total_allocation', 'WB Income Group', 'region', 'is_ldc', 'is_sids', 'is_cbd_party', 'eligible']].copy()
comparison_df = comparison_df.rename(columns={'total_allocation': 'current_amt'})
comparison_df['baseline_amt'] = results_df_baseline['total_allocation']

comparison_df['delta_amt'] = comparison_df['current_amt'] - comparison_df['baseline_amt']
comparison_df['pct_change'] = (comparison_df['delta_amt'] / comparison_df['baseline_amt'].replace(0, np.nan)) * 100

# Add descriptive columns
results_df["EU"] = results_df["is_eu_ms"].map({True: "EU Member", False: "Non-EU"})
results_df["UN LDC"] = results_df["is_ldc"].map({True: "LDC", False: "-"})

# Apply sorting
if sort_option == "Allocation (highest first)":
    results_df = results_df.sort_values(
        by=["total_allocation", "party"],
        ascending=[False, True]
    ).reset_index(drop=True)
    results_df.index = results_df.index + 1
    results_df.index.name = "Rank"
else:
    results_df = results_df.sort_values(
        by="party",
        ascending=True
    ).reset_index(drop=True)

def format_currency(val):
    if use_thousands and val < 1.0:
        return f"${val * 1000:,.2f}k"
    return f"${val:,.2f}m"

# Helper for dataframe formatting
def get_column_config(use_thousands, include_country_count=False):
    config = {}
    if include_country_count:
        config["Countries (number)"] = st.column_config.NumberColumn("Countries (number)", format="%d")
        
    if use_thousands:
        # When using thousands, we must use TextColumn because we mix 'k' and 'm'
        config.update({
            "total_allocation": st.column_config.TextColumn("Total Share (USD)"),
            "state_component": st.column_config.TextColumn("State Component (USD)"),
            "iplc_component": st.column_config.TextColumn("IPLC Component (USD)"),
            "component_iusaf_amt": st.column_config.TextColumn("IUSAF (USD)"),
            "component_tsac_amt": st.column_config.TextColumn("TSAC (USD)"),
            "component_sosac_amt": st.column_config.TextColumn("SOSAC (USD)"),
        })
    else:
        # Standard millions view can use NumberColumn for better sorting
        config.update({
            "total_allocation": st.column_config.NumberColumn("Total Share (USD Millions)", format="$%.2f"),
            "state_component": st.column_config.NumberColumn("State Component (USD Millions)", format="$%.2f"),
            "iplc_component": st.column_config.NumberColumn("IPLC Component (USD Millions)", format="$%.2f"),
            "component_iusaf_amt": st.column_config.NumberColumn("IUSAF (USD Millions)", format="$%.2f"),
            "component_tsac_amt": st.column_config.NumberColumn("TSAC (USD Millions)", format="$%.2f"),
            "component_sosac_amt": st.column_config.NumberColumn("SOSAC (USD Millions)", format="$%.2f"),
        })
    
    # Common labels for Banding (if present in display_cols)
    config.update({
        "un_band": "UN Band",
        "un_band_weight": st.column_config.NumberColumn("Band Weight", format="%.2f")
    })
    
    return config

# Main Tabs
tabs = [
    "By Party", 
    "By UN Region", 
    "By UN Sub-region",
    "By UN Intermediate Region",
    "Share by Income Group",
    "LDC Share", 
    "SIDS",
    "Low Income",
    "Middle Income",
    "High Income",
    "Inversion Comparison"
]

if st.session_state.get("show_negotiation_dashboard", True):
    tabs.insert(0, "Negotiation Dashboard")

main_tabs = st.tabs(tabs)
current_tab_idx = 0

if st.session_state.get("show_negotiation_dashboard", True):
    with main_tabs[current_tab_idx]:
        st.subheader("Negotiation Dashboard")
        
        # Summary Row
        col1, col2, col3, col4 = st.columns(4)
        num_increases = (comparison_df['delta_amt'] > 0.001).sum()
        num_decreases = (comparison_df['delta_amt'] < -0.001).sum()
        unchanged = len(comparison_df[comparison_df['eligible']]) - num_increases - num_decreases
        
        col1.metric(f"Increases vs Baseline ({baseline_label})", num_increases, delta=None)
        col2.metric(f"Decreases vs Baseline ({baseline_label})", num_decreases, delta=None)
        col3.metric("Unchanged", unchanged)
        
        total_shift = comparison_df[comparison_df['delta_amt'] > 0]['delta_amt'].sum()
        col4.metric("Reallocated Amount", f"US${total_shift:,.2f}m", help=f"Total amount shifted from countries with decreases to those with increases compared to {baseline_label}.")

        st.divider()
        
        # Charts Row
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if is_eq_mode or is_inverted_scale:
                title = f"**Top 10 & Bottom 10 Recipients ({'Equality' if is_eq_mode else 'IUSAF Base'}) (US$m)**"
                st.write(title)
                # Filter for non-zero allocations to show meaningful "Bottom 10"
                non_zero_base = comparison_df[comparison_df['current_amt'] > 0.0001].copy()
                
                # Consistent Top 10: Sort by Amount (desc) then Alphabetical (asc)
                top_iusaf = non_zero_base.sort_values(['current_amt', 'party'], ascending=[False, True]).head(10).copy()
                top_iusaf['category'] = 'Top 10'
                
                # Consistent Bottom 10: Sort by Amount (asc) then Alphabetical (asc)
                bottom_iusaf = non_zero_base.sort_values(['current_amt', 'party'], ascending=[True, True]).head(10).copy()
                bottom_iusaf['category'] = 'Bottom 10'
                
                # For display in px.bar orientation='h'
                combined_iusaf = pd.concat([
                    bottom_iusaf.sort_values(['current_amt', 'party'], ascending=[False, False]),
                    top_iusaf.sort_values(['current_amt', 'party'], ascending=[True, False])
                ])
                
                fig = px.bar(
                    combined_iusaf, 
                    x='current_amt', 
                    y='party', 
                    orientation='h',
                    color='category',
                    color_discrete_map={'Top 10': '#1f77b4', 'Bottom 10': '#94a3b8'}, # Blue and Neutral Gray
                    labels={'current_amt': 'Allocation (US$m)', 'party': 'Country', 'category': 'Group'}
                )
                fig.update_layout(
                    showlegend=True, 
                    height=500, 
                    margin=dict(l=150, r=50, t=40, b=40)
                )
                fig.update_yaxes(automargin=True)
            else:
                st.write(f"**Top 10 Increases & Decreases vs {baseline_label} (US$m)**")
                # Consistent Increases: Sort by Delta (desc) then Alphabetical (asc)
                top_increases = comparison_df.sort_values(['delta_amt', 'party'], ascending=[False, True]).head(10).copy()
                top_increases['category'] = 'Top 10 Increases'
                
                # Consistent Decreases: Sort by Delta (asc) then Alphabetical (asc)
                top_decreases = comparison_df.sort_values(['delta_amt', 'party'], ascending=[True, True]).head(10).copy()
                top_decreases['category'] = 'Top 10 Decreases'
                
                # For display: Decreases at bottom, Increases at top. 
                # Reverse alphabetical for top-to-bottom visual order in Plotly 'h'
                inc_dec_df = pd.concat([
                    top_decreases.sort_values(['delta_amt', 'party'], ascending=[False, False]),
                    top_increases.sort_values(['delta_amt', 'party'], ascending=[True, False])
                ])
                
                fig = px.bar(
                    inc_dec_df, 
                    x='delta_amt', 
                    y='party', 
                    orientation='h',
                    color='delta_amt',
                    color_continuous_scale='RdBu_r',
                    labels={'delta_amt': 'Delta (US$m)', 'party': 'Country'}
                )
                fig.update_layout(
                    showlegend=False, 
                    height=500, 
                    margin=dict(l=150, r=50, t=40, b=40)
                )
                fig.update_yaxes(automargin=True)
            st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            group_type = st.selectbox("Compare by:", ["region", "WB Income Group", "is_ldc", "is_sids"], key="group_impact_type")
            
            if (tsac_beta == 0 and sosac_gamma == 0) or st.session_state.get("equality_mode", False):
                title = "**Group Totals (IUSAF Base) (US$m)**" if not st.session_state.get("equality_mode") else "**Group Totals (Equality) (US$m)**"
                st.write(title)
                
                # Filter for eligible parties only for aggregation
                eligible_comp = comparison_df[comparison_df['eligible']].copy()
                
                group_stats = eligible_comp.groupby(group_type).agg(
                    total_amt=('current_amt', 'sum'),
                    party_count=('party', 'count')
                ).sort_values('total_amt', ascending=True)
                
                # Formatting for display
                if group_type == "is_ldc":
                    group_stats.index = group_stats.index.map({True: "LDC", False: "Non-LDC"})
                if group_type == "is_sids":
                    group_stats.index = group_stats.index.map({True: "SIDS", False: "Non-SIDS"})
                
                # Prepare custom text: "$Value (Count countries)"
                group_stats['display_text'] = group_stats.apply(
                    lambda x: f"${x['total_amt']:,.1f}m ({int(x['party_count'])})", axis=1
                )
                
                fig = px.bar(
                    group_stats,
                    x='total_amt',
                    y=group_stats.index,
                    orientation='h',
                    text='display_text',
                    labels={'total_amt': 'Total Allocation (US$m)', 'y': 'Group'}
                )
                fig.update_traces(textposition='outside', cliponaxis=False)
                fig.update_yaxes(automargin=True)
                fig.update_layout(height=400, margin=dict(l=200, r=300, t=40, b=40))
            else:
                st.write("**Group Impact (Share % Change)**")
                eligible_comp = comparison_df[comparison_df['eligible']].copy()
                
                group_baseline = eligible_comp.groupby(group_type)['baseline_amt'].sum()
                group_current = eligible_comp.groupby(group_type)['current_amt'].sum()
                group_counts = eligible_comp.groupby(group_type)['party'].count()
                
                group_impact = (((group_current / group_baseline.replace(0, np.nan)) - 1) * 100)
                
                group_stats = pd.DataFrame({
                    'impact': group_impact,
                    'party_count': group_counts
                }).sort_values('impact', ascending=True)
                
                # Formatting for display
                if group_type == "is_ldc":
                    group_stats.index = group_stats.index.map({True: "LDC", False: "Non-LDC"})
                if group_type == "is_sids":
                    group_stats.index = group_stats.index.map({True: "SIDS", False: "Non-SIDS"})
                
                # Prepare custom text: "%Impact (Count countries)" - Round to whole numbers
                group_stats['display_text'] = group_stats.apply(
                    lambda x: f"{int(round(x['impact']))}% ({int(x['party_count'])})", axis=1
                )
                    
                fig = px.bar(
                    group_stats,
                    x='impact',
                    y=group_stats.index,
                    orientation='h',
                    text='display_text',
                    labels={'impact': '% Change in Total Share', 'y': 'Group'}
                )
                fig.update_traces(textposition='outside', cliponaxis=False)
                fig.update_yaxes(automargin=True)
                fig.update_layout(height=400, margin=dict(l=200, r=300, t=40, b=40))
                st.caption("*Percentages are rounded to the nearest whole number.")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        
        # Lower Detail Row
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.write("**Country Allocation Waterfall**")
            negotiation_party_options = sorted(results_df['party'].unique())
            if (
                "negotiation_target_party" not in st.session_state
                or st.session_state["negotiation_target_party"] not in negotiation_party_options
            ):
                st.session_state["negotiation_target_party"] = negotiation_party_options[0]

            target_party = st.selectbox(
                "Select Country:",
                options=negotiation_party_options,
                key="negotiation_target_party"
            )
            row = results_df[results_df['party'] == target_party].iloc[0]
            
            # We need to compute deltas for the waterfall
            is_eq = st.session_state.get("equality_mode", False)
            base_label = "Equality Base" if is_eq else "Inverted UN Scale (IUSAF) Base"
            tsac_label = "TSAC Adjustment" if not is_eq else "TSAC (0)"
            sosac_label = "SOSAC Adjustment" if not is_eq else "SOSAC (0)"

            fig = go.Figure(go.Waterfall(
                name = "Allocation", orientation = "v",
                measure = ["relative", "relative", "relative", "total"],
                x = [base_label, tsac_label, sosac_label, "Final Allocation"],
                textposition = "outside",
                text = [f"${row['component_iusaf_amt']:,.2f}m", f"${row['component_tsac_amt']:,.2f}m", f"${row['component_sosac_amt']:,.2f}m", f"${row['total_allocation']:,.2f}m"],
                y = [row['component_iusaf_amt'], row['component_tsac_amt'], row['component_sosac_amt'], 0],
                connector = {"line":{"color":"rgb(63, 63, 63)"}},
            ))
            fig.update_layout(height=400, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)

        with detail_col2:
            st.write("**How stewardship settings affect this country**")

            n_eligible_for_reference = int(results_df['eligible'].sum())
            equality_reference_m = (fund_size_usd / n_eligible_for_reference) / 1_000_000.0 if n_eligible_for_reference > 0 else 0.0

            scenario_specs = [
                ("IUSAF only", 0.00, 0.00, False),
                ("Modest stewardship", 0.05, 0.03, False),
                ("Stronger stewardship", 0.10, 0.05, False),
                ("Current setting", float(tsac_beta), float(sosac_gamma), st.session_state.get("equality_mode", False)),
            ]

            scenario_rows = []
            for scenario_name, beta_s, gamma_s, eq_mode_s in scenario_specs:
                scenario_df = calculate_allocations(
                    st.session_state.base_df,
                    fund_size_usd,
                    iplc_share,
                    False,
                    exclude_hi,
                    floor_pct=floor_pct,
                    ceiling_pct=ceiling_pct,
                    tsac_beta=beta_s,
                    sosac_gamma=gamma_s,
                    equality_mode=eq_mode_s,
                    un_scale_mode=st.session_state.get("un_scale_mode", "raw_inversion")
                )

                party_row = scenario_df[scenario_df['party'] == target_party].iloc[0]
                allocation_m = float(party_row['total_allocation'])
                diff_m = allocation_m - equality_reference_m

                eligible_rank_df = scenario_df[scenario_df['eligible']].sort_values(
                    by=['total_allocation', 'party'], ascending=[False, True]
                ).reset_index(drop=True)
                rank_series = eligible_rank_df.index[eligible_rank_df['party'] == target_party]
                rank_value = int(rank_series[0] + 1) if len(rank_series) > 0 else None

                scenario_rows.append({
                    "scenario": scenario_name,
                    "allocation_m": allocation_m,
                    "diff_from_equality_m": diff_m,
                    "rank": rank_value,
                    "country": target_party,
                })

            scenario_compare_df = pd.DataFrame(scenario_rows)

            fig = px.bar(
                scenario_compare_df,
                x='scenario',
                y='allocation_m',
                labels={'scenario': 'Scenario', 'allocation_m': 'Allocation (US$m)'},
                text=scenario_compare_df['allocation_m'].map(lambda v: f"${v:,.2f}m")
            )
            fig.update_traces(
                hovertemplate=(
                    "%{customdata[0]}<br>"
                    "Scenario: %{x}<br>"
                    "Allocation: $%{y:,.2f}m<br>"
                    "%{customdata[1]}<br>"
                    "Rank: %{customdata[2]}<extra></extra>"
                ),
                customdata=np.stack([
                    scenario_compare_df['country'],
                    scenario_compare_df['diff_from_equality_m'].map(
                        lambda d: f"{'Above' if d >= 0 else 'Below'} equality by ${abs(d):,.2f}m"
                    ),
                    scenario_compare_df['rank'].fillna('n/a').astype(str)
                ], axis=-1),
                textposition='outside'
            )
            fig.add_hline(
                y=equality_reference_m,
                line_dash='dash',
                line_color='firebrick',
                annotation_text='Equality reference',
                annotation_position='top left'
            )
            fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            current_alloc_m = float(scenario_compare_df.loc[scenario_compare_df['scenario'] == 'Current setting', 'allocation_m'].iloc[0])
            iusaf_alloc_m = float(scenario_compare_df.loc[scenario_compare_df['scenario'] == 'IUSAF only', 'allocation_m'].iloc[0])
            delta_current_vs_iusaf = current_alloc_m - iusaf_alloc_m
            st.caption(
                f"{target_party}: Current setting allocates ${current_alloc_m:,.2f}m; "
                f"IUSAF only allocates ${iusaf_alloc_m:,.2f}m "
                f"({delta_current_vs_iusaf:+,.2f}m difference)."
            )

    current_tab_idx += 1

with main_tabs[current_tab_idx]:
    st.subheader("Allocations by Country")
    # Add party status column for display
    def get_status(row):
        if not row["is_cbd_party"]:
            return "Non-Party"
        return "Party"
        
    results_df["CBD Party"] = results_df.apply(get_status, axis=1)
    
    display_cols = ['party', 'total_allocation', 'state_component', 'iplc_component', 'WB Income Group', 'UN LDC', 'CBD Party', 'EU']
    
    if show_advanced:
        # Add component shares and amounts to display
        display_cols.extend(['iusaf_share', 'tsac_share', 'sosac_share', 'component_iusaf_amt', 'component_tsac_amt', 'component_sosac_amt'])
    
    if st.session_state["un_scale_mode"] == "band_inversion":
        display_cols.extend(['un_band', 'un_band_weight'])

    if show_raw:
        st.info("""
    **How the Calculation Works (Plain Language)**

This model uses an inverted version of the UN Scale of Assessments, which is a widely used measure of countries’ relative economic capacity.

In simple terms, countries with a smaller assessed share of the UN budget receive a larger indicative share of this fund, while countries with a larger assessed share receive a smaller indicative share.

Simple examples

Country A (smaller assessed share)
Suppose Country A’s UN assessment is 0.001%. Because this is a very small assessed share, the model assigns Country A a relatively large weight, which results in a larger share of the Cali Fund.

Country B (larger assessed share)
Suppose Country B’s UN assessment is 10%. Because this is a much larger assessed share, the model assigns Country B a relatively smaller weight, which results in a smaller share of the Cali Fund.

(Behind the scenes, assessed shares are first converted from percentages into standard numerical values before being inverted. This is a technical step required for the calculation and does not affect the overall logic.)

Final step

After these weights are calculated, they are rescaled so that the total amount distributed exactly equals the fund size selected in the sidebar. Each Party’s total allocation is then divided into a State Component and an Indigenous Peoples and Local Communities (IPLC) Component according to the selected percentage.

For more detailed information see this [walkthrough](https://github.com/tierravivaai/cali-fund-allocation-model/blob/main/walkthrough.md)
    """)
        
        with st.expander("How the calculation works (technical summary)"):
            st.markdown("For each Party, the calculation proceeds in four steps:")
            
            st.markdown("""
            1. **Inversion**
            Each Party’s UN Scale of Assessments share is first converted from a percentage into a decimal (for example, 0.005% becomes 0.00005).

            The model then inverts this value by taking its reciprocal (that is, dividing 1 by the decimal value). This produces an inverse weight.

            2. **Normalisation**
            All inverse weights are summed, and each Party’s weight is divided by this total. This produces a set of shares that sum exactly to 100%.

            3. **Allocation**
            Each Party’s share is multiplied by the total fund size to determine its indicative allocation.

            4. **Earmarking**
            The allocation is then divided into a State component and an IPLC component according to the selected percentage.

            For more detailed information see this [walkthrough](https://github.com/tierravivaai/cali-fund-allocation-model/blob/main/walkthrough.md)
            """)
        
        display_cols.insert(1, 'un_share')
        display_cols.insert(2, 'inverted_share')
    
    search = st.text_input("Search Country", "")
    filtered_df = results_df[results_df['party'].str.contains(search, case=False)].copy()
    
    # Add Total row for validation
    filtered_df = add_total_row(filtered_df, "party")

    # Only apply string formatting if toggle is ON; otherwise use numeric for sorting
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component', 'component_iusaf_amt', 'component_tsac_amt', 'component_sosac_amt']:
            if col in filtered_df.columns:
                filtered_df[col] = filtered_df[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)
    
    config = {
        "eligible": None, # Hide this column
        "party": "Country",
        "un_share": st.column_config.NumberColumn("UN assessed share (%)", format="%.4f"),
        "un_share_fraction": st.column_config.NumberColumn("UN assessed share (fraction)", format="%.6f"),
        "inverted_share": st.column_config.NumberColumn("Indicative share of Cali Fund (%)", format="%.6f"),
        "iusaf_share": st.column_config.NumberColumn("IUSAF Share (%)", format="%.6f"),
        "tsac_share": st.column_config.NumberColumn("TSAC Share (%)", format="%.6f"),
        "sosac_share": st.column_config.NumberColumn("SOSAC Share (%)", format="%.6f"),
    }
    config.update(get_column_config(use_thousands, include_country_count=True))

    # Determine whether to hide index based on sorting
    # Always hide index in tab1 now that we have a Total row at the bottom
    filtered_df.insert(1, "Countries (number)", 1)
    # The total row for 'Countries (number)' will be the count of countries in the filtered list
    # but the '1' in each row serves as the counter.
    # Note: add_total_row sums the numeric columns.
    
    # Hide Countries (number) for the 'Total' row label if needed, but it's fine.
    
    st.dataframe(
        filtered_df[display_cols],
        column_config=config,
        hide_index=True,
        width="stretch"
    )

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("Totals by UN Region")

    region_df = aggregate_by_region(results_df, "region")
    region_df = region_df.sort_values("total_allocation", ascending=False)
    region_df = add_total_row(region_df, "region")

    if use_thousands:
        for col in ["total_allocation", "state_component", "iplc_component"]:
            region_df[col] = region_df[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)

    # Reorder to ensure Countries (number) is second
    display_cols_region = ["region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    st.dataframe(
        region_df[display_cols_region],
        column_config=get_column_config(use_thousands, include_country_count=True),
        hide_index=True,
        width="stretch",
    )

    # Region selector (acts as the "click Africa" interaction)
    region_list = (
        aggregate_by_region(results_df, "region")["region"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    region_list = sorted(region_list)

    selected_region = st.selectbox(
        "Show countries in region",
        options=region_list,
        index=0,
        key="selected_region",
    )

    region_countries = results_df[results_df["region"] == selected_region].copy()

    if sort_option == "Allocation (highest first)":
        region_countries = region_countries.sort_values(
            by=["total_allocation", "party"],
            ascending=[False, True],
        ).reset_index(drop=True)
        region_countries.index = region_countries.index + 1
        region_countries.index.name = "Rank"
        hide_index = False
    else:
        region_countries = region_countries.sort_values(
            by="party",
            ascending=True,
        ).reset_index(drop=True)
        hide_index = True

    display_cols_reg = ["party", "total_allocation", "state_component", "iplc_component", "WB Income Group", "UN LDC", "EU"]
    if st.session_state["un_scale_mode"] == "band_inversion":
        display_cols_reg.extend(['un_band', 'un_band_weight'])

    if use_thousands:
        for col in ["total_allocation", "state_component", "iplc_component"]:
            region_countries[col] = region_countries[col].apply(format_currency)

    config = {"party": "Country"}
    config.update(get_column_config(use_thousands))

    st.dataframe(
        region_countries[display_cols_reg],
        column_config=config,
        hide_index=hide_index,
        width="stretch",
    )

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("Totals by UN Sub-region")
    sub_region_df = aggregate_by_region(results_df, 'sub_region')
    sub_region_df = sub_region_df.sort_values('total_allocation', ascending=False)
    sub_region_df = add_total_row(sub_region_df, "sub_region")
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            sub_region_df[col] = sub_region_df[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)
            
    display_cols_sub = ["sub_region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    st.dataframe(
        sub_region_df[display_cols_sub],
        column_config=get_column_config(use_thousands, include_country_count=True),
        hide_index=True,
        width="stretch"
    )

    # Sub-region selector
    sub_region_list = (
        aggregate_by_region(results_df, "sub_region")["sub_region"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    sub_region_list = sorted(sub_region_list)

    selected_sub_region = st.selectbox(
        "Show countries in sub-region",
        options=sub_region_list,
        index=0,
        key="selected_sub_region",
    )

    sub_region_countries = results_df[results_df["sub_region"] == selected_sub_region].copy()

    if sort_option == "Allocation (highest first)":
        sub_region_countries = sub_region_countries.sort_values(
            by=["total_allocation", "party"],
            ascending=[False, True],
        ).reset_index(drop=True)
        sub_region_countries.index = sub_region_countries.index + 1
        sub_region_countries.index.name = "Rank"
        hide_index = False
    else:
        sub_region_countries = sub_region_countries.sort_values(
            by="party",
            ascending=True,
        ).reset_index(drop=True)
        hide_index = True

    display_cols_sub_detail = ["party", "total_allocation", "state_component", "iplc_component", "WB Income Group", "UN LDC", "EU"]
    if st.session_state["un_scale_mode"] == "band_inversion":
        display_cols_sub_detail.extend(['un_band', 'un_band_weight'])

    if use_thousands:
        for col in ["total_allocation", "state_component", "iplc_component"]:
            sub_region_countries[col] = sub_region_countries[col].apply(format_currency)

    config = {"party": "Country"}
    config.update(get_column_config(use_thousands))

    st.dataframe(
        sub_region_countries[display_cols_sub_detail],
        column_config=config,
        hide_index=hide_index,
        width="stretch",
    )

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("Totals by UN Intermediate Region")
    # Include all countries, including those with 'NA' intermediate_region
    # but rename 'NA' for clearer display
    int_region_df = aggregate_by_region(results_df, 'intermediate_region')
    int_region_df['intermediate_region'] = int_region_df['intermediate_region'].replace('NA', 'Not Categorized')
    
    int_region_df = int_region_df.sort_values('total_allocation', ascending=False)
    int_region_df = add_total_row(int_region_df, "intermediate_region")
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            int_region_df[col] = int_region_df[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)
            
    display_cols_int = ["intermediate_region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    st.dataframe(
        int_region_df[display_cols_int],
        column_config=get_column_config(use_thousands, include_country_count=True),
        hide_index=True,
        width="stretch"
    )

    # Intermediate region selector
    int_region_list = (
        aggregate_by_region(results_df, "intermediate_region")["intermediate_region"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    int_region_list = sorted(int_region_list)

    if int_region_list:
        selected_int_region = st.selectbox(
            "Show countries in intermediate region",
            options=int_region_list,
            index=0,
            key="selected_int_region",
        )

        int_region_countries = results_df[results_df["intermediate_region"] == selected_int_region].copy()

        if sort_option == "Allocation (highest first)":
            int_region_countries = int_region_countries.sort_values(
                by=["total_allocation", "party"],
                ascending=[False, True],
            ).reset_index(drop=True)
            int_region_countries.index = int_region_countries.index + 1
            int_region_countries.index.name = "Rank"
            hide_index = False
        else:
            int_region_countries = int_region_countries.sort_values(
                by="party",
                ascending=True,
            ).reset_index(drop=True)
            hide_index = True

        display_cols_int_detail = ["party", "total_allocation", "state_component", "iplc_component", "WB Income Group", "UN LDC", "EU"]
        if st.session_state["un_scale_mode"] == "band_inversion":
            display_cols_int_detail.extend(['un_band', 'un_band_weight'])

        if use_thousands:
            for col in ["total_allocation", "state_component", "iplc_component"]:
                int_region_countries[col] = int_region_countries[col].apply(format_currency)

        config = {"party": "Country"}
        config.update(get_column_config(use_thousands))

        st.dataframe(
            int_region_countries[display_cols_int_detail],
            column_config=config,
            hide_index=hide_index,
            width="stretch",
        )

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("Totals by World Bank Income Group")
    income_df = aggregate_by_income(results_df)
    income_df = income_df.sort_values('total_allocation', ascending=False)
    income_df = add_total_row(income_df, "WB Income Group")
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            income_df[col] = income_df[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)
    
    config = {"WB Income Group": "Income Group"}
    config.update(get_column_config(use_thousands, include_country_count=True))
    
    display_cols_income = ['WB Income Group', 'Countries (number)', 'total_allocation', 'state_component', 'iplc_component']
    st.dataframe(
        income_df[display_cols_income],
        column_config=config,
        hide_index=True,
        width="stretch"
    )

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("LDC Share")
    st.markdown("Least Developed Countries (LDCs) are low-income countries as defined by the UN Committee for Development Policy (CDP) as described [here](https://policy.desa.un.org/least-developed-countries). There are currently 44 LDCs.")
    ldc_total, _ = aggregate_special_groups(results_df)
    
    # Calculate non-LDC (broadly 'Developed/Other')
    # To sum to 196, we count ALL CBD parties NOT in LDC group
    mask_cbd = results_df['is_cbd_party']
    non_ldc_df = results_df[mask_cbd & (~results_df['is_ldc'])]
    non_ldc_total = non_ldc_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    non_ldc_count = len(non_ldc_df)
    
    summary_data = pd.DataFrame([
        {"Group": "Least Developed Countries (LDC)", "Countries (number)": ldc_total['Countries (number)'], **ldc_total.drop('Countries (number)').to_dict()},
        {"Group": "Other Countries", "Countries (number)": non_ldc_count, **non_ldc_total.to_dict()}
    ])
    summary_data = add_total_row(summary_data, "Group")

    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            summary_data[col] = summary_data[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)
    
    display_cols_summary = ["Group", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    st.dataframe(
        summary_data[display_cols_summary],
        column_config=get_column_config(use_thousands, include_country_count=True),
        hide_index=True,
        width="stretch"
    )

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("Small Island Developing States (SIDS)")
    _, sids_total = aggregate_special_groups(results_df)
    
    # Calculate non-SIDS
    mask_cbd = results_df['is_cbd_party']
    non_sids_df = results_df[mask_cbd & (~results_df['is_sids'])]
    non_sids_total = non_sids_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    non_sids_count = len(non_sids_df)
    
    summary_data_sids = pd.DataFrame([
        {"Group": "Small Island Developing States (SIDS)", "Countries (number)": sids_total['Countries (number)'], **sids_total.drop('Countries (number)').to_dict()},
        {"Group": "Other Countries", "Countries (number)": non_sids_count, **non_sids_total.to_dict()}
    ])
    summary_data_sids = add_total_row(summary_data_sids, "Group")
    
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            summary_data_sids[col] = summary_data_sids[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)
            
    display_cols_summary_sids = ["Group", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    st.dataframe(
        summary_data_sids[display_cols_summary_sids],
        column_config=get_column_config(use_thousands, include_country_count=True),
        hide_index=True,
        width="stretch"
    )

    # SIDS Detail Selector
    st.divider()
    sids_group_option = st.selectbox(
        "Show countries in group",
        options=["Small Island Developing States (SIDS)", "Other Countries"],
        index=0,
        key="selected_sids_group"
    )

    if sids_group_option == "Small Island Developing States (SIDS)":
        sids_filtered_df = results_df[results_df["is_sids"]].copy()
    else:
        sids_filtered_df = results_df[mask_cbd & (~results_df["is_sids"])].copy()

    if sort_option == "Allocation (highest first)":
        sids_filtered_df = sids_filtered_df.sort_values(
            by=["total_allocation", "party"],
            ascending=[False, True],
        ).reset_index(drop=True)
        sids_filtered_df.index = sids_filtered_df.index + 1
        sids_filtered_df.index.name = "Rank"
        hide_index = False
    else:
        sids_filtered_df = sids_filtered_df.sort_values(
            by="party",
            ascending=True,
        ).reset_index(drop=True)
        hide_index = True

    display_cols = ["party", "total_allocation", "state_component", "iplc_component", "WB Income Group", "UN LDC", "EU"]
    sids_display_df = sids_filtered_df[display_cols].copy()
    
    # Add Countries (number) dummy column and Total row
    sids_display_df.insert(1, "Countries (number)", 1)
    sids_display_df = add_total_row(sids_display_df, "party")

    if use_thousands:
        for col in ["total_allocation", "state_component", "iplc_component"]:
            sids_display_df[col] = sids_display_df[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)

    config = {"party": "Country"}
    config.update(get_column_config(use_thousands, include_country_count=True))

    st.dataframe(
        sids_display_df,
        column_config=config,
        hide_index=True,
        width="stretch",
    )

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("Low Income Countries")
    li_df = results_df[results_df['WB Income Group'] == 'Low income'].copy()
    
    display_li_df = li_df.copy()
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            display_li_df[col] = display_li_df[col].apply(format_currency)

    config = {
        "party": "Country",
        "WB Income Group": "WB Classification"
    }
    config.update(get_column_config(use_thousands, include_country_count=True))

    li_total = li_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    li_count = len(li_df)
    
    display_cols_li = ['party', 'total_allocation', 'state_component', 'iplc_component', 'WB Income Group', 'UN LDC']
    if st.session_state["un_scale_mode"] == "band_inversion":
        display_cols_li.extend(['un_band', 'un_band_weight'])
        
    li_table = display_li_df[display_cols_li].sort_values('party')
    # Add country count for every row (1) so it sums correctly in Total row
    li_table.insert(1, "Countries (number)", 1)
    li_table = add_total_row(li_table, "party")

    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
             li_table[col] = li_table[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)

    st.dataframe(
        li_table,
        column_config=config,
        hide_index=True,
        width="stretch"
    )
    st.metric("Low Income Total Allocation", format_currency(li_total['total_allocation']))
    col1, col2 = st.columns(2)
    col1.metric("Low Income State Component", format_currency(li_total['state_component']))
    col2.metric("Low Income IPLC Component", format_currency(li_total['iplc_component']))

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("Middle Income Countries")
    mi_df = results_df[results_df['WB Income Group'].isin(['Lower middle income', 'Upper middle income'])].copy()
    
    display_mi_df = mi_df.copy()
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            display_mi_df[col] = display_mi_df[col].apply(format_currency)

    config = {
        "party": "Country",
        "WB Income Group": "WB Classification"
    }
    config.update(get_column_config(use_thousands, include_country_count=True))

    mi_total = mi_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    mi_count = len(mi_df)
    
    display_cols_mi = ['party', 'total_allocation', 'state_component', 'iplc_component', 'UN LDC', 'WB Income Group']
    if st.session_state["un_scale_mode"] == "band_inversion":
        display_cols_mi.extend(['un_band', 'un_band_weight'])
    
    mi_table = display_mi_df[display_cols_mi].sort_values('party')
    mi_table.insert(1, "Countries (number)", 1)
    mi_table = add_total_row(mi_table, "party")

    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            mi_table[col] = mi_table[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)

    st.dataframe(
        mi_table,
        column_config=config,
        hide_index=True,
        width="stretch"
    )
    st.metric("Middle Income Countries Total Allocation", format_currency(mi_total['total_allocation']))
    col1, col2 = st.columns(2)
    col1.metric("Middle Income State Component", format_currency(mi_total['state_component']))
    col2.metric("Middle Income IPLC Component", format_currency(mi_total['iplc_component']))

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("High Income Countries")
    hi_df = results_df[results_df['WB Income Group'] == 'High income'].copy()
    
    display_hi_df = hi_df.copy()
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            display_hi_df[col] = display_hi_df[col].apply(format_currency)

    config = {"party": "Country"}
    config.update(get_column_config(use_thousands, include_country_count=True))

    hi_total = hi_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    hi_count = len(hi_df)
    
    display_cols_hi = ['party', 'total_allocation', 'state_component', 'iplc_component', 'EU']
    if st.session_state["un_scale_mode"] == "band_inversion":
        display_cols_hi.extend(['un_band', 'un_band_weight'])

    hi_table = display_hi_df[display_cols_hi].sort_values('party')
    hi_table.insert(1, "Countries (number)", 1)
    hi_table = add_total_row(hi_table, "party")

    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            hi_table[col] = hi_table[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)

    st.dataframe(
        hi_table,
        column_config=config,
        hide_index=True,
        width="stretch"
    )
    st.metric("High Income Total Allocation", format_currency(hi_total['total_allocation']))
    col1, col2 = st.columns(2)
    col1.metric("High Income State Component", format_currency(hi_total['state_component']))
    col2.metric("High Income IPLC Component", format_currency(hi_total['iplc_component']))

current_tab_idx += 1
with main_tabs[current_tab_idx]:
    st.subheader("Comparison: Raw Inversion vs Band-based Inversion")
    
    # Calculate both modes for comparison
    comp_raw = calculate_allocations(
        st.session_state.base_df, fund_size_usd, iplc_share, False, exclude_hi, 
        floor_pct, ceiling_pct, tsac_beta, sosac_gamma, equality_mode=False, un_scale_mode="raw_inversion"
    )
    comp_band = calculate_allocations(
        st.session_state.base_df, fund_size_usd, iplc_share, False, exclude_hi, 
        floor_pct, ceiling_pct, tsac_beta, sosac_gamma, equality_mode=False, un_scale_mode="band_inversion"
    )
    
    # Equal share reference
    n_eligible = results_df['eligible'].sum()
    equal_share_m = (fund_size_usd / n_eligible) / 1_000_000 if n_eligible > 0 else 0
    
    # Merge for comparison
    m_comp = comp_raw[['party', 'un_share', 'total_allocation', 'eligible']].rename(columns={'total_allocation': 'raw_amt'})
    m_comp['band_amt'] = comp_band['total_allocation']
    m_comp['un_band'] = comp_band['un_band']
    m_comp['diff_amt'] = m_comp['band_amt'] - m_comp['raw_amt']
    m_comp['equal_share'] = equal_share_m
    
    # Filter for eligible only
    m_comp = m_comp[m_comp['eligible']].copy()
    
    # Stats
    above_raw = (m_comp['raw_amt'] > equal_share_m).sum()
    above_band = (m_comp['band_amt'] > equal_share_m).sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Parties (n)", int(n_eligible))
    c2.metric("Above Equal Share (Raw)", int(above_raw))
    c3.metric("Above Equal Share (Band)", int(above_band))
    c4.metric("Equal Share Reference", f"${equal_share_m:.2f}m")
    
    st.divider()
    
    # Charts
    chart_c1, chart_c2 = st.columns(2)
    with chart_c1:
        st.write(f"**{n_eligible} Countries Above/Below Equal Share**")
        status_data = pd.DataFrame({
            'Method': ['Raw Inversion', 'Raw Inversion', 'Band-based', 'Band-based'],
            'Status': ['Above', 'Below', 'Above', 'Below'],
            'Count': [above_raw, len(m_comp) - above_raw, above_band, len(m_comp) - above_band]
        })
        fig_status = px.bar(status_data, x='Method', y='Count', color='Status', barmode='group')
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)
        
    with chart_c2:
        st.write("**Top 10 Gaining from Banding (US$m)**")
        gaining = m_comp.sort_values('diff_amt', ascending=False).head(10).copy()
        fig_gain = px.bar(gaining, x='diff_amt', y='party', orientation='h', labels={'diff_amt': 'Gain (US$m)', 'party': 'Country'})
        fig_gain.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
        st.plotly_chart(fig_gain, use_container_width=True)
        
    st.write("**Comparison Table**")
    m_comp['diff_from_equal_raw'] = m_comp['raw_amt'] - equal_share_m
    m_comp['diff_from_equal_band'] = m_comp['band_amt'] - equal_share_m
    
    st.dataframe(
        m_comp[['party', 'un_share', 'un_band', 'raw_amt', 'band_amt', 'equal_share', 'diff_from_equal_raw', 'diff_from_equal_band']],
        column_config={
            "party": "Country",
            "un_share": st.column_config.NumberColumn("UN Share (%)", format="%.4f"),
            "raw_amt": st.column_config.NumberColumn("Raw Allocation (m)", format="$%.2f"),
            "band_amt": st.column_config.NumberColumn("Band Allocation (m)", format="$%.2f"),
            "equal_share": st.column_config.NumberColumn("Equal Share (m)", format="$%.2f"),
            "diff_from_equal_raw": st.column_config.NumberColumn("Diff (Raw - Equal)", format="$%.2f"),
            "diff_from_equal_band": st.column_config.NumberColumn("Diff (Band - Equal)", format="$%.2f"),
        },
        hide_index=True,
        width="stretch"
    )

st.divider()
st.markdown("""
**Notes**  
The allocations shown are indicative and are generated using an inverted [UN Scale of Assessments](https://digitallibrary.un.org/record/4071844?ln=en&utm_source=chatgpt.com&v=pdf#files) for the years 2025-2027 to support discussion. Definitions of UN regions, Least developed countries (LDC) and Small Island Developing States (SIDS) are from the [UNSD M49](https://unstats.un.org/unsd/methodology/m49/) standard. [World Bank Income Classification groups](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups) are shown to assist with interpretation and to enable the ability to toggle high income (developed) countries on or off in calculations.

The Terrestrial Stewardship Allocation Component (TSAC) is calculated as the country share of the total Land Area in the FAOSTAT Land Area (Square km) table  for 1961-2023 on 2023 values available from the [World Bank Indicators Databank](https://data.worldbank.org/indicator/AG.LND.TOTL.K2).

The SIDS Ocean Stewardship Allocation Component (SOSAC) is calculated as an equal-share pool across all eligible SIDS Parties using the UNSD M49 SIDS classification. In practice, each eligible SIDS receives an equal share (`1 / number of eligible SIDS`) weighted by the SOSAC slider value. If no eligible SIDS are present, the SOSAC weight is reallocated to the IUSAF base.

---
Prepared by Paul Oldham [TierraViva AI](https://www.tierraviva.ai/). Developed with Droid by [Factory AI](https://factory.ai/). Source code available on [Github](https://github.com/tierravivaai/cali-fund-allocation-model)
""")
