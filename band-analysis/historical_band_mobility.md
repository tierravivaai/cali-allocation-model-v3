# Historical IUSAF Band Mobility Assessment

## Why this is a stronger test
UN assessment rates are formal percentages for apportioning the United Nations regular budget and are adopted by the General Assembly. That means a Party can only change bands if its approved UN assessment rate changes enough to cross one of the current band thresholds. Historical movement in those approved rates is therefore direct evidence on whether band crossover is common or rare.

## Data and method

- Resolution `A/RES/79/249` confirms that the General Assembly sets the scale of assessments for `2025–2027` and that the minimum, LDC cap and maximum rates are formal UN-approved values.
- Historical rates come from `reference/UNGA-budget/Scale of Assessments for RB 1946-2027.xlsx`.
- The analysis covers the **current eligible parties with positive UN shares** in the model (`exclude_high_income=True`, IUSAF-only baseline).
- For each historical year, the Party's UN share is reclassified using the **current six-band thresholds**. This asks a policy-relevant question: if today's band structure had been applied over the recent past, how often would Parties have crossed bands?

## Headline result

| window | years | parties_with_history | parties_that_moved | share_that_moved_pct |
| --- | --- | --- | --- | --- |
| last_20_years | 2008-2027 | 139 | 61 | 43.885 |
| last_10_years | 2018-2027 | 139 | 23 | 16.547 |
| last_5_years | 2023-2027 | 139 | 10 | 7.194 |

## Parties that moved bands in the last 20 years

| mobility_rank | party | current_band | last_20_years_bands_seen | last_20_years_band_changes | last_20_years_min_un_share | last_20_years_max_un_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Guyana | Band 3: 0.01% - 0.1% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 2 | 0.001 | 0.011 |
| 2 | Algeria | Band 3: 0.01% - 0.1% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 2 | 0.085 | 0.161 |
| 3 | Cuba | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.054 | 0.122 |
| 4 | Djibouti | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 5 | Equatorial Guinea | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 2 | 0.002 | 0.016 |
| 6 | Mauritius | Band 2: 0.001% - 0.01% | Band 3: 0.01% - 0.1%; Band 2: 0.001% - 0.01% | 1 | 0.010 | 0.019 |
| 7 | Saint Kitts and Nevis | Band 1: <= 0.001% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 2 | 0.001 | 0.002 |
| 8 | Somalia | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 9 | Venezuela (Bolivarian Republic of) | Band 3: 0.01% - 0.1% | Band 4: 0.1% - 1.0%; Band 3: 0.01% - 0.1% | 1 | 0.069 | 0.728 |
| 10 | Viet Nam | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.024 | 0.159 |
| 11 | Cameroon | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 3 | 0.009 | 0.014 |
| 12 | China | Band 6: > 10.0% | Band 5: 1.0% - 10.0%; Band 6: > 10.0% | 1 | 2.667 | 20.004 |
| 13 | Côte d’Ivoire | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 3 | 0.009 | 0.024 |
| 14 | India | Band 5: 1.0% - 10.0% | Band 4: 0.1% - 1.0%; Band 5: 1.0% - 10.0% | 1 | 0.450 | 1.106 |
| 15 | Libya | Band 3: 0.01% - 0.1% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 2 | 0.018 | 0.142 |
| 16 | Pakistan | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.059 | 0.123 |
| 17 | Saint Lucia | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 18 | Seychelles | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01%; Band 1: <= 0.001% | 2 | 0.001 | 0.002 |
| 19 | Syrian Arab Republic | Band 2: 0.001% - 0.01% | Band 3: 0.01% - 0.1%; Band 2: 0.001% - 0.01% | 1 | 0.006 | 0.036 |
| 20 | Timor-Leste | Band 1: <= 0.001% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 2 | 0.001 | 0.003 |
| 21 | Togo | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 22 | Türkiye | Band 4: 0.1% - 1.0% | Band 4: 0.1% - 1.0%; Band 5: 1.0% - 10.0% | 2 | 0.381 | 1.371 |
| 23 | Ukraine | Band 3: 0.01% - 0.1% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 2 | 0.045 | 0.103 |
| 24 | Afghanistan | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.007 |
| 25 | Azerbaijan | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.005 | 0.060 |
| 26 | Benin | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.005 |
| 27 | Bolivia (Plurinational State of) | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.006 | 0.019 |
| 28 | Bosnia and Herzegovina | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.006 | 0.017 |
| 29 | Brazil | Band 5: 1.0% - 10.0% | Band 4: 0.1% - 1.0%; Band 5: 1.0% - 10.0% | 1 | 0.876 | 3.823 |
| 30 | Cambodia | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.008 |
| 31 | Chad | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.005 |
| 32 | Congo | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.006 |
| 33 | Egypt | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.088 | 0.186 |
| 34 | Gabon | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.008 | 0.020 |
| 35 | Ghana | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.004 | 0.025 |
| 36 | Guinea | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 3 | 0.001 | 0.004 |
| 37 | Iraq | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.015 | 0.131 |
| 38 | Jamaica | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 2 | 0.007 | 0.014 |
| 39 | Kazakhstan | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.029 | 0.191 |
| 40 | Kenya | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.010 | 0.037 |
| 41 | Kyrgyzstan | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.003 |
| 42 | Lao People's Democratic Republic | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.007 |
| 43 | Malawi | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.003 |
| 44 | Maldives | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.004 |
| 45 | Mali | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.005 |
| 46 | Mauritania | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.003 |
| 47 | Mongolia | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.005 |
| 48 | Montenegro | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.005 |
| 49 | Mozambique | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.004 |
| 50 | Niger | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.004 |
| 51 | Nigeria | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.048 | 0.250 |
| 52 | Paraguay | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.005 | 0.026 |
| 53 | Peru | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.078 | 0.163 |
| 54 | Philippines | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.078 | 0.212 |
| 55 | Republic of Moldova | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.006 |
| 56 | Rwanda | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.003 |
| 57 | Suriname | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.006 |
| 58 | Tajikistan | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.004 |
| 59 | Turkmenistan | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.006 | 0.036 |
| 60 | Uzbekistan | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.008 | 0.032 |
| 61 | Zambia | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.009 |

## Parties that moved bands in the last 10 years

| mobility_rank | party | current_band | last_10_years_bands_seen | last_10_years_band_changes | last_10_years_min_un_share | last_10_years_max_un_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Guyana | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.002 | 0.011 |
| 2 | Algeria | Band 3: 0.01% - 0.1% | Band 4: 0.1% - 1.0%; Band 3: 0.01% - 0.1% | 1 | 0.087 | 0.161 |
| 3 | Cuba | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.065 | 0.122 |
| 4 | Djibouti | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 5 | Equatorial Guinea | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 2 | 0.008 | 0.016 |
| 6 | Mauritius | Band 2: 0.001% - 0.01% | Band 3: 0.01% - 0.1%; Band 2: 0.001% - 0.01% | 1 | 0.010 | 0.019 |
| 7 | Saint Kitts and Nevis | Band 1: <= 0.001% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 2 | 0.001 | 0.002 |
| 8 | Somalia | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 9 | Venezuela (Bolivarian Republic of) | Band 3: 0.01% - 0.1% | Band 4: 0.1% - 1.0%; Band 3: 0.01% - 0.1% | 1 | 0.069 | 0.728 |
| 10 | Viet Nam | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.058 | 0.159 |
| 11 | Cameroon | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.010 | 0.014 |
| 12 | China | Band 6: > 10.0% | Band 5: 1.0% - 10.0%; Band 6: > 10.0% | 1 | 7.921 | 20.004 |
| 13 | Côte d’Ivoire | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.009 | 0.024 |
| 14 | India | Band 5: 1.0% - 10.0% | Band 4: 0.1% - 1.0%; Band 5: 1.0% - 10.0% | 1 | 0.737 | 1.106 |
| 15 | Libya | Band 3: 0.01% - 0.1% | Band 4: 0.1% - 1.0%; Band 3: 0.01% - 0.1% | 1 | 0.018 | 0.125 |
| 16 | Pakistan | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.093 | 0.123 |
| 17 | Saint Lucia | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 18 | Seychelles | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 19 | Syrian Arab Republic | Band 2: 0.001% - 0.01% | Band 3: 0.01% - 0.1%; Band 2: 0.001% - 0.01% | 1 | 0.006 | 0.024 |
| 20 | Timor-Leste | Band 1: <= 0.001% | Band 2: 0.001% - 0.01%; Band 1: <= 0.001% | 1 | 0.001 | 0.003 |
| 21 | Togo | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 22 | Türkiye | Band 4: 0.1% - 1.0% | Band 5: 1.0% - 10.0%; Band 4: 0.1% - 1.0% | 1 | 0.685 | 1.371 |
| 23 | Ukraine | Band 3: 0.01% - 0.1% | Band 4: 0.1% - 1.0%; Band 3: 0.01% - 0.1% | 1 | 0.056 | 0.103 |

## Parties that moved bands in the last 5 years

| mobility_rank | party | current_band | last_5_years_bands_seen | last_5_years_band_changes | last_5_years_min_un_share | last_5_years_max_un_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Guyana | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | 1 | 0.004 | 0.011 |
| 2 | Algeria | Band 3: 0.01% - 0.1% | Band 4: 0.1% - 1.0%; Band 3: 0.01% - 0.1% | 1 | 0.087 | 0.109 |
| 3 | Cuba | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.095 | 0.122 |
| 4 | Djibouti | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 5 | Equatorial Guinea | Band 2: 0.001% - 0.01% | Band 3: 0.01% - 0.1%; Band 2: 0.001% - 0.01% | 1 | 0.008 | 0.012 |
| 6 | Mauritius | Band 2: 0.001% - 0.01% | Band 3: 0.01% - 0.1%; Band 2: 0.001% - 0.01% | 1 | 0.010 | 0.019 |
| 7 | Saint Kitts and Nevis | Band 1: <= 0.001% | Band 2: 0.001% - 0.01%; Band 1: <= 0.001% | 1 | 0.001 | 0.002 |
| 8 | Somalia | Band 2: 0.001% - 0.01% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01% | 1 | 0.001 | 0.002 |
| 9 | Venezuela (Bolivarian Republic of) | Band 3: 0.01% - 0.1% | Band 4: 0.1% - 1.0%; Band 3: 0.01% - 0.1% | 1 | 0.069 | 0.175 |
| 10 | Viet Nam | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | 1 | 0.093 | 0.159 |

## Check on currently borderline Parties

| party | current_band | last_20_years_bands_seen | last_10_years_bands_seen | last_5_years_bands_seen |
| --- | --- | --- | --- | --- |
| Guyana | Band 3: 0.01% - 0.1% | Band 1: <= 0.001%; Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% |
| Algeria | Band 3: 0.01% - 0.1% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | Band 4: 0.1% - 1.0%; Band 3: 0.01% - 0.1% | Band 4: 0.1% - 1.0%; Band 3: 0.01% - 0.1% |
| Cuba | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% |
| China | Band 6: > 10.0% | Band 5: 1.0% - 10.0%; Band 6: > 10.0% | Band 5: 1.0% - 10.0%; Band 6: > 10.0% | Band 6: > 10.0% |
| India | Band 5: 1.0% - 10.0% | Band 4: 0.1% - 1.0%; Band 5: 1.0% - 10.0% | Band 4: 0.1% - 1.0%; Band 5: 1.0% - 10.0% | Band 5: 1.0% - 10.0% |
| Pakistan | Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | Band 3: 0.01% - 0.1%; Band 4: 0.1% - 1.0% | Band 4: 0.1% - 1.0% |
| Brazil | Band 5: 1.0% - 10.0% | Band 4: 0.1% - 1.0%; Band 5: 1.0% - 10.0% | Band 5: 1.0% - 10.0% | Band 5: 1.0% - 10.0% |
| Gabon | Band 3: 0.01% - 0.1% | Band 2: 0.001% - 0.01%; Band 3: 0.01% - 0.1% | Band 3: 0.01% - 0.1% | Band 3: 0.01% - 0.1% |
| Georgia | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01% |
| Mexico | Band 5: 1.0% - 10.0% | Band 5: 1.0% - 10.0% | Band 5: 1.0% - 10.0% | Band 5: 1.0% - 10.0% |
| Papua New Guinea | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01% | Band 2: 0.001% - 0.01% |

## Interpretation

- If a Party has stayed in the same band across the last `20`, `10`, and `5` years, that is strong empirical evidence that near-term crossover risk is low absent a material shift in its approved UN assessment rate.
- If a Party has moved between bands historically, it should be treated as a genuinely mobile case and monitored more closely.
- Exact-threshold Parties remain the most fragile by construction, but the historical test helps separate **formal-but-stable threshold positions** from **genuinely mobile band positions**.

## Coverage note
All current eligible Parties with positive UN shares were matched to the historical workbook.
