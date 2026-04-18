#!/usr/bin/env python3
"""
Create perspective visualization showing scale of transfers.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

results_dir = os.path.join(os.path.dirname(__file__), 'scenario_results')
figures_dir = os.path.join(os.path.dirname(__file__), 'figures')

scenarios = ['pure_iusaf', 'strict', 'bounded', 'even']
scenario_labels = ['Pure IUSAF', 'Strict', 'Bounded', 'Even']

def main():
    # Load data
    data = {}
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        data[scenario] = df
    
    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('white')
    
    # --- Left panel: Amount in play ---
    ax1 = axes[0]
    
    amounts_in_play = []
    for scenario in ['strict', 'bounded', 'even']:
        df = data[scenario]
        baseline = data['pure_iusaf']
        merged = df.merge(baseline[['party', 'total_allocation']], 
                          on='party', suffixes=('', '_baseline'))
        merged['abs_delta'] = (merged['total_allocation'] - merged['total_allocation_baseline']).abs()
        amounts_in_play.append(merged['abs_delta'].sum())
    
    x = np.arange(3)
    bars = ax1.bar(x, amounts_in_play, color=['#22C55E', '#3B82F6', '#8B5CF6'], 
                   edgecolor='white', linewidth=2)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, amounts_in_play)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'${val:.1f}m\n({val/10:.1f}%)', ha='center', va='bottom', fontsize=10)
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Strict', 'Bounded', 'Even'])
    ax1.set_ylabel('Amount In Play ($m)', fontsize=11)
    ax1.set_title('Total Amount Being Transferred\n(vs Pure IUSAF baseline)', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 75)
    ax1.axhline(y=50, color='#888888', linestyle='--', alpha=0.5, label='5% of fund')
    ax1.legend(loc='upper left', fontsize=9)
    
    # --- Right panel: Transfer distribution ---
    ax2 = axes[1]
    
    # Even scenario distribution
    df = data['even']
    baseline = data['pure_iusaf']
    merged = df.merge(baseline[['party', 'total_allocation']], on='party', suffixes=('', '_baseline'))
    merged['abs_delta'] = (merged['total_allocation'] - merged['total_allocation_baseline']).abs()
    merged['delta_pct'] = (merged['abs_delta'] / merged['total_allocation_baseline']) * 100
    
    # Categories
    categories = ['< $0.5m\n(0.05%)', '$0.5-1m', '$1-5m', '> $5m']
    counts = [
        (merged['abs_delta'] < 0.5).sum(),
        ((merged['abs_delta'] >= 0.5) & (merged['abs_delta'] < 1.0)).sum(),
        ((merged['abs_delta'] >= 1.0) & (merged['abs_delta'] < 5.0)).sum(),
        (merged['abs_delta'] >= 5.0).sum()
    ]
    
    colors = ['#10B981', '#F59E0B', '#EF4444', '#7C3AED']
    bars = ax2.bar(categories, counts, color=colors, edgecolor='white', linewidth=2)
    
    for bar, count in zip(bars, counts):
        pct = count / len(merged) * 100
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{count}\n({pct:.0f}%)', ha='center', va='bottom', fontsize=10)
    
    ax2.set_ylabel('Number of Parties', fontsize=11)
    ax2.set_title('Distribution of Transfer Sizes\n(Even Scenario)', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 140)
    
    # Add annotation
    ax2.text(0.5, -0.18, 'Most transfers are very small (< $0.5m)\n= less than 0.05% of the total fund',
             transform=ax2.transAxes, ha='center', fontsize=10, 
             color='#666666', style='italic')
    
    plt.suptitle('Perspective: Scale of Stewardship Transfers', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = os.path.join(figures_dir, 'transfer_scale_perspective.svg')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
