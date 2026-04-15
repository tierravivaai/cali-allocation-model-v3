#!/usr/bin/env python3
"""
Generate two distribution plots of the UN Scale of Assessments (2027):

  Fig 1: All countries with non-zero shares (baseline skew)
  Fig 2: CBD Parties with High Income excluded (exclude_except_sids mode)

Uses the model's own data loading pipeline (data_loader.py) to ensure
consistent Party lists, name mapping, and income classification.

Output:
  - SVG figures
  - CSV data files
  - README.md metadata
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os
import sys
import duckdb
from datetime import datetime, timezone

# --- Paths ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_RAW = os.path.join(PROJECT_ROOT, "data-raw")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# --- Source file paths ---
UN_SCALE_CSV = os.path.join(DATA_RAW, "UNGA_scale_of_assessment.csv")
CBD_BUDGET_CSV = os.path.join(DATA_RAW, "cbd_cop16_budget_table.csv")
WB_INCOME_CSV = os.path.join(DATA_RAW, "world_bank_income_class.csv")
UNSD_REGIONS_CSV = os.path.join(DATA_RAW, "unsd_region_useme.csv")
NAME_MAP_CSV = os.path.join(DATA_RAW, "manual_name_map.csv")

# Use the model's own data loading pipeline for consistency
sys.path.insert(0, SRC_DIR)
from cali_model.data_loader import load_data, get_base_data


def load_model_data():
    """Load data using the model's own pipeline (ensures consistent Party list)."""
    con = duckdb.connect()
    load_data(con)
    df = get_base_data(con)
    con.close()
    return df


def build_full_distribution(df):
    """Fig 1 data: all countries with non-zero 2027 UN share."""
    result = df[df["un_share"] > 0][["party", "un_share"]].copy()
    result = result.rename(columns={"party": "party_name"})
    return result.reset_index(drop=True)


def build_filtered_distribution(df):
    """Fig 2 data: CBD Parties, exclude high income except SIDS.

    Replicates calculator.py: exclude_high_income=True,
    high_income_mode="exclude_except_sids"
    """
    eligible = df["is_cbd_party"] & ~(
        (df["WB Income Group"] == "High income") & (df["is_sids"] == False)
    )
    result = df[eligible][["party", "un_share"]].copy()
    result = result.rename(columns={"party": "party_name"})
    return result.reset_index(drop=True)


def plot_distribution(shares, title, filename, color="#3B82F6"):
    """Create a bar chart with percentage bands on x-axis and party counts on y-axis."""
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")

    n_total = len(shares)
    n_zero = int((shares["un_share"] == 0).sum())
    nonzero = shares[shares["un_share"] > 0]["un_share"].values

    # 6 bands aligned with config/un_scale_bands.yaml
    # Repo convention: > min_threshold and <= max_threshold
    bands = [
        (-0.0001, 0.001, "≤ 0.001%"),
        (0.001, 0.01, "0.001–0.01%"),
        (0.01, 0.1, "0.01–0.1%"),
        (0.1, 1.0, "0.1–1%"),
        (1.0, 10.0, "1–10%"),
        (10.0, 100.0, "> 10%"),
    ]

    labels = []
    counts = []
    all_shares = shares["un_share"].values
    for lo, hi, label in bands:
        count = int(np.sum((all_shares > lo) & (all_shares <= hi)))
        labels.append(label)
        counts.append(count)

    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, counts, color=color, edgecolor="white", width=0.7, alpha=0.85)

    # Add count labels on top of bars
    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            str(count),
            ha="center", va="bottom", fontsize=10, fontweight="bold", color="#333333"
        )

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_xlabel("UN Scale of Assessment Share (%)", fontsize=11)
    ax.set_ylabel("Number of Parties", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_ylim(0, max(counts) * 1.15)

    # Summary stats annotation
    stats_lines = [f"N = {n_total}"]
    if n_zero > 0:
        stats_lines.append(f"({n_zero} with 0% share)")
    stats_lines.append(f"Median = {np.median(nonzero):.4f}%")
    stats_lines.append(f"Top 10 = {np.sum(np.sort(nonzero)[-10:]):.1f}% of total")
    stats_text = "\n".join(stats_lines)
    ax.text(
        0.97, 0.75, stats_text, transform=ax.transAxes,
        fontsize=9, verticalalignment="top", horizontalalignment="right",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#F0F0F0", alpha=0.9)
    )

    plt.tight_layout()
    svg_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(svg_path, format="svg", bbox_inches="tight", facecolor="white")
    png_path = os.path.splitext(svg_path)[0] + ".png"
    plt.savefig(png_path, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved: {svg_path}")
    print(f"Saved: {png_path}")
    return svg_path


def compute_raw_inversion(shares):
    """Compute raw IUSAF inversion: inv_weight = 1 / (un_share/100), normalised.

    Replicates calculator.py raw_inversion logic:
      inv_weight = 1 / (un_share / 100) for un_share > 0
      iusaf_share = 0 for un_share == 0
      Normalise so iusaf_share sums to 1.0 (as fraction, multiply by 100 for %)
    """
    data = shares[shares["party_name"] != "European Union"].copy()
    data = data.sort_values("un_share", ascending=False).reset_index(drop=True)

    iusaf_share = pd.Series(0.0, index=data.index)
    nonzero = data["un_share"] > 0
    inv_weight = 1.0 / (data.loc[nonzero, "un_share"] / 100.0)
    iusaf_share.loc[nonzero] = (inv_weight / inv_weight.sum()) * 100.0

    data["iusaf_share"] = iusaf_share
    # Re-sort by IUSAF share descending for the ranked chart
    data = data.sort_values("iusaf_share", ascending=False).reset_index(drop=True)
    return data


def plot_distribution_5band(shares, title, filename, color="#3B82F6"):
    """5-band bar chart — original structure with China grouped in Band 5 (1–10%)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")

    n_total = len(shares)
    n_zero = int((shares["un_share"] == 0).sum())
    nonzero = shares[shares["un_share"] > 0]["un_share"].values

    bands = [
        (-0.0001, 0.001, "≤ 0.001%"),
        (0.001, 0.01, "0.001–0.01%"),
        (0.01, 0.1, "0.01–0.1%"),
        (0.1, 1.0, "0.1–1%"),
        (1.0, 100.0, "1–10%+"),
    ]

    labels = []
    counts = []
    all_shares = shares["un_share"].values
    for lo, hi, label in bands:
        count = int(np.sum((all_shares > lo) & (all_shares <= hi)))
        labels.append(label)
        counts.append(count)

    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, counts, color=color, edgecolor="white", width=0.7, alpha=0.85)

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            str(count),
            ha="center", va="bottom", fontsize=10, fontweight="bold", color="#333333"
        )

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_xlabel("UN Scale of Assessment Share (%)", fontsize=11)
    ax.set_ylabel("Number of Parties", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_ylim(0, max(counts) * 1.15)

    stats_lines = [f"N = {n_total}"]
    if n_zero > 0:
        stats_lines.append(f"({n_zero} with 0% share)")
    stats_lines.append(f"Median = {np.median(nonzero):.4f}%")
    stats_text = "\n".join(stats_lines)
    ax.text(
        0.97, 0.85, stats_text, transform=ax.transAxes,
        fontsize=9, verticalalignment="top", horizontalalignment="right",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#F0F0F0", alpha=0.9)
    )

    plt.tight_layout()
    svg_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(svg_path, format="svg", bbox_inches="tight", facecolor="white")
    png_path = os.path.splitext(svg_path)[0] + ".png"
    plt.savefig(png_path, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved: {svg_path}")
    print(f"Saved: {png_path}")
    return svg_path


def save_csv(data, filename):
    csv_path = os.path.join(OUTPUT_DIR, filename)
    data.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}")
    return csv_path


def plot_ranked_bars(shares, title, filename, color="#6366F1", value_col="un_share", y_label="UN Scale of Assessment Share (%)"):
    """Create a ranked bar chart: each Party as one bar, sorted highest to lowest."""
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor("white")

    # Filter out EU, keep zero-rated Parties
    plot_data = shares[shares["party_name"] != "European Union"].copy()
    plot_data = plot_data.sort_values(value_col, ascending=False).reset_index(drop=True)

    n_total = len(plot_data)
    x_pos = np.arange(n_total)
    values = plot_data[value_col].values

    ax.bar(x_pos, values, color=color, edgecolor="none", width=0.85, alpha=0.85)

    ax.set_xlim(-0.5, n_total - 0.5)
    ax.set_xlabel(f"Parties ranked by share (N={n_total})", fontsize=11)
    ax.set_ylabel(y_label, fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)

    # Remove x-axis tick labels (no country names)
    ax.set_xticks([])

    plt.tight_layout()
    svg_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(svg_path, format="svg", bbox_inches="tight", facecolor="white")
    png_path = os.path.splitext(svg_path)[0] + ".png"
    plt.savefig(png_path, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved: {svg_path}")
    print(f"Saved: {png_path}")
    return svg_path


def plot_ranked_bars_two_panel(shares, title, filename, color="#6366F1", zoom_ymax=1.5, value_col="un_share", y_label="UN Scale Share (%)"):
    """Two-panel ranked bar chart: top = full range, bottom = zoomed into lower end."""
    plot_data = shares[shares["party_name"] != "European Union"].copy()
    plot_data = plot_data.sort_values(value_col, ascending=False).reset_index(drop=True)

    n_total = len(plot_data)
    x_pos = np.arange(n_total)
    values = plot_data[value_col].values

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(8, 8), sharex=True,
        gridspec_kw={"height_ratios": [1, 1.2]}
    )
    fig.patch.set_facecolor("white")

    # Top panel: full range
    ax_top.bar(x_pos, values, color=color, edgecolor="none", width=0.85, alpha=0.85)
    ax_top.set_xlim(-0.5, n_total - 0.5)
    ax_top.set_ylabel(y_label, fontsize=10)
    ax_top.set_title(title, fontsize=11, fontweight="bold")
    ax_top.grid(True, axis="y", alpha=0.3)
    ax_top.set_xticks([])

    # Bottom panel: zoomed into lower end
    ax_bot.bar(x_pos, values, color=color, edgecolor="none", width=0.85, alpha=0.85)
    ax_bot.set_xlim(-0.5, n_total - 0.5)
    ax_bot.set_ylim(0, zoom_ymax)
    ax_bot.set_xlabel(f"Parties ranked by share (N={n_total})", fontsize=10)
    ax_bot.set_ylabel(y_label, fontsize=10)
    ax_bot.grid(True, axis="y", alpha=0.3)
    ax_bot.set_xticks([])
    # Zoom label
    ax_bot.text(
        0.99, 0.97, f"Zoomed: 0–{zoom_ymax}%",
        transform=ax_bot.transAxes, fontsize=9,
        verticalalignment="top", horizontalalignment="right",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#F0F0F0", alpha=0.8)
    )

    plt.tight_layout(h_pad=1.5)
    svg_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(svg_path, format="svg", bbox_inches="tight", facecolor="white")
    png_path = os.path.splitext(svg_path)[0] + ".png"
    plt.savefig(png_path, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved: {svg_path}")
    print(f"Saved: {png_path}")
    return svg_path


def generate_readme(fig1_data, fig2_data, fig1_path, fig2_path, fig1_csv, fig2_csv):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    import matplotlib
    mpl_version = matplotlib.__version__
    pd_version = pd.__version__
    np_version = np.__version__

    content = f"""# UN Scale of Assessment 2027 — Distribution Figures

Generated: {now}
Project: Cali Allocation Model (Inverted UN Scale Option)

---

## Figure 1: Full Distribution (All Countries)

- **File**: `{os.path.basename(fig1_path)}`
- **Data**: `{os.path.basename(fig1_csv)}`
- **Source**: `{UN_SCALE_CSV}` (column: 2027)
- **Filter**: All countries with non-zero 2027 UN share (N={len(fig1_data)})
- **Chart type**: Log-scale histogram
- **Packages**: matplotlib {mpl_version}, pandas {pd_version}, numpy {np_version}

### Key statistics
- Min: {fig1_data['un_share'].min():.4f}%
- Max: {fig1_data['un_share'].max():.4f}%
- Median: {fig1_data['un_share'].median():.4f}%
- Top 10 countries hold {fig1_data.nlargest(10, 'un_share')['un_share'].sum():.1f}% of total shares

---

## Figure 2: CBD Parties (High Income Excluded, SIDS Preserved)

- **File**: `{os.path.basename(fig2_path)}`
- **Data**: `{os.path.basename(fig2_csv)}`
- **Source data**:
  - UN Scale: `{UN_SCALE_CSV}` (column: 2027)
  - CBD Parties: `{CBD_BUDGET_CSV}`
  - Income groups: `{WB_INCOME_CSV}`
  - SIDS flag: `{UNSD_REGIONS_CSV}`
  - Name mapping: `{NAME_MAP_CSV}`
- **Filter**: CBD Parties, exclude High income except SIDS
  (replicates calculator.py: `exclude_high_income=True, high_income_mode="exclude_except_sids"`)
- **N = {len(fig2_data)}** eligible Parties ({int((fig2_data['un_share'] == 0).sum())} with 0% UN share)
- **Chart type**: Log-scale histogram
- **Packages**: matplotlib {mpl_version}, pandas {pd_version}, numpy {np_version}

### Key statistics
- Min: {fig2_data['un_share'].min():.4f}%
- Max: {fig2_data['un_share'].max():.4f}%
- Median: {fig2_data['un_share'].median():.4f}%
- Top 10 countries hold {fig2_data.nlargest(10, 'un_share')['un_share'].sum():.1f}% of total shares

---

## Regeneration

Run from project root:
```
python figures/un_scale_distribution/generate_plots.py
```
"""
    readme_path = os.path.join(OUTPUT_DIR, "README.md")
    with open(readme_path, "w") as f:
        f.write(content)
    print(f"Saved: {readme_path}")


if __name__ == "__main__":
    print("Loading model data via cali_model.data_loader...")
    df = load_model_data()

    print("Building Figure 1: Full UN Scale distribution...")
    fig1_data = build_full_distribution(df)
    fig1_path = plot_distribution(
        fig1_data,
        "Distribution of UN Scale of Assessment Shares (2027)\nAll countries with non-zero share",
        "fig_1_full_distribution.svg",
        color="#3B82F6",
    )
    fig1_csv = save_csv(fig1_data, "fig_1_full_distribution.csv")

    print("\nBuilding Figure 2: CBD Parties (High Income excluded)...")
    fig2_data = build_filtered_distribution(df)
    fig2_path = plot_distribution(
        fig2_data,
        "Distribution of UN Scale of Assessment Shares (2027)\nCBD Parties — High income excluded (SIDS preserved)",
        "fig_2_non_high_income.svg",
        color="#22C55E",
    )
    fig2_csv = save_csv(fig2_data, "fig_2_non_high_income.csv")

    print("\nBuilding Figure 2b: 5-band distribution (China in Band 5)...")
    fig2b_path = plot_distribution_5band(
        fig2_data,
        "Distribution of UN Scale of Assessment Shares (2027)\nCBD Parties — 5-band structure (China grouped with Band 5)",
        "fig_2b_5band.svg",
        color="#22C55E",
    )

    no_top = fig2_data[fig2_data["party_name"] != "China"].copy()

    # --- Raw inversion of UN Scale ---
    print("\nComputing raw IUSAF inversion...")
    iusaf_data = compute_raw_inversion(fig2_data)

    print("\nBuilding Figure 5: IUSAF ranked bars (142 eligible Parties)...")
    fig5_path = plot_ranked_bars(
        iusaf_data,
        "Inverted UN Scale (IUSAF) Shares — Raw Inversion (2027)\nCBD Parties (High income excluded, SIDS preserved)",
        "fig_5_iusaf_ranked.svg",
        color="#059669",
        value_col="iusaf_share",
        y_label="IUSAF Share (%)",
    )
    fig5_csv = save_csv(iusaf_data, "fig_5_iusaf_ranked.csv")

    print("\nBuilding Figure 3: Two-panel ranked bars (142 eligible Parties)...")
    fig3_path = plot_ranked_bars_two_panel(
        fig2_data,
        "UN Scale of Assessment Shares (2027)\nCBD Parties (High income excluded, SIDS preserved)",
        "fig_3_two_panel_ranked.svg",
        color="#6366F1",
        zoom_ymax=1.5,
    )

    print("\nBuilding Figure 4: Two-panel ranked bars without top contributor...")
    fig4_path = plot_ranked_bars_two_panel(
        no_top,
        "UN Scale of Assessment Shares (2027) — Without Top Contributor\nCBD Parties (High income excluded, SIDS preserved)",
        "fig_4_two_panel_ranked_no_top.svg",
        color="#8B5CF6",
        zoom_ymax=1.5,
    )

    print("\nGenerating README.md...")
    generate_readme(fig1_data, fig2_data, fig1_path, fig2_path, fig1_csv, fig2_csv)

    print("\nDone.")
