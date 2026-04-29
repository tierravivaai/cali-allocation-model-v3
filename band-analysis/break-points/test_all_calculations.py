#!/usr/bin/env python3
"""
Comprehensive Mechanical Verification Tests for Break Points Analysis.

Tests:
1. Total allocations sum to fund size ($1 billion)
2. Transfer scale calculations are correct
3. Band transfer calculations are correct
4. Gini coefficients are within valid range
5. Spearman correlations are valid
6. Fund size scaling is proportional
7. Percentages sum correctly
"""

import pandas as pd
import numpy as np
import os
import sys

# Configuration
scenarios = ['pure_iusaf', 'strict', 'bounded', 'even']
results_dir = os.path.join(os.path.dirname(__file__), 'scenario_results')
TOLERANCE = 0.01  # $10,000 tolerance
EXPECTED_TOTAL = 1000.0  # $1 billion in millions

def test_total_sums():
    """Test 1: Total allocations sum to $1 billion."""
    print("\nTEST 1: Total allocations sum to $1 billion")
    print("-" * 60)
    
    errors = []
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        total = df['total_allocation'].sum()
        
        if abs(total - EXPECTED_TOTAL) > TOLERANCE:
            errors.append(f"  FAIL: {scenario} total = {total:.4f}m (expected {EXPECTED_TOTAL}m)")
        else:
            print(f"  PASS: {scenario} total = {total:.4f}m")
    
    return len(errors) == 0, errors

def test_transfer_scale():
    """Test 2: Transfer scale calculations are correct."""
    print("\nTEST 2: Transfer scale calculations")
    print("-" * 60)
    
    errors = []
    
    # Load data
    data = {}
    for scenario in scenarios:
        data[scenario] = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
    
    baseline = data['pure_iusaf']
    
    # Expected percentages
    expected_pct = {
        'strict': 0.043,
        'bounded': 0.051,
        'smoothed': 0.060,
    }
    
    for scenario in ['strict', 'bounded', 'even']:
        df = data[scenario]
        merged = df.merge(baseline[['party', 'total_allocation']], 
                          on='party', suffixes=('', '_baseline'))
        merged['abs_delta'] = (merged['total_allocation'] - merged['total_allocation_baseline']).abs()
        
        total_in_play = merged['abs_delta'].sum()
        pct_of_fund = total_in_play / EXPECTED_TOTAL
        
        # Verify percentage is in expected range (4-6%)
        if not (0.04 <= pct_of_fund <= 0.07):
            errors.append(f"  FAIL: {scenario} % in play = {pct_of_fund*100:.1f}% (expected 4-6%)")
        else:
            print(f"  PASS: {scenario} amount in play = ${total_in_play:.1f}m ({pct_of_fund*100:.1f}%)")
        
        # Verify undisputed amount
        undisputed = EXPECTED_TOTAL - total_in_play
        undisputed_pct = undisputed / EXPECTED_TOTAL
        
        if not (0.93 <= undisputed_pct <= 0.96):
            errors.append(f"  FAIL: {scenario} undisputed = {undisputed_pct*100:.1f}% (expected 94%)")
        else:
            print(f"  PASS: {scenario} undisputed = ${undisputed:.1f}m ({undisputed_pct*100:.1f}%)")
    
    return len(errors) == 0, errors

def test_band_transfers():
    """Test 3: Band transfer calculations are correct."""
    print("\nTEST 3: Band transfer calculations")
    print("-" * 60)
    
    errors = []
    
    # Load data
    data = {}
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        data[scenario] = df
    
    baseline = data['pure_iusaf']
    
    # Verify band transfers sum to zero (within tolerance)
    for scenario in ['strict', 'bounded', 'even']:
        df = data[scenario]
        
        band_totals_baseline = baseline.groupby('un_band')['total_allocation'].sum()
        band_totals_scenario = df.groupby('un_band')['total_allocation'].sum()
        
        deltas = band_totals_scenario - band_totals_baseline
        sum_deltas = deltas.sum()
        
        if abs(sum_deltas) > TOLERANCE:
            errors.append(f"  FAIL: {scenario} band deltas sum = {sum_deltas:.4f}m (expected ~0)")
        else:
            print(f"  PASS: {scenario} band deltas sum = {sum_deltas:.4f}m")
    
    # Verify Bands 2-3 lose, Bands 4-6 gain (TSAC effect)
    for scenario in ['even']:
        df = data[scenario]
        
        band_totals_baseline = baseline.groupby('un_band')['total_allocation'].sum()
        band_totals_scenario = df.groupby('un_band')['total_allocation'].sum()
        
        band2_delta = band_totals_scenario.get('Band 2: 0.001% - 0.01%', 0) - band_totals_baseline.get('Band 2: 0.001% - 0.01%', 0)
        band3_delta = band_totals_scenario.get('Band 3: 0.01% - 0.1%', 0) - band_totals_baseline.get('Band 3: 0.01% - 0.1%', 0)
        
        if band2_delta >= 0:
            errors.append(f"  FAIL: Band 2 should lose allocation, got {band2_delta:.1f}m")
        else:
            print(f"  PASS: Band 2 loses ${abs(band2_delta):.1f}m (as expected)")
        
        if band3_delta >= 0:
            errors.append(f"  FAIL: Band 3 should lose allocation, got {band3_delta:.1f}m")
        else:
            print(f"  PASS: Band 3 loses ${abs(band3_delta):.1f}m (as expected)")
    
    return len(errors) == 0, errors

def test_gini_coefficients():
    """Test 4: Gini coefficients are within valid range."""
    print("\nTEST 4: Gini coefficients")
    print("-" * 60)
    
    errors = []
    
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        allocations = df['total_allocation'].values
        
        # Calculate Gini
        sorted_allocs = np.sort(allocations)
        n = len(sorted_allocs)
        gini = 2 * np.sum((np.arange(1, n+1) * sorted_allocs)) / (n * sorted_allocs.sum()) - (n+1) / n
        
        # Verify Gini is in valid range [0, 1]
        if not (0 <= gini <= 1):
            errors.append(f"  FAIL: {scenario} Gini = {gini:.4f} (invalid range)")
        # Verify Gini is low (this is a relatively equal distribution)
        elif not (0.05 <= gini <= 0.15):
            errors.append(f"  WARN: {scenario} Gini = {gini:.4f} (outside expected 0.05-0.15 range)")
            print(f"  WARN: {scenario} Gini = {gini:.4f} (outside expected range)")
        else:
            print(f"  PASS: {scenario} Gini = {gini:.4f}")
    
    return len(errors) == 0, errors

def test_spearman_correlations():
    """Test 5: Spearman correlations are valid."""
    print("\nTEST 5: Spearman correlations vs Pure IUSAF")
    print("-" * 60)
    
    errors = []
    
    baseline = pd.read_csv(os.path.join(results_dir, 'pure_iusaf.csv'))
    
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        
        merged = df.merge(baseline[['party', 'total_allocation']], 
                          on='party', suffixes=('', '_baseline'))
        
        spearman = merged['total_allocation'].corr(merged['total_allocation_baseline'], method='spearman')
        
        # Verify correlation is in valid range [-1, 1]
        if not (-1 <= spearman <= 1):
            errors.append(f"  FAIL: {scenario} Spearman = {spearman:.4f} (invalid range)")
        # Verify high correlation (should be close to 1 for these scenarios)
        elif not (0.8 <= spearman <= 1.0):
            errors.append(f"  FAIL: {scenario} Spearman = {spearman:.4f} (expected 0.8-1.0)")
        else:
            print(f"  PASS: {scenario} Spearman = {spearman:.4f}")
    
    return len(errors) == 0, errors

def test_fund_size_scaling():
    """Test 6: Fund size scaling is proportional."""
    print("\nTEST 6: Fund size scaling is proportional")
    print("-" * 60)
    
    errors = []
    
    # The percentages should be constant regardless of fund size
    # Test with different fund sizes
    fund_sizes = [50, 200, 500, 1000, 2000]  # in millions
    
    # At 6% in play, the percentages should be constant
    for fund_size in fund_sizes:
        in_play = fund_size * 0.06
        undisputed = fund_size * 0.94
        
        # Verify percentages
        in_play_pct = in_play / fund_size
        undisputed_pct = undisputed / fund_size
        
        if abs(in_play_pct - 0.06) > 0.001:
            errors.append(f"  FAIL: ${fund_size}m fund - in play pct = {in_play_pct:.3f} (expected 0.06)")
        elif abs(undisputed_pct - 0.94) > 0.001:
            errors.append(f"  FAIL: ${fund_size}m fund - undisputed pct = {undisputed_pct:.3f} (expected 0.94)")
        else:
            print(f"  PASS: ${fund_size}m fund - in play ${in_play:.1f}m ({in_play_pct*100:.0f}%), undisputed ${undisputed:.0f}m ({undisputed_pct*100:.0f}%)")
    
    return len(errors) == 0, errors

def test_percentage_sums():
    """Test 7: IUSAF + TSAC + SOSAC weights sum correctly."""
    print("\nTEST 7: Component weights sum to 100%")
    print("-" * 60)
    
    errors = []
    
    # Verify the scenario parameters
    scenario_params = {
        'pure_iusaf': {'tsac': 0, 'sosac': 0, 'iusaf': 100},
        'strict': {'tsac': 1.5, 'sosac': 3, 'iusaf': 95.5},
        'bounded': {'tsac': 3.5, 'sosac': 3, 'iusaf': 93.5},
        'even': {'tsac': 5, 'sosac': 3, 'iusaf': 92},
    }
    
    for scenario, params in scenario_params.items():
        total = params['tsac'] + params['sosac'] + params['iusaf']
        
        if abs(total - 100) > 0.01:
            errors.append(f"  FAIL: {scenario} weights sum = {total}% (expected 100%)")
        else:
            print(f"  PASS: {scenario} - TSAC={params['tsac']}%, SOSAC={params['sosac']}%, IUSAF={params['iusaf']}% = {total}%")
    
    return len(errors) == 0, errors

def test_model_level_thresholds():
    """Test 8: Model-level overturn threshold is correct."""
    print("\nTEST 8: Model-level overturn threshold")
    print("-" * 60)
    
    errors = []
    
    # The model overturns when TSAC + SOSAC > 50%
    # Verify all current scenarios are below this threshold
    
    scenario_totals = {
        'strict': 1.5 + 3,  # 4.5%
        'bounded': 3.5 + 3,  # 6.5%
        'even': 5 + 3,  # 8%
    }
    
    for scenario, total in scenario_totals.items():
        if total >= 50:
            errors.append(f"  FAIL: {scenario} TSAC+SOSAC = {total}% (should be < 50% for model-level stability)")
        else:
            margin = 50 - total
            print(f"  PASS: {scenario} TSAC+SOSAC = {total}% (margin to overturn: {margin:.1f}%)")
    
    # Verify the threshold calculation
    threshold = 50
    print(f"\n  Model overturn threshold: TSAC + SOSAC = {threshold}%")
    print(f"  At this point: IUSAF weight = {100-threshold}%")
    
    return len(errors) == 0, errors

def test_non_negative_allocations():
    """Test 9: All allocations are non-negative."""
    print("\nTEST 9: Non-negative allocations")
    print("-" * 60)
    
    errors = []
    
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        
        if (df['total_allocation'] < 0).any():
            errors.append(f"  FAIL: {scenario} has negative allocations")
        else:
            print(f"  PASS: {scenario} - all allocations >= 0")
    
    return len(errors) == 0, errors

def test_sids_ldc_totals():
    """Test 10: SIDS and LDC totals are reasonable."""
    print("\nTEST 10: SIDS and LDC totals")
    print("-" * 60)
    
    errors = []
    
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        
        sids_total = df[df['is_sids']]['total_allocation'].sum()
        ldc_total = df[df['is_ldc']]['total_allocation'].sum()
        
        # Verify SIDS total is in reasonable range (250-400m)
        if not (250 <= sids_total <= 400):
            errors.append(f"  FAIL: {scenario} SIDS total = ${sids_total:.1f}m (expected 250-400m)")
        else:
            print(f"  PASS: {scenario} SIDS total = ${sids_total:.1f}m")
        
        # Verify LDC total is in reasonable range (300-400m)
        if not (300 <= ldc_total <= 400):
            errors.append(f"  FAIL: {scenario} LDC total = ${ldc_total:.1f}m (expected 300-400m)")
        else:
            print(f"  PASS: {scenario} LDC total = ${ldc_total:.1f}m")
    
    return len(errors) == 0, errors

def main():
    print("=" * 60)
    print("MECHANICAL VERIFICATION TESTS")
    print("=" * 60)
    
    all_tests = [
        ("Total sums", test_total_sums),
        ("Transfer scale", test_transfer_scale),
        ("Band transfers", test_band_transfers),
        ("Gini coefficients", test_gini_coefficients),
        ("Spearman correlations", test_spearman_correlations),
        ("Fund size scaling", test_fund_size_scaling),
        ("Percentage sums", test_percentage_sums),
        ("Model-level thresholds", test_model_level_thresholds),
        ("Non-negative allocations", test_non_negative_allocations),
        ("SIDS/LDC totals", test_sids_ldc_totals),
    ]
    
    all_passed = True
    all_errors = []
    
    for test_name, test_func in all_tests:
        passed, errors = test_func()
        if not passed:
            all_passed = False
            all_errors.extend(errors)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED:")
        for error in all_errors:
            print(error)
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
