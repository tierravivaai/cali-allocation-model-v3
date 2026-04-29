#!/usr/bin/env python3
"""
Updated visualizations for Break Points Analysis.

Generates:
1. transfer_scale_summary.svg - KEY: Amount in play at different fund sizes
2. band_transfers_diverging.svg - Band-level gains/losses
3. scenario_comparison.svg - Key metrics across scenarios
4. negotiation_space.svg - Model-level thresholds

Removes outdated figures that referenced per-party crossover points.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# Configuration
scenarios = ['pure_iusaf', 'strict', 'bounded', 'even']
scenario_labels = ['Pure IUSAF', 'Strict', 'Bounded', 'Even']
results_dir = os.path.join(os.path.dirname(__file__), 'scenario_results')
figures_dir = os.path.join(os.path.dirname(__file__), 'figures')

# Band colors
band_colors = {
    'Band 1: <= 0.001%': '#1D9E75',
    'Band 2: 0.001% - 0.01%': '#2DD4A7',
    'Band 3: 0.01% - 0.1%': '#378ADD',
    'Band 4: 0.1% - 1.0%': '#6BA3E8',
    'Band 5: 1.0% - 10.0%': '#BA7517',
    'Band 6: > 10.0%': '#D85A30',
}

def load_data():
    """Load all scenario data."""
    data = {}
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        data[scenario] = df
    return data

def create_transfer_scale_summary():
    """Create the KEY visualization showing transfer scale at different fund sizes."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('white')
    
    # Left panel: Amount in play at different fund sizes
    ax1 = axes[0]
    
    fund_sizes = [50, 200, 500, 1000, 2000]  # in millions
    fund_labels = ['$50m', '$200m', '$500m', '$1bn', '$2bn']
    
    # Calculate amounts in play (6% at Even scenario)
    amounts_in_play = [f * 0.06 for f in fund_sizes]
    amounts_stable = [f * 0.94 for f in fund_sizes]
    
    x = np.arange(len(fund_sizes))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, amounts_in_play, width, label='In Play (6%)', 
                    color='#EF4444', edgecolor='white')
    bars2 = ax1.bar(x + width/2, amounts_stable, width, label='Stable (94%)', 
                    color='#22C55E', edgecolor='white')
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(fund_labels)
    ax1.set_ylabel('Amount ($m)', fontsize=11)
    ax1.set_title('Stewardship Pool vs Stable Allocations\nat Different Fund Sizes', 
                  fontsize=12, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'${height:.1f}m',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    
    # Right panel: Transfer distribution at $1bn Even scenario
    ax2 = axes[1]
    
    # Load Even scenario data
    df_even = pd.read_csv(os.path.join(results_dir, 'even.csv'))
    df_pure = pd.read_csv(os.path.join(results_dir, 'pure_iusaf.csv'))
    
    merged = df_even.merge(df_pure[['party', 'total_allocation']], 
                           on='party', suffixes=('', '_baseline'))
    merged['abs_delta'] = (merged['total_allocation'] - merged['total_allocation_baseline']).abs()
    
    # Categorize transfers
    categories = ['< $0.5m\n(73%)', '$0.5-1m\n(23%)', '> $1m\n(4%)']
    counts = [
        (merged['abs_delta'] < 0.5).sum(),
        ((merged['abs_delta'] >= 0.5) & (merged['abs_delta'] < 1.0)).sum(),
        (merged['abs_delta'] >= 1.0).sum()
    ]
    
    colors = ['#10B981', '#F59E0B', '#EF4444']
    bars = ax2.bar(categories, counts, color=colors, edgecolor='white', linewidth=2)
    
    for bar, count in zip(bars, counts):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{count}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_ylabel('Number of Parties', fontsize=11)
    ax2.set_title('Distribution of Transfer Sizes\n($1bn fund, Even scenario)', 
                  fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 130)
    
    # Add annotation
    ax2.text(0.5, -0.15, 'Most transfers are < $0.5m = 0.05% of fund',
             transform=ax2.transAxes, ha='center', fontsize=10, 
             color='#666666', style='italic')
    
    plt.suptitle('KEY INSIGHT: Only 6% of Fund is "In Play" — 94% Stable', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = os.path.join(figures_dir, 'transfer_scale_summary.svg')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Created: {output_path}")

def create_band_transfers():
    """Create band-level transfer visualization."""
    data = load_data()
    
    # Aggregate by band
    band_data = {}
    for scenario in scenarios:
        df = data[scenario]
        band_totals = df.groupby('un_band')['total_allocation'].sum()
        band_data[scenario] = band_totals
    
    band_df = pd.DataFrame(band_data)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    
    bands = sorted(band_df.index)
    y_positions = np.arange(len(bands))
    bar_height = 0.25
    
    # Distinct colors for each scenario
    scenario_colors = {
        'strict': '#22C55E',   # Green
        'bounded': '#3B82F6',  # Blue  
        'even': '#8B5CF6',     # Purple
    }
    
    for i, scenario in enumerate(['strict', 'bounded', 'even']):
        baseline = band_df['pure_iusaf']
        deltas = band_df[scenario] - baseline
        
        # Offset each scenario's bars
        offset = (i - 1) * bar_height
        
        for j, band in enumerate(bands):
            delta = deltas[band]
            color = scenario_colors[scenario]
            
            # Lighter color for losses
            alpha = 1.0 if delta >= 0 else 0.6
            
            ax.barh(y_positions[j] + offset, delta, 
                   height=bar_height, color=color, edgecolor='white', alpha=alpha)
    
    ax.set_yticks(y_positions)
    ax.set_yticklabels([b.split(':')[0] for b in bands], fontsize=10)
    ax.set_xlabel('Change from Pure IUSAF ($m)', fontsize=11)
    ax.set_title('Allocation Transfers by Band\n(Solid = gain, Lighter = loss)', 
                 fontsize=13, fontweight='bold')
    
    ax.axvline(x=0, color='#333333', linewidth=1)
    ax.grid(True, axis='x', alpha=0.3)
    
    # Legend below the x-axis
    legend_patches = [
        mpatches.Patch(color='#22C55E', label='Strict (1.5%+3%)'),
        mpatches.Patch(color='#3B82F6', label='Bounded (3.5%+3%)'),
        mpatches.Patch(color='#8B5CF6', label='Even (5%+3%)'),
    ]
    ax.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, -0.15),
              ncol=3, fontsize=10, frameon=False)
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.22)  # Extra space for legend
    
    plt.tight_layout()
    
    output_path = os.path.join(figures_dir, 'band_transfers.svg')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Created: {output_path}")

def create_scenario_comparison():
    """Create scenario comparison visualization."""
    data = load_data()
    
    metrics = {
        'Gini': [],
        'Spearman': [],
        'SIDS_total': [],
        'LDC_total': [],
    }
    
    baseline = data['pure_iusaf']
    
    for scenario in scenarios:
        df = data[scenario]
        
        # Gini (using all rows in the CSV)
        allocations = df['total_allocation'].values
        sorted_allocs = np.sort(allocations)
        n = len(sorted_allocs)
        gini_val = 2 * np.sum((np.arange(1, n+1) * sorted_allocs)) / (n * sorted_allocs.sum()) - (n+1) / n
        metrics['Gini'].append(gini_val)
        
        # Spearman (vs pure IUSAF)
        merged = df.merge(baseline[['party', 'total_allocation']], on='party', suffixes=('', '_base'))
        spearman = merged['total_allocation'].corr(merged['total_allocation_base'], method='spearman')
        metrics['Spearman'].append(spearman)
        
        # SIDS/LDC totals
        metrics['SIDS_total'].append(df[df['is_sids']]['total_allocation'].sum())
        metrics['LDC_total'].append(df[df['is_ldc']]['total_allocation'].sum())
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.patch.set_facecolor('white')
    
    colors = ['#1D9E75', '#378ADD', '#8B5CF6', '#D85A30']
    
    # Gini
    ax = axes[0, 0]
    ax.bar(scenario_labels, metrics['Gini'], color=colors, edgecolor='white')
    ax.set_ylabel('Gini Coefficient')
    ax.set_title('Distributional Equality\n(lower = more equal)', fontsize=11, fontweight='bold')
    ax.set_ylim(0.08, 0.10)
    ax.grid(True, axis='y', alpha=0.3)
    
    # Spearman
    ax = axes[0, 1]
    ax.bar(scenario_labels, metrics['Spearman'], color=colors, edgecolor='white')
    ax.set_ylabel('Spearman Correlation')
    ax.set_title('Rank Correlation with Pure IUSAF\n(1.0 = identical ranking)', fontsize=11, fontweight='bold')
    ax.set_ylim(0.8, 1.05)
    # Band-order overturn reference line at TSAC = 3.0%
    ax.axvline(x=0.03, color='#EF4444', linestyle='--', alpha=0.5, label='Band-order overturn (TSAC=3.0%)')
    ax.legend(fontsize=9)
    ax.grid(True, axis='y', alpha=0.3)
    
    # SIDS
    ax = axes[1, 0]
    ax.bar(scenario_labels, metrics['SIDS_total'], color=colors, edgecolor='white')
    ax.set_ylabel('Total Allocation ($m)')
    ax.set_title('SIDS Total Allocation', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    
    # LDC
    ax = axes[1, 1]
    ax.bar(scenario_labels, metrics['LDC_total'], color=colors, edgecolor='white')
    ax.set_ylabel('Total Allocation ($m)')
    ax.set_title('LDC Total Allocation', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.suptitle('Scenario Comparison: Key Metrics', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = os.path.join(figures_dir, 'scenario_comparison.svg')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Created: {output_path}")

def create_order_overturn():
    """Create visualization showing when band ordering breaks down."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    from cali_model.data_loader import load_data, get_base_data
    from cali_model.calculator import calculate_allocations
    import duckdb
    
    # Initialize
    con = duckdb.connect(database=':memory:')
    load_data(con)
    base_df = get_base_data(con)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor('white')
    
    # Sweep TSAC values
    tsac_values = [i * 0.005 for i in range(31)]  # 0 to 15%
    
    band_order = [
        ('Band 1: <= 0.001%', '#1D9E75', 'Band 1'),
        ('Band 2: 0.001% - 0.01%', '#2DD4A7', 'Band 2'),
        ('Band 3: 0.01% - 0.1%', '#378ADD', 'Band 3'),
        ('Band 4: 0.1% - 1.0%', '#6BA3E8', 'Band 4'),
        ('Band 5: 1.0% - 10.0%', '#BA7517', 'Band 5'),
        ('Band 6: > 10.0%', '#D85A30', 'Band 6'),
    ]
    
    # Store band means for each TSAC value
    all_band_means = {band[0]: [] for band in band_order}
    
    for tsac in tsac_values:
        results_df = calculate_allocations(
            base_df, fund_size=1_000_000_000, iplc_share_pct=50,
            exclude_high_income=True, tsac_beta=tsac, sosac_gamma=0.03,
            un_scale_mode='band_inversion', equality_mode=False
        )
        
        eligible = results_df[results_df['eligible']].copy()
        band_means = eligible.groupby('un_band')['total_allocation'].mean()
        
        for band_key, _, _ in band_order:
            all_band_means[band_key].append(band_means.get(band_key, 0))
    
    # Plot each band's mean allocation over TSAC range
    tsac_pcts = [t * 100 for t in tsac_values]
    
    for band_key, color, label in band_order:
        ax.plot(tsac_pcts, all_band_means[band_key], '-', color=color, 
                linewidth=2.5, label=label)
    
    # Mark order overturn threshold
    overturn_tsac = 2.95
    ax.axvline(x=overturn_tsac, color='#EF4444', linewidth=2, linestyle='--')
    ax.text(overturn_tsac + 0.3, 10, 'Order Overturn\nThreshold\n(2.95%)', 
            fontsize=10, fontweight='bold', color='#EF4444')
    
    # Mark current scenarios
    scenarios = [
        (1.5, 'Strict', '#22C55E'),
        (3.5, 'Bounded', '#3B82F6'),
        (5.0, 'Even', '#8B5CF6'),
    ]
    
    for tsac, name, color in scenarios:
        ax.axvline(x=tsac, color=color, linewidth=1.5, linestyle=':', alpha=0.7)
        ax.text(tsac, 19.5, name, ha='center', fontsize=9, fontweight='bold', color=color)
    
    # Highlight the crossover region
    ax.fill_between([2.8, 3.2], 0, 20, color='#EF4444', alpha=0.1)
    
    ax.set_xlabel('TSAC Weight (%)', fontsize=12)
    ax.set_ylabel('Mean Per-Party Allocation ($m)', fontsize=12)
    ax.set_title('Order Overturn: When Band Structure Breaks Down\n(Band 6 overtakes Band 5 at TSAC ≈ 2.95%)', 
                 fontsize=13, fontweight='bold')
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 21)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    # Add annotation
    ax.text(7.5, 3, 'Below threshold: Band ordering preserved (IUSAF equity)\nAbove threshold: Band ordering inverted (China > Brazil)', 
            fontsize=9, color='#555555', style='italic',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    output_path = os.path.join(figures_dir, 'order_overturn.svg')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Created: {output_path}")
    """Create visualization showing model-level thresholds."""
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor('white')
    
    # Draw the threshold scale - just colored bands
    ax.set_xlim(0, 55)
    ax.set_ylim(0, 6)
    
    # Zones with labels at top
    zones = [
        (0, 20, '#22C55E', 'Conservative', '(IUSAF > 80%)'),
        (20, 40, '#F59E0B', 'Moderate', '(IUSAF 60-80%)'),
        (40, 50, '#EF4444', 'Aggressive', '(IUSAF < 60%)'),
    ]
    
    for start, end, color, label1, label2 in zones:
        ax.fill_between([start, end], 0, 6, color=color, alpha=0.4)
        ax.text((start + end) / 2, 5.5, label1, ha='center', va='top', 
                fontsize=12, fontweight='bold')
        ax.text((start + end) / 2, 4.8, label2, ha='center', va='top', 
                fontsize=9, color='#555555')
    
    # Overturn zone (purple, smaller)
    ax.fill_between([50, 55], 0, 6, color='#7C3AED', alpha=0.4)
    ax.text(52.5, 5.5, 'Overturn', ha='center', va='top', fontsize=12, fontweight='bold')
    ax.text(52.5, 4.8, '(IUSAF < 50%)', ha='center', va='top', fontsize=9, color='#555555')
    
    # Threshold line
    ax.axvline(x=50, color='#333333', linewidth=3, linestyle='--')
    
    # Current positions as clear markers on the x-axis
    # Strict: 1.5% + 3% = 4.5%
    # Bounded: 3.5% + 3% = 6.5%
    # Even: 5% + 3% = 8%
    
    scenarios_data = [
        (4.5, 'Strict', '#22C55E', 'TSAC=1.5% + SOSAC=3%'),
        (6.5, 'Bounded', '#3B82F6', 'TSAC=3.5% + SOSAC=3%'),
        (8.0, 'Even', '#8B5CF6', 'TSAC=5% + SOSAC=3%'),
    ]
    
    for x_pos, name, color, detail in scenarios_data:
        # Vertical line from x-axis to marker
        ax.plot([x_pos, x_pos], [0, 2], color=color, linewidth=2)
        # Dot marker
        ax.plot(x_pos, 2, 'o', markersize=20, color=color, markeredgecolor='white', markeredgewidth=2)
        # Label above dot
        ax.text(x_pos, 2.8, name, ha='center', va='bottom', fontsize=11, fontweight='bold', color=color)
        ax.text(x_pos, 3.4, detail, ha='center', va='bottom', fontsize=8, color='#555555')
    
    # X-axis label
    ax.set_xlabel('TSAC + SOSAC Combined Weight (%)', fontsize=12)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.set_yticks([])
    
    # Title
    ax.set_title('Negotiation Space: All Current Scenarios in Conservative Zone\n(Far below 50% model overturn threshold)', 
                 fontsize=13, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    output_path = os.path.join(figures_dir, 'negotiation_space.svg')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Created: {output_path}")

def remove_outdated_figures():
    """Remove figures that reference outdated per-party crossover logic."""
    outdated = [
        'break_point_timeline.svg',  # Referenced 1.8% per-party crossover
        'decision_boundaries.svg',   # May have outdated metrics
        'party_distribution_heatmap.svg',  # Replaced by scenario comparison
        'band_composition_stacked.svg',  # Replaced by simpler visualizations
        'band_transfers_flow.svg',  # Simplified
        'transfer_scale_perspective.svg',  # Replaced by summary
        'band_transfers_diverging.svg',  # Replaced by updated version
    ]
    
    for filename in outdated:
        filepath = os.path.join(figures_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Removed outdated: {filepath}")

def main():
    print("=" * 60)
    print("Updating all visualizations")
    print("=" * 60)
    
    # Remove outdated figures
    print("\nRemoving outdated figures...")
    remove_outdated_figures()
    
    # Create updated figures
    print("\nCreating updated figures...")
    create_transfer_scale_summary()
    create_band_transfers()
    create_scenario_comparison()
    create_order_overturn()
    create_negotiation_space()
    
    print("\n" + "=" * 60)
    print("Done! New figures:")
    for f in sorted(os.listdir(figures_dir)):
        print(f"  - {f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
