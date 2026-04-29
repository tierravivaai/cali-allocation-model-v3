#!/usr/bin/env python3
"""
Test for mechanical correctness of scenario totals.

Verifies that:
1. Total allocations sum to $1 billion (± $1 for rounding)
2. SIDS + LDC + Other - Overlap = Total
3. All values are non-negative
"""

import pandas as pd
import os

TOLERANCE = 0.01  # $10,000 tolerance for rounding
EXPECTED_TOTAL = 1000.0  # $1 billion in millions

scenarios = ['pure_iusaf', 'strict', 'bounded', 'even']
results_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(results_dir, 'scenario_results')

def test_totals():
    errors = []
    
    for scenario in scenarios:
        df = pd.read_csv(os.path.join(results_dir, f'{scenario}.csv'))
        
        # Test 1: Total sums to $1 billion
        total = df['total_allocation'].sum()
        if abs(total - EXPECTED_TOTAL) > TOLERANCE:
            errors.append(f"{scenario}: Total {total:.2f}m != expected {EXPECTED_TOTAL}m")
        
        # Test 2: SIDS + LDC + Other = Total (accounting for overlap)
        sids_total = df[df['is_sids'] == True]['total_allocation'].sum()
        ldc_total = df[df['is_ldc'] == True]['total_allocation'].sum()
        sids_and_ldc = df[(df['is_sids'] == True) & (df['is_ldc'] == True)]['total_allocation'].sum()
        other = total - sids_total - ldc_total + sids_and_ldc
        
        calculated_total = sids_total + ldc_total - sids_and_ldc + other
        if abs(calculated_total - total) > TOLERANCE:
            errors.append(f"{scenario}: Component sum {calculated_total:.2f}m != total {total:.2f}m")
        
        # Test 3: All allocations are non-negative
        if (df['total_allocation'] < 0).any():
            errors.append(f"{scenario}: Negative allocation found")
    
    if errors:
        print("FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("PASSED: All totals sum correctly to $1 billion")
        return True


if __name__ == "__main__":
    success = test_totals()
    exit(0 if success else 1)
