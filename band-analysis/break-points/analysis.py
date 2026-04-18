#!/usr/bin/env python3
"""
Break Points Analysis: Compute crossover points and generate visualizations.

This script:
1. Computes TSAC overturn point (where TSAC overtakes IUSAF)
2. Computes SOSAC overturn point (where SOSAC overtakes IUSAF for SIDS)
3. Generates allocations for 6 key scenarios
4. Creates visualizations showing decision boundaries
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from typing import Tuple, Dict, Optional

from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations
from cali_model.sensitivity_metrics import compute_gini


# ============================================================================
# Configuration
# ============================================================================

FUND_SIZE = 1_000_000_000
IPLC_SHARE_PCT = 50
EXCLUDE_HIGH_INCOME = True
UN_SCALE_MODE = "band_inversion"
SOSAC_GAMMA_DEFAULT = 0.03

# DEPRECATED: The 0.85 Spearman threshold was replaced by Option D (band-order preservation
# + Spearman safety floor 0.80) in v4.0. See docs/spearman-threshold-assessment.md.
SPEARMAN_SAFETY_FLOOR = 0.80

# Output directory
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================================
# Helper Functions
# ============================================================================

def compute_spearman_vs_iusaf(current: pd.DataFrame, baseline: pd.DataFrame) -> float:
    """Compute Spearman rank correlation between current and baseline allocations."""
    cur = current[current['eligible']].copy()
    base = baseline[baseline['eligible']].copy()
    
    merged = cur[['party', 'final_share']].merge(
        base[['party', 'final_share']], on='party', how='inner', suffixes=('_cur', '_base')
    )
    
    if merged.empty:
        return float('nan')
    
    r_cur = merged['final_share_cur'].rank(method='average')
    r_base = merged['final_share_base'].rank(method='average')
    
    if r_cur.nunique() <= 1 or r_base.nunique() <= 1:
        return 1.0 if merged['final_share_cur'].round(12).equals(merged['final_share_base'].round(12)) else 0.0
    
    return float(r_cur.corr(r_base, method='pearson'))


def compute_component_ratios(df: pd.DataFrame, beta: float, gamma: float) -> pd.DataFrame:
    """Compute TSAC/IUSAF and SOSAC/IUSAF ratios for each Party."""
    results = []
    eligible = df[df['eligible']].copy()
    
    alpha = 1.0 - beta - gamma
    
    for _, row in eligible.iterrows():
        iusaf_amt = alpha * row.get('iusaf_share', 0) * FUND_SIZE / 1_000_000
        tsac_amt = beta * row.get('tsac_share', 0) * FUND_SIZE / 1_000_000
        sosac_amt = gamma * row.get('sosac_share', 0) * FUND_SIZE / 1_000_000
        
        tsac_iusaf_ratio = tsac_amt / iusaf_amt if iusaf_amt > 0 else float('inf')
        sosac_iusaf_ratio = sosac_amt / iusaf_amt if iusaf_amt > 0 else float('inf')
        
        results.append({
            'party': row['party'],
            'is_sids': row.get('is_sids', False),
            'is_ldc': row.get('is_ldc', False),
            'iusaf_amt_m': iusaf_amt,
            'tsac_amt_m': tsac_amt,
            'sosac_amt_m': sosac_amt,
            'tsac_iusaf_ratio': tsac_iusaf_ratio,
            'sosac_iusaf_ratio': sosac_iusaf_ratio,
            'total_allocation_m': row.get('total_allocation', 0)
        })
    
    return pd.DataFrame(results)


def run_scenario(base_df: pd.DataFrame, beta: float, gamma: float, 
                 scenario_id: str = "scenario") -> pd.DataFrame:
    """Run a single allocation scenario."""
    results = calculate_allocations(
        base_df,
        fund_size=FUND_SIZE,
        iplc_share_pct=IPLC_SHARE_PCT,
        exclude_high_income=EXCLUDE_HIGH_INCOME,
        tsac_beta=beta,
        sosac_gamma=gamma,
        un_scale_mode=UN_SCALE_MODE,
        equality_mode=False
    )
    results['scenario_id'] = scenario_id
    return results


def get_scenario_metrics(results: pd.DataFrame, pure_iusaf_results: pd.DataFrame) -> Dict:
    """Compute key metrics for a scenario."""
    eligible = results[results['eligible']]
    pure_eligible = pure_iusaf_results[pure_iusaf_results['eligible']]
    
    # Gini coefficient (pass as Series)
    gini = compute_gini(eligible['total_allocation']) if len(eligible) > 0 else None
    
    # Spearman vs pure IUSAF
    spearman = compute_spearman_vs_iusaf(results, pure_iusaf_results)
    
    # Band 1 mean
    band1 = eligible[eligible['un_band'].str.startswith('Band 1', na=False)]
    band1_mean = band1['total_allocation'].mean() if len(band1) > 0 else None
    
    # SIDS total
    sids_total = eligible.loc[eligible['is_sids'], 'total_allocation'].sum()
    
    # LDC total
    if 'UN LDC' in eligible.columns:
        ldc_mask = eligible['UN LDC'].eq('LDC')
    else:
        ldc_mask = eligible['is_ldc']
    ldc_total = eligible.loc[ldc_mask, 'total_allocation'].sum() if ldc_mask.any() else 0
    
    return {
        'gini': gini,
        'spearman': spearman,
        'band1_mean_m': band1_mean,
        'sids_total_m': sids_total,
        'ldc_total_m': ldc_total,
        'n_eligible': len(eligible)
    }


# ============================================================================
# Binary Search for Crossover Points
# ============================================================================

def find_tsac_crossover(base_df: pd.DataFrame, target_ratio: float = 1.0,
                        tolerance: float = 0.001, max_iterations: int = 50) -> Tuple[float, pd.DataFrame]:
    """
    Binary search to find TSAC beta where max(TSAC/IUSAF ratio) = target_ratio.
    
    Returns: (beta_value, ratios_dataframe)
    """
    low = 0.0
    high = 0.15  # 15% upper bound
    
    best_beta = None
    best_ratios = None
    
    for iteration in range(max_iterations):
        mid = (low + high) / 2
        
        results = run_scenario(base_df, beta=mid, gamma=SOSAC_GAMMA_DEFAULT, 
                               scenario_id=f"tsac_search_{mid:.4f}")
        ratios_df = compute_component_ratios(results, mid, SOSAC_GAMMA_DEFAULT)
        
        # Find max TSAC/IUSAF ratio (excluding inf)
        finite_ratios = ratios_df['tsac_iusaf_ratio'].replace(float('inf'), np.nan).dropna()
        max_ratio = finite_ratios.max() if len(finite_ratios) > 0 else float('inf')
        
        if abs(max_ratio - target_ratio) < tolerance:
            best_beta = mid
            best_ratios = ratios_df
            break
        
        if max_ratio < target_ratio:
            low = mid
        else:
            high = mid
        
        best_beta = mid
        best_ratios = ratios_df
    
    return best_beta, best_ratios


def find_sosac_crossover(base_df: pd.DataFrame, target_ratio: float = 1.0,
                         tolerance: float = 0.001, max_iterations: int = 50) -> Tuple[float, pd.DataFrame]:
    """
    Binary search to find SOSAC gamma where max(SOSAC/IUSAF ratio for SIDS) = target_ratio.
    
    Returns: (gamma_value, ratios_dataframe)
    """
    low = 0.0
    high = 0.30  # 30% upper bound (based on analytical estimate of ~17.4%)
    
    best_gamma = None
    best_ratios = None
    
    for iteration in range(max_iterations):
        mid = (low + high) / 2
        
        results = run_scenario(base_df, beta=0.0, gamma=mid, 
                               scenario_id=f"sosac_search_{mid:.4f}")
        ratios_df = compute_component_ratios(results, 0.0, mid)
        
        # Find max SOSAC/IUSAF ratio among SIDS only
        sids_ratios = ratios_df[ratios_df['is_sids']]['sosac_iusaf_ratio']
        finite_ratios = sids_ratios.replace(float('inf'), np.nan).dropna()
        max_ratio = finite_ratios.max() if len(finite_ratios) > 0 else float('inf')
        
        if abs(max_ratio - target_ratio) < tolerance:
            best_gamma = mid
            best_ratios = ratios_df
            break
        
        if max_ratio < target_ratio:
            low = mid
        else:
            high = mid
        
        best_gamma = mid
        best_ratios = ratios_df
    
    return best_gamma, best_ratios


# ============================================================================
# Visualization Functions
# ============================================================================

def create_break_point_timeline(tsac_sweep_path: str, sosac_sweep_path: str,
                                 tsac_crossover: float, sosac_crossover: float,
                                 output_path: str):
    """Create visualization showing component ratios vs parameter values."""
    
    # Load sweep data
    tsac_df = pd.read_csv(tsac_sweep_path)
    sosac_df = pd.read_csv(sosac_sweep_path)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('white')
    
    # --- TSAC Panel ---
    ax1 = axes[0]
    ax1.plot(tsac_df['sweep_value'] * 100, tsac_df['china_tsac_iusaf_ratio'], 
             'o-', color='#D85A30', linewidth=2, markersize=4, label='China')
    ax1.plot(tsac_df['sweep_value'] * 100, tsac_df['brazil_tsac_iusaf_ratio'],
             's-', color='#BA7517', linewidth=2, markersize=4, label='Brazil')
    
    # Balance point lines
    ax1.axvline(x=1.5, color='#1D9E75', linestyle='--', linewidth=1.5, alpha=0.8, label='Strict (1.5%)')
    ax1.axvline(x=2.5, color='#378ADD', linestyle='--', linewidth=1.5, alpha=0.8, label='Gini-minimum (2.5%)')
    ax1.axvline(x=3.0, color='#8B5CF6', linestyle='--', linewidth=1.5, alpha=0.8, label='Band-order overturn (3.0%)')
    ax1.axvline(x=3.5, color='#BA7517', linestyle='--', linewidth=1.5, alpha=0.8, label='Bounded (3.5%)')
    ax1.axvline(x=tsac_crossover * 100, color='#EF4444', linestyle='-', linewidth=2, 
                label=f'TSAC Overturn ({tsac_crossover*100:.2f}%)')
    
    # Threshold line
    ax1.axhline(y=1.0, color='#333333', linestyle='-', linewidth=1, alpha=0.5)
    
    ax1.set_xlabel('TSAC Weight (β)', fontsize=11)
    ax1.set_ylabel('TSAC/IUSAF Ratio', fontsize=11)
    ax1.set_title('TSAC Component vs IUSAF Baseline', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 7)
    ax1.grid(True, alpha=0.3)
    
    # --- SOSAC Panel ---
    ax2 = axes[1]
    ax2.plot(sosac_df['sweep_value'] * 100, sosac_df['max_sosac_iusaf_ratio'],
             'o-', color='#378ADD', linewidth=2, markersize=4, label='Max SIDS ratio')
    
    # Crossover line
    ax2.axvline(x=sosac_crossover * 100, color='#EF4444', linestyle='-', linewidth=2,
                label=f'SOSAC Overturn ({sosac_crossover*100:.2f}%)')
    
    # Threshold line
    ax2.axhline(y=1.0, color='#333333', linestyle='-', linewidth=1, alpha=0.5)
    
    ax2.set_xlabel('SOSAC Weight (γ)', fontsize=11)
    ax2.set_ylabel('SOSAC/IUSAF Ratio (SIDS)', fontsize=11)
    ax2.set_title('SOSAC Component vs IUSAF Baseline (SIDS)', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=9)
    ax2.set_xlim(0, 20)
    ax2.set_ylim(0, 1.5)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Saved: {output_path}")


def create_party_heatmap(scenario_results: Dict[str, pd.DataFrame], output_path: str):
    """Create heatmap showing Party allocations across scenarios."""
    
    # Get top 20 parties by total allocation across scenarios
    all_allocations = []
    for scenario_id, df in scenario_results.items():
        eligible = df[df['eligible']].copy()
        eligible['scenario'] = scenario_id
        all_allocations.append(eligible[['party', 'scenario', 'total_allocation']])
    
    combined = pd.concat(all_allocations, ignore_index=True)
    
    # Pivot to matrix
    pivot = combined.pivot_table(index='party', columns='scenario', values='total_allocation', aggfunc='first')
    
    # Select top parties by average allocation
    top_parties = pivot.mean(axis=1).nlargest(20).index
    pivot_top = pivot.loc[top_parties]
    
    # Scenario order
    scenario_order = ['pure_iusaf', 'strict', 'bounded', 'even', 'tsac_overturn', 'sosac_overturn']
    scenario_order = [s for s in scenario_order if s in pivot_top.columns]
    pivot_top = pivot_top[scenario_order]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    fig.patch.set_facecolor('white')
    
    # Custom colormap
    cmap = LinearSegmentedColormap.from_list('custom', ['#f0f9ff', '#0891b2', '#1e3a5f'])
    
    # Plot heatmap
    im = ax.imshow(pivot_top.values, cmap=cmap, aspect='auto')
    
    # Labels
    ax.set_xticks(range(len(scenario_order)))
    ax.set_xticklabels([s.replace('_', ' ').title() for s in scenario_order], rotation=45, ha='right', fontsize=10)
    ax.set_yticks(range(len(top_parties)))
    ax.set_yticklabels(pivot_top.index, fontsize=9)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Total Allocation ($m)', fontsize=10)
    
    ax.set_title('Party Allocations Across Scenarios (Top 20 by Allocation)', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Saved: {output_path}")


def create_decision_boundaries(scenario_metrics: Dict[str, Dict], output_path: str):
    """Create multi-panel visualization showing key metrics across scenarios."""
    
    scenarios = list(scenario_metrics.keys())
    scenario_labels = [s.replace('_', ' ').title() for s in scenarios]
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.patch.set_facecolor('white')
    
    # Metrics to plot
    metrics_config = [
        ('gini', 'Gini Coefficient', 'lower is more equal'),
        ('spearman', 'Spearman vs Pure IUSAF', '1.0 = identical ranking'),
        ('band1_mean_m', 'Band 1 Mean Allocation ($m)', ''),
        ('sids_total_m', 'SIDS Total Allocation ($m)', ''),
        ('ldc_total_m', 'LDC Total Allocation ($m)', ''),
    ]
    
    colors = ['#1D9E75', '#378ADD', '#8B5CF6', '#BA7517', '#D85A30', '#EF4444']
    
    for idx, (metric_key, title, subtitle) in enumerate(metrics_config):
        ax = axes.flatten()[idx]
        
        values = [scenario_metrics[s].get(metric_key) for s in scenarios]
        
        bars = ax.bar(range(len(scenarios)), values, color=colors[:len(scenarios)], 
                      edgecolor='white', linewidth=1)
        
        ax.set_xticks(range(len(scenarios)))
        ax.set_xticklabels(scenario_labels, rotation=45, ha='right', fontsize=9)
        ax.set_title(title, fontsize=11, fontweight='bold')
        
        if subtitle:
            ax.text(0.5, -0.15, subtitle, transform=ax.transAxes, ha='center', 
                    fontsize=8, color='#666666', style='italic')
        
        ax.grid(True, axis='y', alpha=0.3)
    
    # Summary panel
    ax = axes.flatten()[5]
    ax.axis('off')
    
    summary_text = "Decision Boundaries Summary\n\n"
    summary_text += "• Lower Bound: Strict (β=1.5%)\n  IUSAF dominant for all Parties\n\n"
    summary_text += "• Gini-minimum (β=2.5%): Lowest Gini\n  preserving IUSAF band order\n\n"
    summary_text += "• Band-order overturn (β=3.0%):\n  Band 6 overtakes Band 5\n\n"
    summary_text += "• Upper Bound (TSAC): β where TSAC\n  overtakes IUSAF for any Party\n\n"
    summary_text += "• Upper Bound (SOSAC): γ where SOSAC\n  overtakes IUSAF for SIDS"
    
    ax.text(0.1, 0.9, summary_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='#f8fafc', edgecolor='#e2e8f0'))
    
    plt.suptitle('Decision Boundaries: Key Metrics Across Scenarios', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Saved: {output_path}")


# ============================================================================
# Main Analysis
# ============================================================================

def main():
    print("=" * 60)
    print("Break Points Analysis")
    print("=" * 60)
    
    # Initialize database and load data
    import duckdb
    con = duckdb.connect(database=':memory:')
    load_data(con)
    base_df = get_base_data(con)
    
    print(f"\nLoaded {len(base_df)} Parties")
    
    # --- Compute Pure IUSAF baseline ---
    print("\n1. Computing Pure IUSAF baseline...")
    pure_iusaf = run_scenario(base_df, beta=0.0, gamma=0.0, scenario_id="pure_iusaf")
    
    # --- Find TSAC Crossover ---
    print("\n2. Finding TSAC crossover point...")
    tsac_crossover, tsac_ratios = find_tsac_crossover(base_df)
    print(f"   TSAC Overturn Point: β = {tsac_crossover:.4f} ({tsac_crossover*100:.2f}%)")
    
    # Identify which Party is binding
    max_ratio_idx = tsac_ratios['tsac_iusaf_ratio'].idxmax()
    binding_party = tsac_ratios.loc[max_ratio_idx, 'party']
    print(f"   Binding Party: {binding_party}")
    
    # --- Find SOSAC Crossover ---
    print("\n3. Finding SOSAC crossover point...")
    sosac_crossover, sosac_ratios = find_sosac_crossover(base_df)
    print(f"   SOSAC Overturn Point: γ = {sosac_crossover:.4f} ({sosac_crossover*100:.2f}%)")
    
    # Identify which SIDS Party is binding
    sids_ratios = sosac_ratios[sosac_ratios['is_sids']]
    max_sids_idx = sids_ratios['sosac_iusaf_ratio'].idxmax()
    binding_sids = sosac_ratios.loc[max_sids_idx, 'party']
    print(f"   Binding SIDS: {binding_sids}")
    
    # --- Generate All Scenarios ---
    print("\n4. Generating scenario allocations...")
    scenarios = {
        'pure_iusaf': (0.0, 0.0),
        'strict': (0.015, 0.03),
        'bounded': (0.035, 0.03),
        'gini_minimum': (0.025, 0.03),
        'band_order_overturn': (0.03, 0.03),
        'tsac_overturn': (tsac_crossover, 0.03),
        'sosac_overturn': (0.0, sosac_crossover),
    }
    
    scenario_results = {}
    scenario_metrics = {}
    
    for scenario_id, (beta, gamma) in scenarios.items():
        print(f"   Computing {scenario_id} (β={beta:.4f}, γ={gamma:.4f})...")
        results = run_scenario(base_df, beta=beta, gamma=gamma, scenario_id=scenario_id)
        scenario_results[scenario_id] = results
        
        metrics = get_scenario_metrics(results, pure_iusaf)
        scenario_metrics[scenario_id] = metrics
        print(f"      Gini: {metrics['gini']:.4f}, Spearman: {metrics['spearman']:.4f}")
    
    # --- Save Scenario Results ---
    print("\n5. Saving scenario results...")
    results_dir = os.path.join(OUTPUT_DIR, 'scenario_results')
    os.makedirs(results_dir, exist_ok=True)
    
    for scenario_id, results in scenario_results.items():
        output_path = os.path.join(results_dir, f"{scenario_id}.csv")
        eligible = results[results['eligible']]
        cols = ['party', 'total_allocation', 'iusaf_share', 'tsac_share', 'sosac_share',
                'component_iusaf_amt', 'component_tsac_amt', 'component_sosac_amt',
                'is_sids', 'is_ldc', 'un_band']
        eligible[cols].to_csv(output_path, index=False)
        print(f"   Saved: {output_path}")
    
    # --- Create Visualizations ---
    print("\n6. Creating visualizations...")
    figures_dir = os.path.join(OUTPUT_DIR, 'figures')
    os.makedirs(figures_dir, exist_ok=True)
    
    # Paths to existing sweep data
    tsac_sweep_path = os.path.join(OUTPUT_DIR, '..', '..', 'sensitivity-reports', 
                                    'v3-sensitivity-reports', 'tsac_fine_sweep.csv')
    sosac_sweep_path = os.path.join(OUTPUT_DIR, '..', '..', 'sensitivity-reports',
                                    'v3-sensitivity-reports', 'sosac_fine_sweep.csv')
    
    # Timeline visualization
    create_break_point_timeline(
        tsac_sweep_path, sosac_sweep_path,
        tsac_crossover, sosac_crossover,
        os.path.join(figures_dir, 'break_point_timeline.svg')
    )
    
    # Heatmap
    create_party_heatmap(
        scenario_results,
        os.path.join(figures_dir, 'party_distribution_heatmap.svg')
    )
    
    # Decision boundaries
    create_decision_boundaries(
        scenario_metrics,
        os.path.join(figures_dir, 'decision_boundaries.svg')
    )
    
    # --- Print Summary ---
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"\nTSAC Overturn Point: β = {tsac_crossover*100:.2f}%")
    print(f"  - At this point, TSAC component equals IUSAF component for {binding_party}")
    print(f"  - Beyond this, TSAC becomes the primary allocation driver")
    
    print(f"\nSOSAC Overturn Point: γ = {sosac_crossover*100:.2f}%")
    print(f"  - At this point, SOSAC component equals IUSAF component for {binding_sids}")
    print(f"  - Beyond this, SOSAC dominates allocations for SIDS")
    
    print("\nScenario Comparison:")
    print("-" * 80)
    print(f"{'Scenario':<20} {'Gini':<10} {'Spearman':<12} {'Band1($m)':<12} {'SIDS($m)':<12} {'LDC($m)':<12}")
    print("-" * 80)
    for scenario_id in scenarios.keys():
        m = scenario_metrics[scenario_id]
        print(f"{scenario_id:<20} {m['gini']:.4f}    {m['spearman']:.4f}      "
              f"{m['band1_mean_m']:.2f}        {m['sids_total_m']:.1f}       {m['ldc_total_m']:.1f}")
    
    print("\n" + "=" * 60)
    print("Analysis complete. Results saved to:")
    print(f"  - {results_dir}/")
    print(f"  - {figures_dir}/")
    print("=" * 60)
    
    # Return results for potential further use
    return {
        'tsac_crossover': tsac_crossover,
        'sosac_crossover': sosac_crossover,
        'scenario_metrics': scenario_metrics,
        'scenario_results': scenario_results
    }


if __name__ == "__main__":
    results = main()
