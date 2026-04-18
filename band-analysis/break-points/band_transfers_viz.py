#!/usr/bin/env python3
"""
Create visualizations for band allocation transfers.
1. Diverging bar chart
2. Sankey-style flow diagram
3. Stacked bar chart
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

def load_band_data():
    """Load and aggregate data by band."""
    data = {}
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        band_totals = df.groupby('un_band')['total_allocation'].sum()
        data[scenario] = band_totals
    return pd.DataFrame(data).fillna(0)

def create_diverging_bar_chart(band_df):
    """Create diverging bar chart showing gains/losses by band."""
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')
    
    bands = sorted(band_df.index)
    y_positions = np.arange(len(bands))
    bar_height = 0.2
    
    colors = ['#22C55E', '#3B82F6', '#8B5CF6']  # green, blue, purple for scenarios
    
    for i, scenario in enumerate(['strict', 'bounded', 'even']):
        baseline = band_df['pure_iusaf']
        deltas = band_df[scenario] - baseline
        
        # Create bars
        for j, band in enumerate(bands):
            delta = deltas[band]
            color = colors[i] if delta >= 0 else '#EF4444'
            alpha = 0.9 if delta >= 0 else 0.7
            
            ax.barh(y_positions[j] + (i - 1) * bar_height, delta, 
                   height=bar_height, color=color, alpha=alpha, edgecolor='white')
    
    # Formatting
    ax.set_yticks(y_positions)
    ax.set_yticklabels([b.split(':')[0] for b in bands])
    ax.set_xlabel('Change from Pure IUSAF ($m)', fontsize=11)
    ax.set_title('Allocation Transfers by Band\n(Green = gain, Red = loss)', fontsize=13, fontweight='bold')
    
    # Add legend
    legend_patches = [
        mpatches.Patch(color='#22C55E', label='Strict'),
        mpatches.Patch(color='#3B82F6', label='Bounded'),
        mpatches.Patch(color='#8B5CF6', label='Even'),
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=10)
    
    # Add zero line
    ax.axvline(x=0, color='#333333', linewidth=1)
    ax.grid(True, axis='x', alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(figures_dir, 'band_transfers_diverging.svg')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {output_path}")

def create_stacked_bar_chart(band_df):
    """Create stacked bar chart showing band composition per scenario."""
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')
    
    bands = sorted(band_df.index)
    x_positions = np.arange(len(scenarios))
    bar_width = 0.6
    
    bottom = np.zeros(len(scenarios))
    
    for band in bands:
        values = band_df.loc[band, scenarios].values
        color = band_colors.get(band, '#888888')
        ax.bar(x_positions, values, bar_width, bottom=bottom, 
               label=band.split(':')[0], color=color, edgecolor='white')
        bottom += values
    
    # Formatting
    ax.set_xticks(x_positions)
    ax.set_xticklabels(scenario_labels, fontsize=11)
    ax.set_ylabel('Total Allocation ($m)', fontsize=11)
    ax.set_title('Band Composition by Scenario\n(Total = $1,000m)', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9, title='Band')
    
    # Add horizontal line at $1000m
    ax.axhline(y=1000, color='#333333', linewidth=1, linestyle='--', alpha=0.5)
    
    ax.set_ylim(0, 1050)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(figures_dir, 'band_composition_stacked.svg')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {output_path}")

def create_flow_diagram(band_df):
    """Create Sankey-style flow diagram showing transfers."""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    
    bands = sorted(band_df.index)
    
    # Left side: Pure IUSAF
    # Right side: Even scenario
    left_x = 0
    right_x = 1
    
    # Calculate band heights (proportional to allocation)
    pure_totals = band_df['pure_iusaf']
    even_totals = band_df['even']
    
    # Calculate transfers
    transfers = {}
    for band in bands:
        transfers[band] = even_totals[band] - pure_totals[band]
    
    # Draw left bars (Pure IUSAF)
    left_bottom = 0
    left_positions = {}
    for band in bands:
        height = pure_totals[band]
        left_positions[band] = (left_bottom, height)
        ax.barh(left_bottom, height, left=left_x, height=height, 
                color=band_colors.get(band, '#888888'), 
                orientation='horizontal', align='edge', edgecolor='white')
        # Add label
        ax.text(-0.02, left_bottom + height/2, band.split(':')[0], 
                ha='right', va='center', fontsize=9)
        left_bottom += height
    
    # Draw right bars (Even)
    right_bottom = 0
    for band in bands:
        height = even_totals[band]
        ax.barh(right_bottom, height, left=right_x, height=height,
                color=band_colors.get(band, '#888888'),
                orientation='horizontal', align='edge', edgecolor='white')
        right_bottom += height
    
    # Draw flow lines (simplified - show net transfers as arrows)
    # Gainers get arrows pointing right
    # Losers have arrows pointing left
    
    y_center = 500  # Center of chart
    
    # Annotate transfers
    ax.annotate('', xy=(0.7, 850), xytext=(0.3, 350),
                arrowprops=dict(arrowstyle='->', color='#EF4444', lw=2))
    ax.text(0.5, 600, 'Transfer: Band 2-3 → Band 4-6', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#FEF3C7', edgecolor='#F59E0B'))
    
    # Labels
    ax.text(0, -30, 'Pure IUSAF\n($1,000m)', ha='center', fontsize=12, fontweight='bold')
    ax.text(1, -30, 'Even\n($1,000m)', ha='center', fontsize=12, fontweight='bold')
    
    ax.set_title('Allocation Flow: Pure IUSAF → Even Scenario\n(Net transfer from Band 2-3 to Band 4-6)', 
                 fontsize=13, fontweight='bold', pad=20)
    
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(-60, 1100)
    ax.axis('off')
    
    plt.tight_layout()
    output_path = os.path.join(figures_dir, 'band_transfers_flow.svg')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {output_path}")

def main():
    print("Creating band transfer visualizations...")
    
    band_df = load_band_data()
    
    create_diverging_bar_chart(band_df)
    create_stacked_bar_chart(band_df)
    create_flow_diagram(band_df)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
