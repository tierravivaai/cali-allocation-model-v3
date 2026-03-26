# IUSAF Band Crossover Risk Analysis

## Scope
This analysis uses the **current eligible-party set** under the live model configuration: band inversion, `exclude_high_income=True`, `TSAC=0`, `SOSAC=0`. It therefore reflects the same party universe used for the current IUSAF-only allocation baseline.

## Statistical method
Band assignment follows the implemented rule in `logic/calculator.py`: **`min_threshold < un_share <= max_threshold`**.

For each eligible Party, crossover risk is measured as:

- `abs_margin` = absolute distance from the Party's current `un_share` to the nearest band threshold
- `pct_change_to_cross` = `abs_margin / un_share × 100`
- `cross_if_direction` indicates whether the Party would cross bands under an **increase** or **decrease** in `un_share`

A Party ranked near the top of the risk table can cross bands more easily than a Party ranked near the bottom.

## Band-level summary

| band_id | band_label | parties | exact_threshold_cases | min_pct_change | median_pct_change | max_pct_change |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Band 1: <= 0.001% | 28 | 28 | 0.0 | 0.0 | 0.0 |
| 2 | Band 2: 0.001% - 0.01% | 59 | 11 | 0.0 | 50.0 | 80.0 |
| 3 | Band 3: 0.01% - 0.1% | 30 | 0 | 9.090909090909085 | 54.1958041958042 | 78.26086956521738 |
| 4 | Band 4: 0.1% - 1.0% | 18 | 0 | 18.032786885245898 | 47.611990070028526 | 79.59183673469387 |
| 5 | Band 5: 1.0% - 10.0% | 3 | 0 | 9.584086799276681 | 12.049252418645558 | 29.12827781715096 |
| 6 | Band 6: > 10.0% | 1 | 0 | 50.009998000399925 | 50.009998000399925 | 50.009998000399925 |

## Exact-threshold cases
These Parties already sit exactly on a published band edge. Under the implemented rule they remain in the lower band, but **any movement in the crossover direction would change their band**.

| risk_rank | party | band_label | un_share | nearest_threshold | cross_if_direction |
| --- | --- | --- | --- | --- | --- |
| 1 | Belize | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 2 | Bhutan | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 3 | Burundi | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 4 | Cabo Verde | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 5 | Central African Republic | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 6 | Comoros | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 7 | Dominica | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 8 | Eritrea | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 9 | Gambia | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 10 | Grenada | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 11 | Guinea-Bissau | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 12 | Kiribati | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 13 | Lesotho | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 14 | Liberia | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 15 | Marshall Islands | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 16 | Micronesia (Federated States of) | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 17 | Nauru | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 18 | Palau | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 19 | Saint Kitts and Nevis | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 20 | Saint Vincent and the Grenadines | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 21 | Samoa | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 22 | Sao Tome and Principe | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 23 | Sierra Leone | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 24 | Solomon Islands | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 25 | Timor-Leste | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 26 | Tonga | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 27 | Tuvalu | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 28 | Vanuatu | Band 1: <= 0.001% | 0.001 | 0.001 | increase |
| 29 | Albania | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 30 | Angola | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 31 | Bangladesh | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 32 | Democratic Republic of the Congo | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 33 | Ethiopia | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 34 | Honduras | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 35 | Mauritius | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 36 | Myanmar | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 37 | Nepal | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 38 | Uganda | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |
| 39 | United Republic of Tanzania | Band 2: 0.001% - 0.01% | 0.010 | 0.010 | increase |

## Parties within 10% of a band crossover

| risk_rank | party | band_label | un_share | nearest_edge | nearest_threshold | cross_if_direction | pct_change_to_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Belize | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 2 | Bhutan | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 3 | Burundi | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 4 | Cabo Verde | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 5 | Central African Republic | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 6 | Comoros | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 7 | Dominica | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 8 | Eritrea | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 9 | Gambia | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 10 | Grenada | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 11 | Guinea-Bissau | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 12 | Kiribati | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 13 | Lesotho | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 14 | Liberia | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 15 | Marshall Islands | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 16 | Micronesia (Federated States of) | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 17 | Nauru | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 18 | Palau | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 19 | Saint Kitts and Nevis | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 20 | Saint Vincent and the Grenadines | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 21 | Samoa | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 22 | Sao Tome and Principe | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 23 | Sierra Leone | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 24 | Solomon Islands | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 25 | Timor-Leste | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 26 | Tonga | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 27 | Tuvalu | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 28 | Vanuatu | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 29 | Albania | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 30 | Angola | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 31 | Bangladesh | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 32 | Democratic Republic of the Congo | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 33 | Ethiopia | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 34 | Honduras | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 35 | Mauritius | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 36 | Myanmar | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 37 | Nepal | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 38 | Uganda | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 39 | United Republic of Tanzania | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 40 | Gabon | Band 3: 0.01% - 0.1% | 0.011 | lower | 0.010 | decrease | 9.09% |
| 41 | Guyana | Band 3: 0.01% - 0.1% | 0.011 | lower | 0.010 | decrease | 9.09% |
| 42 | India | Band 5: 1.0% - 10.0% | 1.106 | lower | 1.000 | decrease | 9.58% |

## Parties within 20% of a band crossover

| risk_rank | party | band_label | un_share | nearest_edge | nearest_threshold | cross_if_direction | pct_change_to_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Belize | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 2 | Bhutan | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 3 | Burundi | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 4 | Cabo Verde | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 5 | Central African Republic | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 6 | Comoros | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 7 | Dominica | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 8 | Eritrea | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 9 | Gambia | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 10 | Grenada | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 11 | Guinea-Bissau | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 12 | Kiribati | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 13 | Lesotho | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 14 | Liberia | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 15 | Marshall Islands | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 16 | Micronesia (Federated States of) | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 17 | Nauru | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 18 | Palau | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 19 | Saint Kitts and Nevis | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 20 | Saint Vincent and the Grenadines | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 21 | Samoa | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 22 | Sao Tome and Principe | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 23 | Sierra Leone | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 24 | Solomon Islands | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 25 | Timor-Leste | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 26 | Tonga | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 27 | Tuvalu | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 28 | Vanuatu | Band 1: <= 0.001% | 0.001 | upper | 0.001 | increase | 0.00% |
| 29 | Albania | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 30 | Angola | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 31 | Bangladesh | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 32 | Democratic Republic of the Congo | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 33 | Ethiopia | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 34 | Honduras | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 35 | Mauritius | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 36 | Myanmar | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 37 | Nepal | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 38 | Uganda | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 39 | United Republic of Tanzania | Band 2: 0.001% - 0.01% | 0.010 | upper | 0.010 | increase | 0.00% |
| 40 | Gabon | Band 3: 0.01% - 0.1% | 0.011 | lower | 0.010 | decrease | 9.09% |
| 41 | Guyana | Band 3: 0.01% - 0.1% | 0.011 | lower | 0.010 | decrease | 9.09% |
| 42 | India | Band 5: 1.0% - 10.0% | 1.106 | lower | 1.000 | decrease | 9.58% |
| 43 | Georgia | Band 2: 0.001% - 0.01% | 0.009 | upper | 0.010 | increase | 11.11% |
| 44 | Papua New Guinea | Band 2: 0.001% - 0.01% | 0.009 | upper | 0.010 | increase | 11.11% |
| 45 | Mexico | Band 5: 1.0% - 10.0% | 1.137 | lower | 1.000 | decrease | 12.05% |
| 46 | Algeria | Band 3: 0.01% - 0.1% | 0.087 | upper | 0.100 | increase | 14.94% |
| 47 | Cuba | Band 4: 0.1% - 1.0% | 0.122 | lower | 0.100 | decrease | 18.03% |
| 48 | Pakistan | Band 4: 0.1% - 1.0% | 0.123 | lower | 0.100 | decrease | 18.70% |

## Interpretation

- **Band 6 is statistically isolated** in the current eligible-party set: China would need a drop of about **50.01%** in `un_share` to fall back to Band 5.
- The main source of fragility is not Band 6 but the large set of Parties sitting exactly at **0.001** or **0.010**.
- Outside those exact-threshold cases, the most borderline Parties are **Gabon**, **Guyana**, **India**, **Georgia**, **Papua New Guinea**, **Algeria**, **Cuba**, **Pakistan**, and **Mexico**.
- The companion CSV provides the full ranking for all eligible Parties, sorted from highest to lowest crossover risk.
