# Tables

*Generated from `output/tables/*.csv` by `python/make_tables.py`. Dollar amounts are 2024 dollars; present values are discounted at 3% a year to age 65. HRS estimates use the respondent analysis weight, or the nursing-home resident weight for residents; MCBS estimates use the Cost Supplement weight with Fay-adjusted balanced repeated replication.*


**Table 1.** The HRS panel, waves 4 to 16 (1998 to 2022), respondents aged 50 and over.

| Quantity | Value |
|---|---:|
| Respondents with at least one classified interview | 40,354 |
| Person-interviews with a classified state | 237,944 |
| Intervals between interviews | 197,258 |
| Deaths | 16,160 |
| Deaths dated to the year only, placed at mid-year | 139 |
| Known-alive censored observations | 8,548 |
| Person-years in censored observations | 39,760.5 |
| Observations dropped for missing race | 375 |
| Mean interval length, years | 2.1 |
| Waves | 4-16 (1998-2022) |
| Weighted share of person-interviews in Healthy, % | 16.3 |
| Weighted share of person-interviews in Chronic illness, % | 67.5 |
| Weighted share of person-interviews in Disability, % | 10.6 |
| Weighted share of person-interviews in Severe disability at home, % | 4.0 |
| Weighted share of person-interviews in Nursing home, % | 1.6 |

**Table 2.** Transition intensities among health states.

*Log-linear intensities with a linear spline in age (knots at 70 and 85), fitted by maximum likelihood to interval-censored transitions, exact deaths and known-alive censoring. Reference: male, no college, non-Hispanic white, age 65. Standard errors clustered on households (sandwich); hazard ratios with 95% intervals. Likelihood-ratio test of the education and race-ethnicity terms: 1,756.2 on 36 degrees of freedom.*

| Transition | Term | Estimate | SE | Hazard ratio | 95% low | 95% high |
|---|---:|---:|---:|---:|---:|---:|
| H to C | log rate at 65 | -2.136 | 0.032 |  |  |  |
| H to C | age, per 10 years | 0.211 | 0.029 | 1.23 | 1.17 | 1.31 |
| H to C | age over 70, change in slope | -0.189 | 0.071 | 0.83 | 0.72 | 0.95 |
| H to C | age over 85, change in slope | -0.106 | 0.331 | 0.90 | 0.47 | 1.72 |
| H to C | female | -0.009 | 0.029 | 0.99 | 0.94 | 1.05 |
| H to C | any college | -0.117 | 0.029 | 0.89 | 0.84 | 0.94 |
| H to C | nonwhite or Hispanic | 0.025 | 0.031 | 1.03 | 0.96 | 1.09 |
| H to D | log rate at 65 | -4.562 | 0.155 |  |  |  |
| H to D | age, per 10 years | -0.029 | 0.139 | 0.97 | 0.74 | 1.27 |
| H to D | age over 70, change in slope | 1.348 | 0.262 | 3.85 | 2.31 | 6.43 |
| H to D | age over 85, change in slope | -0.081 | 0.332 | 0.92 | 0.48 | 1.77 |
| H to D | female | -0.075 | 0.122 | 0.93 | 0.73 | 1.18 |
| H to D | any college | -0.333 | 0.120 | 0.72 | 0.57 | 0.91 |
| H to D | nonwhite or Hispanic | 0.546 | 0.120 | 1.73 | 1.36 | 2.18 |
| H to X | log rate at 65 | -5.499 | 0.209 |  |  |  |
| H to X | age, per 10 years | 0.951 | 0.286 | 2.59 | 1.48 | 4.53 |
| H to X | age over 70, change in slope | -0.025 | 0.457 | 0.98 | 0.40 | 2.39 |
| H to X | age over 85, change in slope | 0.067 | 0.689 | 1.07 | 0.28 | 4.13 |
| H to X | female | -0.879 | 0.225 | 0.42 | 0.27 | 0.64 |
| H to X | any college | -0.765 | 0.230 | 0.47 | 0.30 | 0.73 |
| H to X | nonwhite or Hispanic | 0.339 | 0.215 | 1.40 | 0.92 | 2.14 |
| C to D | log rate at 65 | -2.875 | 0.029 |  |  |  |
| C to D | age, per 10 years | -0.048 | 0.028 | 0.95 | 0.90 | 1.01 |
| C to D | age over 70, change in slope | 0.678 | 0.049 | 1.97 | 1.79 | 2.17 |
| C to D | age over 85, change in slope | 0.122 | 0.089 | 1.13 | 0.95 | 1.35 |
| C to D | female | 0.076 | 0.025 | 1.08 | 1.03 | 1.13 |
| C to D | any college | -0.329 | 0.027 | 0.72 | 0.68 | 0.76 |
| C to D | nonwhite or Hispanic | 0.279 | 0.029 | 1.32 | 1.25 | 1.40 |
| C to L | log rate at 65 | -12.151 | 1.817 |  |  |  |
| C to L | age, per 10 years | -0.051 | 0.347 | 0.95 | 0.48 | 1.88 |
| C to L | age over 70, change in slope | 0.602 | 0.665 | 1.83 | 0.50 | 6.73 |
| C to L | age over 85, change in slope | -5.940 | 4.148 | 0.00 | 0.00 | 8.94 |
| C to L | female | 1.140 | 0.686 | 3.13 | 0.81 | 12.00 |
| C to L | any college | -1.534 | 0.734 | 0.22 | 0.05 | 0.91 |
| C to L | nonwhite or Hispanic | 5.953 | 1.517 | 385.07 | 19.68 | 7,534.67 |
| C to N | log rate at 65 | -6.693 | 0.184 |  |  |  |
| C to N | age, per 10 years | 0.650 | 0.240 | 1.92 | 1.20 | 3.06 |
| C to N | age over 70, change in slope | 0.941 | 0.359 | 2.56 | 1.27 | 5.18 |
| C to N | age over 85, change in slope | -0.094 | 0.266 | 0.91 | 0.54 | 1.53 |
| C to N | female | -0.085 | 0.125 | 0.92 | 0.72 | 1.17 |
| C to N | any college | -0.053 | 0.127 | 0.95 | 0.74 | 1.22 |
| C to N | nonwhite or Hispanic | -0.143 | 0.154 | 0.87 | 0.64 | 1.17 |
| C to X | log rate at 65 | -4.258 | 0.041 |  |  |  |
| C to X | age, per 10 years | 0.562 | 0.053 | 1.75 | 1.58 | 1.95 |
| C to X | age over 70, change in slope | 0.231 | 0.087 | 1.26 | 1.06 | 1.50 |
| C to X | age over 85, change in slope | 0.175 | 0.125 | 1.19 | 0.93 | 1.52 |
| C to X | female | -0.578 | 0.037 | 0.56 | 0.52 | 0.60 |
| C to X | any college | -0.246 | 0.039 | 0.78 | 0.72 | 0.84 |
| C to X | nonwhite or Hispanic | 0.110 | 0.043 | 1.12 | 1.03 | 1.21 |
| D to H | log rate at 65 | -4.716 | 0.131 |  |  |  |
| D to H | age, per 10 years | -0.777 | 0.123 | 0.46 | 0.36 | 0.59 |
| D to H | age over 70, change in slope | 0.667 | 0.262 | 1.95 | 1.16 | 3.26 |
| D to H | age over 85, change in slope | 0.367 | 0.526 | 1.44 | 0.51 | 4.05 |
| D to H | female | -0.390 | 0.117 | 0.68 | 0.54 | 0.85 |
| D to H | any college | 0.216 | 0.119 | 1.24 | 0.98 | 1.57 |
| D to H | nonwhite or Hispanic | 0.198 | 0.119 | 1.22 | 0.97 | 1.54 |
| D to C | log rate at 65 | -1.081 | 0.030 |  |  |  |
| D to C | age, per 10 years | -0.035 | 0.029 | 0.97 | 0.91 | 1.02 |
| D to C | age over 70, change in slope | -0.139 | 0.055 | 0.87 | 0.78 | 0.97 |
| D to C | age over 85, change in slope | -0.038 | 0.128 | 0.96 | 0.75 | 1.24 |
| D to C | female | 0.018 | 0.029 | 1.02 | 0.96 | 1.08 |
| D to C | any college | 0.082 | 0.029 | 1.08 | 1.02 | 1.15 |
| D to C | nonwhite or Hispanic | -0.039 | 0.030 | 0.96 | 0.91 | 1.02 |
| D to L | log rate at 65 | -1.920 | 0.047 |  |  |  |
| D to L | age, per 10 years | -0.112 | 0.052 | 0.89 | 0.81 | 0.99 |
| D to L | age over 70, change in slope | 0.440 | 0.090 | 1.55 | 1.30 | 1.85 |
| D to L | age over 85, change in slope | 0.093 | 0.115 | 1.10 | 0.88 | 1.37 |
| D to L | female | -0.079 | 0.044 | 0.92 | 0.85 | 1.01 |
| D to L | any college | -0.090 | 0.043 | 0.91 | 0.84 | 0.99 |
| D to L | nonwhite or Hispanic | 0.283 | 0.045 | 1.33 | 1.22 | 1.45 |
| D to N | log rate at 65 | -5.726 | 0.529 |  |  |  |
| D to N | age, per 10 years | 1.203 | 0.836 | 3.33 | 0.65 | 17.14 |
| D to N | age over 70, change in slope | 0.379 | 1.017 | 1.46 | 0.20 | 10.72 |
| D to N | age over 85, change in slope | -0.774 | 0.389 | 0.46 | 0.22 | 0.99 |
| D to N | female | 0.492 | 0.245 | 1.64 | 1.01 | 2.64 |
| D to N | any college | -0.246 | 0.160 | 0.78 | 0.57 | 1.07 |
| D to N | nonwhite or Hispanic | -0.937 | 0.326 | 0.39 | 0.21 | 0.74 |
| D to X | log rate at 65 | -2.948 | 0.079 |  |  |  |
| D to X | age, per 10 years | 0.843 | 0.113 | 2.32 | 1.86 | 2.90 |
| D to X | age over 70, change in slope | -0.587 | 0.178 | 0.56 | 0.39 | 0.79 |
| D to X | age over 85, change in slope | 0.308 | 0.217 | 1.36 | 0.89 | 2.08 |
| D to X | female | -0.463 | 0.081 | 0.63 | 0.54 | 0.74 |
| D to X | any college | -0.328 | 0.087 | 0.72 | 0.61 | 0.85 |
| D to X | nonwhite or Hispanic | -0.305 | 0.096 | 0.74 | 0.61 | 0.89 |
| L to D | log rate at 65 | -0.982 | 0.061 |  |  |  |
| L to D | age, per 10 years | -0.240 | 0.055 | 0.79 | 0.71 | 0.88 |
| L to D | age over 70, change in slope | -0.104 | 0.104 | 0.90 | 0.74 | 1.10 |
| L to D | age over 85, change in slope | 0.036 | 0.189 | 1.04 | 0.72 | 1.50 |
| L to D | female | -0.096 | 0.054 | 0.91 | 0.82 | 1.01 |
| L to D | any college | -0.091 | 0.059 | 0.91 | 0.81 | 1.02 |
| L to D | nonwhite or Hispanic | 0.038 | 0.055 | 1.04 | 0.93 | 1.16 |
| L to N | log rate at 65 | -3.281 | 0.167 |  |  |  |
| L to N | age, per 10 years | 1.039 | 0.255 | 2.83 | 1.72 | 4.66 |
| L to N | age over 70, change in slope | -0.567 | 0.354 | 0.57 | 0.28 | 1.14 |
| L to N | age over 85, change in slope | -0.265 | 0.238 | 0.77 | 0.48 | 1.22 |
| L to N | female | -0.063 | 0.142 | 0.94 | 0.71 | 1.24 |
| L to N | any college | -0.091 | 0.124 | 0.91 | 0.72 | 1.17 |
| L to N | nonwhite or Hispanic | -0.615 | 0.153 | 0.54 | 0.40 | 0.73 |
| L to X | log rate at 65 | -2.200 | 0.067 |  |  |  |
| L to X | age, per 10 years | 0.627 | 0.093 | 1.87 | 1.56 | 2.24 |
| L to X | age over 70, change in slope | -0.111 | 0.141 | 0.89 | 0.68 | 1.18 |
| L to X | age over 85, change in slope | -0.029 | 0.131 | 0.97 | 0.75 | 1.26 |
| L to X | female | -0.417 | 0.055 | 0.66 | 0.59 | 0.73 |
| L to X | any college | 0.107 | 0.055 | 1.11 | 1.00 | 1.24 |
| L to X | nonwhite or Hispanic | -0.299 | 0.058 | 0.74 | 0.66 | 0.83 |
| N to D | log rate at 65 | -2.446 | 0.242 |  |  |  |
| N to D | age, per 10 years | -0.543 | 0.262 | 0.58 | 0.35 | 0.97 |
| N to D | age over 70, change in slope | 0.317 | 0.367 | 1.37 | 0.67 | 2.82 |
| N to D | age over 85, change in slope | 0.307 | 0.417 | 1.36 | 0.60 | 3.08 |
| N to D | female | -0.306 | 0.188 | 0.74 | 0.51 | 1.06 |
| N to D | any college | 0.616 | 0.165 | 1.85 | 1.34 | 2.56 |
| N to D | nonwhite or Hispanic | -0.300 | 0.217 | 0.74 | 0.48 | 1.13 |
| N to L | log rate at 65 | -3.344 | 0.400 |  |  |  |
| N to L | age, per 10 years | -0.696 | 0.369 | 0.50 | 0.24 | 1.03 |
| N to L | age over 70, change in slope | 0.122 | 0.591 | 1.13 | 0.35 | 3.60 |
| N to L | age over 85, change in slope | 1.011 | 0.852 | 2.75 | 0.52 | 14.61 |
| N to L | female | 0.355 | 0.440 | 1.43 | 0.60 | 3.38 |
| N to L | any college | 0.617 | 0.294 | 1.85 | 1.04 | 3.29 |
| N to L | nonwhite or Hispanic | -0.026 | 0.339 | 0.97 | 0.50 | 1.89 |
| N to X | log rate at 65 | -1.564 | 0.099 |  |  |  |
| N to X | age, per 10 years | 0.542 | 0.197 | 1.72 | 1.17 | 2.53 |
| N to X | age over 70, change in slope | -0.245 | 0.237 | 0.78 | 0.49 | 1.25 |
| N to X | age over 85, change in slope | 0.195 | 0.107 | 1.22 | 0.99 | 1.50 |
| N to X | female | -0.401 | 0.047 | 0.67 | 0.61 | 0.73 |
| N to X | any college | -0.053 | 0.050 | 0.95 | 0.86 | 1.05 |
| N to X | nonwhite or Hispanic | -0.078 | 0.054 | 0.93 | 0.83 | 1.03 |

**Table 3.** Goodness of fit: observed and expected destination at the next observation, by starting state (percent).

*Expected shares sum the fitted transition probabilities over each observed interval; censored observations are excluded. Cell-level comparisons by age group and interval length are in the replication files (table7f).*

| From | n | H obs | H exp | C obs | C exp | D obs | D exp | L obs | L exp | N obs | N exp | X obs | X exp | Largest gap, pts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Healthy | 31,658 | 77.2% | 77.5% | 18.3% | 18.3% | 2.4% | 2.6% | 0.4% | 0.4% | 0.3% | 0.1% | 1.3% | 1.1% | 0.3 |
| Chronic illness | 141,854 | 0.0% | 0.1% | 84.2% | 85.0% | 8.2% | 8.2% | 1.5% | 1.5% | 0.8% | 0.8% | 5.2% | 4.4% | 0.8 |
| Disability | 25,231 | 1.3% | 0.8% | 33.8% | 33.0% | 36.1% | 39.3% | 12.5% | 12.8% | 2.8% | 2.9% | 13.4% | 11.1% | 3.1 |
| Severe disability at home | 10,100 | 0.2% | 0.2% | 8.1% | 8.2% | 21.1% | 19.3% | 39.8% | 47.0% | 4.9% | 4.7% | 25.8% | 20.5% | 7.2 |
| Nursing home | 4,575 | 0.2% | 0.0% | 2.8% | 1.1% | 2.4% | 3.5% | 2.9% | 2.4% | 41.2% | 56.5% | 50.6% | 36.6% | 15.2 |

**Table 3b.** Mortality: the fitted model, the calibrated model and the 2023 US period life table.

*Entry mix of HRS respondents aged 64 to 66. The multiplier scales death intensities from every live state and equals exp(c0 + c1 (age - 65)/10) at the calibrated values.*

| Sex | e65, fitted | e65, calibrated | e65, life table | Multiplier at 65 | 75 | 85 | 95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| male | 17.49 | 18.23 | 18.19 | 0.86 | 0.89 | 0.91 | 0.93 |
| female | 20.35 | 20.74 | 20.71 | 0.83 | 0.90 | 0.98 | 1.06 |

| Sex | Age | qx, fitted | qx, calibrated | qx, life table | Calibrated / table |
|---|---:|---:|---:|---:|---:|
| male | 65 | 0.0176 | 0.0152 | 0.0162 | 0.94 |
| male | 70 | 0.0258 | 0.0229 | 0.0226 | 1.01 |
| male | 75 | 0.0388 | 0.0351 | 0.0335 | 1.05 |
| male | 80 | 0.0610 | 0.0560 | 0.0542 | 1.03 |
| male | 85 | 0.0966 | 0.0902 | 0.0922 | 0.98 |
| male | 90 | 0.1578 | 0.1498 | 0.1599 | 0.94 |
| male | 95 | 0.2466 | 0.2370 | 0.2563 | 0.92 |
| female | 65 | 0.0113 | 0.0095 | 0.0101 | 0.93 |
| female | 70 | 0.0171 | 0.0151 | 0.0148 | 1.02 |
| female | 75 | 0.0263 | 0.0243 | 0.0237 | 1.02 |
| female | 80 | 0.0429 | 0.0412 | 0.0405 | 1.02 |
| female | 85 | 0.0714 | 0.0710 | 0.0709 | 1.00 |
| female | 90 | 0.1214 | 0.1243 | 0.1285 | 0.97 |
| female | 95 | 0.1955 | 0.2049 | 0.2160 | 0.95 |

**Table 4.** Annual Medicare cost by health state and age band.

*MCBS Cost Supplement cells (age by chronic-condition count) weighted by each HRS state's condition-count mix, with the level in each age band scaled to the MCBS mean. The gradient across states reflects condition counts only; facility, hospice and institutional events are outside the Cost Supplement. The simulation further concentrates this spending in the last year of life (Section 4.3).*

| State | Age | Share 0-1 conditions | 2-3 | 4+ | Cell mix | Scale | Medicare |
|---|---:|---:|---:|---:|---:|---:|---:|
| Healthy | 65-74 | 1.00 | 0.00 | 0.00 | $4,418 | 1.16 | $5,127 |
| Healthy | 75+ | 1.00 | 0.00 | 0.00 | $5,976 | 1.14 | $6,815 |
| Chronic illness | 65-74 | 0.26 | 0.56 | 0.18 | $8,566 | 1.16 | $9,940 |
| Chronic illness | 75+ | 0.18 | 0.57 | 0.24 | $10,512 | 1.14 | $11,987 |
| Disability | 65-74 | 0.11 | 0.46 | 0.43 | $10,925 | 1.16 | $12,678 |
| Disability | 75+ | 0.10 | 0.48 | 0.42 | $11,935 | 1.14 | $13,610 |
| Severe disability at home | 65-74 | 0.06 | 0.37 | 0.56 | $12,063 | 1.16 | $13,998 |
| Severe disability at home | 75+ | 0.07 | 0.40 | 0.53 | $12,754 | 1.14 | $14,544 |
| Nursing home | 65-74 | 0.05 | 0.38 | 0.57 | $12,176 | 1.16 | $14,129 |
| Nursing home | 75+ | 0.09 | 0.39 | 0.51 | $12,534 | 1.14 | $14,293 |

**Table 4b.** Annual out-of-pocket spending by state, age band and sex (HRS core interviews, 2006 to 2022).

*Annualized from the recall since the last interview; premiums excluded. The share on Medicaid is the weighted share of person-waves reporting Medicaid coverage.*

| State | Age | Sex | n | Mean | p50 | p90 | p99 | On Medicaid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Healthy | 65-74 | female | 2,045 | $1,199 | $531 | $3,024 | $9,087 | 2% |
| Healthy | 65-74 | male | 1,775 | $1,258 | $392 | $2,998 | $13,017 | 4% |
| Healthy | 75+ | female | 948 | $1,184 | $484 | $2,773 | $11,512 | 3% |
| Healthy | 75+ | male | 873 | $1,220 | $432 | $3,109 | $13,731 | 8% |
| Chronic illness | 65-74 | female | 19,714 | $1,903 | $962 | $4,403 | $14,172 | 7% |
| Chronic illness | 65-74 | male | 14,799 | $1,832 | $879 | $4,279 | $14,317 | 5% |
| Chronic illness | 75+ | female | 17,552 | $2,040 | $980 | $4,644 | $15,709 | 7% |
| Chronic illness | 75+ | male | 12,926 | $2,008 | $980 | $4,731 | $15,073 | 5% |
| Disability | 65-74 | female | 2,836 | $2,296 | $1,018 | $5,608 | $16,878 | 21% |
| Disability | 65-74 | male | 1,945 | $2,572 | $963 | $6,822 | $22,581 | 14% |
| Disability | 75+ | female | 4,584 | $2,940 | $1,166 | $6,296 | $28,559 | 13% |
| Disability | 75+ | male | 2,865 | $2,777 | $1,246 | $6,300 | $21,035 | 8% |
| Severe disability at home | 65-74 | female | 1,122 | $2,838 | $874 | $7,256 | $25,816 | 34% |
| Severe disability at home | 65-74 | male | 580 | $2,949 | $662 | $7,006 | $27,436 | 25% |
| Severe disability at home | 75+ | female | 2,399 | $3,632 | $1,160 | $8,141 | $47,266 | 25% |
| Severe disability at home | 75+ | male | 1,170 | $4,042 | $1,381 | $8,723 | $49,987 | 15% |
| Nursing home | 65-74 | female | 235 | $11,268 | $1,361 | $33,675 | $86,653 | 50% |
| Nursing home | 65-74 | male | 151 | $9,106 | $0 | $34,359 | $82,263 | 50% |
| Nursing home | 75+ | female | 1,841 | $19,047 | $4,157 | $56,735 | $157,817 | 40% |
| Nursing home | 75+ | male | 655 | $16,387 | $3,282 | $51,040 | $135,957 | 35% |

**Table 4c.** Out-of-pocket spending with and without Medicaid, by state and age band.

*Weighted, sexes pooled. Medicaid pays most long-term-care costs for those enrolled, which is why the simulation draws from the two distributions separately and moves a life onto Medicaid when it spends down.*

| State | Age | On Medicaid | Mean, not on Medicaid | p99 | Mean, on Medicaid | p99 |
|---|---:|---:|---:|---:|---:|---:|
| Healthy | 65-74 | 2.8% | $1,254 | $10,190 | $300 | $3,186 |
| Healthy | 75+ | 5.4% | $1,230 | $13,154 | $668 | $7,966 |
| Chronic illness | 65-74 | 6.1% | $1,937 | $14,484 | $833 | $10,186 |
| Chronic illness | 75+ | 6.1% | $2,096 | $15,609 | $953 | $11,869 |
| Disability | 65-74 | 17.5% | $2,720 | $20,789 | $1,009 | $15,235 |
| Disability | 75+ | 11.4% | $3,061 | $26,814 | $1,455 | $17,444 |
| Severe disability at home | 65-74 | 30.3% | $3,701 | $27,699 | $986 | $11,483 |
| Severe disability at home | 75+ | 22.1% | $4,502 | $51,424 | $1,136 | $16,946 |
| Nursing home | 65-74 | 50.0% | $16,046 | $102,868 | $4,747 | $50,047 |
| Nursing home | 75+ | 38.4% | $23,588 | $152,487 | $9,916 | $96,944 |

**Table 4d.** Out-of-pocket spending in the last year of life (HRS exit interviews, 2006 to 2022).

*Spending from the last core interview to death, pro-rated to twelve months where that window is longer; includes hospice. Unweighted; age band at death.*

| Group | Age at death | Sex | n | Imputed | Mean | p50 | p90 | p99 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Long-term care at last interview | 65-74 | female | 219 | 31% | $10,761 | $583 | $25,685 | $141,728 |
| Long-term care at last interview | 65-74 | male | 176 | 29% | $10,083 | $442 | $22,600 | $173,599 |
| Long-term care at last interview | 75+ | female | 1,865 | 29% | $17,751 | $1,681 | $58,719 | $171,333 |
| Long-term care at last interview | 75+ | male | 992 | 33% | $16,607 | $2,069 | $51,770 | $181,296 |
| Other | 65-74 | female | 771 | 37% | $6,541 | $1,224 | $16,400 | $85,201 |
| Other | 65-74 | male | 883 | 37% | $6,162 | $1,475 | $14,939 | $81,596 |
| Other | 75+ | female | 2,602 | 38% | $8,378 | $1,971 | $19,099 | $95,708 |
| Other | 75+ | male | 2,457 | 39% | $7,536 | $1,743 | $18,671 | $91,986 |

**Table 4e.** Persistence of out-of-pocket spending.

*Correlation of normal scores of annual out-of-pocket spending (within state, age band and wave) between interviews k years apart, and the fitted permanent-plus-decaying form c + (1 - c) phi^k with c = 0.367 and phi = 0.463.*

| Years apart | Pairs | Correlation | Fitted |
|---|---:|---:|---:|
| 2 | 68,498 | 0.494 | 0.503 |
| 4 | 50,712 | 0.418 | 0.397 |
| 6 | 36,658 | 0.376 | 0.374 |
| 8 | 25,280 | 0.353 | 0.369 |

**Table 5.** Expected lifetime cost from age 65 by sex and health state at 65, present value at 3%.

*100,000 simulated lives per row, calibrated mortality, persistent out-of-pocket draws and Medicaid spend-down. Parameter intervals are the 2.5th and 97.5th percentiles of the exact expected value over 200 draws of the transition parameters from their cluster-robust covariance, with spend-down and persistence off. Premiums are the standard Part B and base Part D premiums in years not on Medicaid.*

| Sex | State at 65 | e65 | Ever LTC | Years LTC | Ever Medicaid | Medicare | low | high | Out of pocket | low | high | OOP median | Premiums |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| male | Healthy | 20.4 | 41.5% | 1.24 | 11.4% | $139,934 | $138,309 | $140,955 | $34,484 | $34,462 | $35,298 | $20,026 | $36,431 |
| male | Chronic illness | 18.3 | 41.5% | 1.29 | 12.7% | $157,383 | $156,187 | $158,379 | $35,727 | $36,006 | $36,755 | $21,183 | $33,041 |
| male | Disability | 15.9 | 51.7% | 1.85 | 29.7% | $156,868 | $155,441 | $158,461 | $32,300 | $33,315 | $34,273 | $17,153 | $25,179 |
| male | Severe disability at home | 12.9 | 100.0% | 4.25 | 56.3% | $150,667 | $148,443 | $152,816 | $26,780 | $30,000 | $31,484 | $11,010 | $12,810 |
| male | Nursing home | 8.4 | 100.0% | 4.55 | 68.8% | $125,828 | $121,617 | $130,959 | $40,213 | $39,089 | $44,629 | $10,339 | $6,937 |
| male | Population mix | 18.2 | 44.2% | 1.42 | 15.3% | $154,423 | $153,300 | $155,326 | $35,329 | $35,459 | $36,212 | $20,520 | $32,195 |
| female | Healthy | 22.8 | 54.9% | 1.98 | 11.0% | $153,433 | $152,304 | $154,307 | $43,594 | $44,343 | $45,536 | $25,541 | $40,554 |
| female | Chronic illness | 20.8 | 55.8% | 2.17 | 20.8% | $174,647 | $173,753 | $175,586 | $45,109 | $46,207 | $47,352 | $26,248 | $35,075 |
| female | Disability | 18.8 | 63.6% | 2.87 | 45.1% | $179,473 | $178,326 | $180,886 | $38,410 | $40,969 | $42,131 | $20,278 | $24,983 |
| female | Severe disability at home | 16.0 | 100.0% | 5.57 | 69.0% | $173,373 | $171,347 | $175,741 | $31,950 | $37,822 | $39,540 | $12,919 | $11,217 |
| female | Nursing home | 10.9 | 100.0% | 6.20 | 82.0% | $149,109 | $144,158 | $155,046 | $56,679 | $57,072 | $66,189 | $18,668 | $5,442 |
| female | Population mix | 20.7 | 57.9% | 2.33 | 23.2% | $171,804 | $171,065 | $172,846 | $43,666 | $45,267 | $46,346 | $25,125 | $33,977 |

**Table 5b.** Lifetime cost, Medicaid and tail risk by household income tertile at 65.

*Tertiles of household income within interview wave at ages 64 to 66. Each simulated life keeps its income, non-housing assets and Medicaid status at 65. The transition model has no income term (Section 6.1 reports the extension that adds one).*

| Sex | Income | Median income | Median assets | Medicaid at 65 | LTC at 65 | e65 | Ever LTC | Ever Medicaid | Medicare | Out of pocket | CVaR95 | Premiums |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| male | low | $26,128 | $7,970 | 18.6% | 6.8% | 17.4 | 48.5% | 37.5% | $170,053 | $29,154 | $167,897 | $26,013 |
| male | middle | $71,775 | $91,555 | 2.7% | 2.3% | 18.1 | 43.3% | 10.7% | $147,271 | $34,716 | $186,184 | $33,359 |
| male | high | $166,099 | $429,921 | 0.8% | 0.8% | 18.9 | 41.8% | 3.5% | $149,496 | $39,257 | $197,756 | $35,602 |
| female | low | $23,979 | $5,635 | 21.4% | 8.0% | 20.0 | 61.8% | 45.2% | $188,021 | $36,436 | $214,229 | $27,452 |
| female | middle | $69,071 | $110,388 | 2.6% | 2.2% | 20.9 | 56.6% | 13.9% | $162,097 | $45,082 | $236,242 | $37,101 |
| female | high | $163,114 | $492,086 | 0.8% | 0.8% | 21.6 | 55.5% | 5.2% | $162,782 | $52,254 | $266,081 | $39,357 |

**Table 5c.** The simulation against the exact recursion, with spend-down and persistence off.

*Population mix. The difference is within about two Monte Carlo standard errors.*

| Sex | Medicare, simulated | Medicare, exact | OOP, simulated | OOP, exact | MC SE |
|---|---:|---:|---:|---:|---:|
| male | $154,452 | $154,451 | $35,885 | $35,830 | $92 |
| female | $171,896 | $171,992 | $45,839 | $45,793 | $125 |

**Table 6.** The tail of lifetime out-of-pocket cost.

*VaR is the quantile of the present value of lifetime out-of-pocket cost; CVaR the mean beyond it, with its Monte Carlo standard error from 200 bootstrap resamples of the simulated lives. The last columns describe the lives in the tail.*

| Sex | State at 65 | Level | VaR | CVaR | MC SE | CVaR / mean | LTC in tail | LTC overall | Years LTC in tail | Medicaid in tail | End-of-life share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| male | Healthy | 95% | $115,872 | $183,553 | $1,487 | 5.3 | 69.9% | 41.5% | 2.8 | 27.3% | 11.8% |
| male | Healthy | 99% | $224,495 | $304,418 | $3,651 | 8.8 | 78.4% | 41.5% | 3.7 | 36.2% | 12.2% |
| male | Chronic illness | 95% | $118,213 | $186,511 | $1,525 | 5.2 | 70.2% | 41.5% | 2.9 | 31.3% | 12.1% |
| male | Chronic illness | 99% | $225,133 | $312,051 | $4,175 | 8.7 | 79.3% | 41.5% | 3.7 | 42.5% | 12.7% |
| male | Disability | 95% | $115,461 | $184,247 | $1,520 | 5.7 | 75.8% | 51.7% | 3.6 | 48.4% | 14.9% |
| male | Disability | 99% | $222,364 | $309,538 | $4,103 | 9.6 | 84.0% | 51.7% | 4.6 | 55.5% | 13.7% |
| male | Severe disability at home | 95% | $106,488 | $178,073 | $1,420 | 6.6 | 100.0% | 100.0% | 6.1 | 70.4% | 21.0% |
| male | Severe disability at home | 99% | $213,000 | $300,903 | $4,240 | 11.2 | 100.0% | 100.0% | 7.2 | 69.1% | 14.1% |
| male | Nursing home | 95% | $178,682 | $292,873 | $2,300 | 7.3 | 100.0% | 100.0% | 7.5 | 99.0% | 7.7% |
| male | Nursing home | 99% | $359,430 | $504,582 | $6,429 | 12.5 | 100.0% | 100.0% | 8.6 | 99.9% | 5.9% |
| male | Population mix | 95% | $119,688 | $188,368 | $1,433 | 5.3 | 71.8% | 44.2% | 3.1 | 33.9% | 12.5% |
| male | Population mix | 99% | $227,712 | $311,744 | $4,359 | 8.8 | 79.4% | 44.2% | 4.1 | 43.5% | 12.4% |
| female | Healthy | 95% | $144,462 | $229,407 | $1,766 | 5.3 | 86.3% | 54.9% | 4.6 | 32.4% | 7.4% |
| female | Healthy | 99% | $273,921 | $390,944 | $5,926 | 9.0 | 89.6% | 54.9% | 5.9 | 42.9% | 7.6% |
| female | Chronic illness | 95% | $149,568 | $240,625 | $2,063 | 5.3 | 85.9% | 55.8% | 4.8 | 42.4% | 7.6% |
| female | Chronic illness | 99% | $288,893 | $413,081 | $6,328 | 9.2 | 90.5% | 55.8% | 6.1 | 55.4% | 6.8% |
| female | Disability | 95% | $135,932 | $223,173 | $1,972 | 5.8 | 87.9% | 63.6% | 5.5 | 67.6% | 11.4% |
| female | Disability | 99% | $268,673 | $388,617 | $5,435 | 10.1 | 91.2% | 63.6% | 6.8 | 72.3% | 8.4% |
| female | Severe disability at home | 95% | $128,221 | $217,877 | $1,924 | 6.8 | 100.0% | 100.0% | 8.7 | 73.7% | 14.4% |
| female | Severe disability at home | 99% | $268,453 | $384,702 | $5,119 | 12.0 | 100.0% | 100.0% | 10.6 | 79.8% | 8.6% |
| female | Nursing home | 95% | $243,217 | $380,546 | $2,863 | 6.7 | 100.0% | 100.0% | 10.7 | 95.9% | 5.4% |
| female | Nursing home | 99% | $458,782 | $616,895 | $6,702 | 10.9 | 100.0% | 100.0% | 13.1 | 97.7% | 5.0% |
| female | Population mix | 95% | $147,062 | $235,495 | $1,925 | 5.4 | 85.7% | 57.9% | 5.0 | 44.5% | 8.3% |
| female | Population mix | 99% | $281,920 | $407,630 | $5,822 | 9.3 | 88.8% | 57.9% | 6.3 | 54.7% | 7.5% |

**Table 7.** Financing scenarios: lifetime out-of-pocket cost for a cohort turning 65 in 2026, population mix.

*Hospital Insurance pays 35.1% of Medicare spending per beneficiary (Trustees Table V.D1, 2024). S1: from 2033 the payable share follows the Trustees' path (89% in 2033, 85% in 2050, 93% in 2100) and the stated share of the shortfall falls on beneficiaries not on Medicaid. S1b: the same with the community inpatient and home-health share the Cost Supplement measures. S2: the whole cohort shortfall falls on person-years in long-term care. S3: S1 at 50% with real cost growth. Common random numbers across scenarios.*

| Sex | Scenario | Mean | CVaR95 | CVaR99 | Change in mean | Change in CVaR95 | Ever Medicaid | Change, pts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| male | S0 baseline | $34,950 | $187,136 | $313,260 | $0 | $0 | 15.3% | 0.0 |
| male | S1 shortfall from 2033, shift 0% | $34,950 | $187,136 | $313,260 | $0 | $0 | 15.3% | 0.0 |
| male | S1 shortfall from 2033, shift 25% | $35,951 | $188,347 | $314,406 | $1,002 | $1,210 | 15.4% | 0.1 |
| male | S1 shortfall from 2033, shift 50% | $36,952 | $189,564 | $315,564 | $2,003 | $2,428 | 15.5% | 0.1 |
| male | S1 shortfall from 2033, shift 100% | $38,953 | $192,005 | $317,900 | $4,003 | $4,869 | 15.6% | 0.3 |
| male | S1b community Part A share 26%, shift 50% | $36,430 | $188,929 | $314,959 | $1,481 | $1,793 | 15.4% | 0.1 |
| male | S1b community Part A share 26%, shift 100% | $37,910 | $190,733 | $316,679 | $2,961 | $3,597 | 15.5% | 0.2 |
| male | S2 shortfall on long-term-care years | $37,030 | $191,849 | $319,268 | $2,081 | $4,713 | 16.1% | 0.7 |
| male | S3 real growth 1.7% and shift 50% | $45,301 | $239,347 | $399,180 | $10,352 | $52,211 | 16.4% | 1.1 |
| female | S0 baseline | $43,805 | $239,010 | $416,921 | $0 | $0 | 23.4% | 0.0 |
| female | S1 shortfall from 2033, shift 0% | $43,805 | $239,010 | $416,921 | $0 | $0 | 23.4% | 0.0 |
| female | S1 shortfall from 2033, shift 25% | $44,909 | $240,284 | $418,079 | $1,104 | $1,274 | 23.5% | 0.1 |
| female | S1 shortfall from 2033, shift 50% | $46,013 | $241,542 | $419,231 | $2,208 | $2,531 | 23.6% | 0.2 |
| female | S1 shortfall from 2033, shift 100% | $48,219 | $244,148 | $421,681 | $4,414 | $5,138 | 23.9% | 0.4 |
| female | S1b community Part A share 26%, shift 50% | $45,439 | $240,905 | $418,658 | $1,634 | $1,894 | 23.6% | 0.2 |
| female | S1b community Part A share 26%, shift 100% | $47,070 | $242,788 | $420,386 | $3,265 | $3,778 | 23.7% | 0.3 |
| female | S2 shortfall on long-term-care years | $46,587 | $245,104 | $424,310 | $2,782 | $6,093 | 24.5% | 1.0 |
| female | S3 real growth 1.7% and shift 50% | $58,035 | $316,847 | $553,382 | $14,229 | $77,837 | 25.3% | 1.9 |

**Table 7b.** Medicaid spend-down and scenario effects by household income tertile at 65.

*Households meet out-of-pocket costs from income up to 10% of income and from non-housing assets beyond that; a life needing long-term care whose assets fall below $2,000 goes onto Medicaid. Spend-down counts lives that reach Medicaid after 65.*

| Sex | Income | Scenario | Median assets | Medicaid at 65 | Spend down | Ever Medicaid | Median age at spend-down | Mean OOP | CVaR95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| male | low | S0 baseline | $12,055 | 20.8% | 16.4% | 37.2% | 82 | $29,032 | $164,971 |
| male | low | S1 shortfall from 2033, shift 50% | $12,055 | 20.8% | 16.7% | 37.5% | 82 | $30,755 | $167,036 |
| male | low | S2 shortfall on long-term-care years | $12,055 | 20.8% | 17.9% | 38.7% | 81 | $30,420 | $167,519 |
| male | middle | S0 baseline | $113,937 | 2.9% | 7.7% | 10.6% | 83 | $34,621 | $182,200 |
| male | middle | S1 shortfall from 2033, shift 50% | $113,937 | 2.9% | 7.8% | 10.7% | 83 | $36,636 | $184,563 |
| male | middle | S2 shortfall on long-term-care years | $113,937 | 2.9% | 8.4% | 11.3% | 83 | $36,895 | $186,739 |
| male | high | S0 baseline | $509,219 | 0.9% | 2.7% | 3.6% | 84 | $39,304 | $195,354 |
| male | high | S1 shortfall from 2033, shift 50% | $509,219 | 0.9% | 2.7% | 3.6% | 84 | $41,493 | $198,034 |
| male | high | S2 shortfall on long-term-care years | $509,219 | 0.9% | 2.8% | 3.7% | 84 | $41,675 | $200,894 |
| female | low | S0 baseline | $10,064 | 23.7% | 21.5% | 45.3% | 83 | $36,787 | $217,104 |
| female | low | S1 shortfall from 2033, shift 50% | $10,064 | 23.7% | 21.9% | 45.6% | 83 | $38,656 | $219,215 |
| female | low | S2 shortfall on long-term-care years | $10,064 | 23.7% | 23.4% | 47.2% | 82 | $38,720 | $220,585 |
| female | middle | S0 baseline | $143,658 | 2.8% | 11.0% | 13.8% | 85 | $44,703 | $229,138 |
| female | middle | S1 shortfall from 2033, shift 50% | $143,658 | 2.8% | 11.2% | 13.9% | 85 | $47,026 | $231,648 |
| female | middle | S2 shortfall on long-term-care years | $143,658 | 2.8% | 11.9% | 14.6% | 85 | $47,940 | $235,463 |
| female | high | S0 baseline | $562,530 | 0.9% | 4.4% | 5.3% | 86 | $51,873 | $261,897 |
| female | high | S1 shortfall from 2033, shift 50% | $562,530 | 0.9% | 4.4% | 5.4% | 86 | $54,384 | $264,852 |
| female | high | S2 shortfall on long-term-care years | $562,530 | 0.9% | 4.6% | 5.5% | 86 | $55,323 | $270,505 |

**Table 8.** The model's out-of-pocket spending against published estimates.

*Published values converted to 2024 dollars with the CPI-U. Bases differ, as the basis column states; model values are per person, include Part B and Part D premiums only where the source's measure does, and exclude Medicaid payments throughout.*

| Source | Quantity | Basis | Published | 2024 dollars | Model, men | Model, women |
|---|---:|---:|---:|---:|---:|---:|
| Jones et al. (2018) | Lifetime medical spending from 70, mean | per household, includes Medicaid payments, PV at 3% | 122,000 | 161,662 | 33,235 | 42,298 |
| Jones et al. (2018) | Lifetime medical spending from 70, 95th percentile | per household, includes Medicaid payments, PV at 3% | 300,000 | 397,530 | 116,640 | 149,384 |
| Kelley et al. (2013) | Out-of-pocket spending in the last five years of life, mean | per individual, includes insurance premiums | 38,688 | 56,368 | 35,182 | 42,826 |
| Kelley et al. (2013) | Out-of-pocket spending in the last five years of life, median | per individual, includes insurance premiums | 22,885 | 33,343 | 21,013 | 22,400 |
| Marshall et al. (2011) | Out-of-pocket spending in the last year of life, mean | per individual, HRS 1998-2006; the source's dollar year is not stated | 11,618 | 16,927 | 10,386 | 12,568 |
| Marshall et al. (2011) | Out-of-pocket spending in the last year of life, 95th percentile | per individual, HRS 1998-2006; the source's dollar year is not stated | 49,907 | 72,714 | 53,447 | 67,837 |
| Hurd et al. (2017) | Ever a nursing-home stay | percent, from ages 57-61; the model starts at 65 | 56 | 56 | 19 | 30 |
| Hurd et al. (2017) | Lifetime nursing-home out-of-pocket spending, mean | per person from 57, PV at 3%; zero for most | 7,300 | 9,673 | 4,636 | 9,864 |

**Table 9.** Robustness: each row changes one decision.

*Population mix at 65; 40,000 lives per sex with common random numbers. Refits use the sex-only covariate set and rebuild the entry sample, state costs and calibration from the variant panel; compare them with the sex-only row. The CVaR95 Monte Carlo standard error is about the last column's size.*

| Variant | e65 M | e65 F | LTC M | LTC F | Medicaid M | Medicaid F | Medicare M | Medicare F | OOP M | OOP F | CVaR95 M | CVaR95 F | MC SE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $154,778 | $171,775 | $35,058 | $43,640 | $185,746 | $234,519 | $2,153 |
| discount 2% | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $173,027 | $193,908 | $39,340 | $49,831 | $213,025 | $274,357 | $2,498 |
| discount 4% | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $139,456 | $153,404 | $31,481 | $38,559 | $163,868 | $203,049 | $1,890 |
| Trustees real growth 1.7% | 18.3 | 20.7 | 44% | 58% | 16% | 25% | $188,416 | $212,763 | $42,862 | $54,882 | $235,533 | $307,206 | $2,776 |
| D, L and N Medicare +25% | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $166,176 | $186,554 | $35,058 | $43,640 | $185,746 | $234,519 | $2,153 |
| functional cost gradient | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $159,704 | $183,189 | $35,058 | $43,640 | $185,746 | $234,519 | $2,153 |
| Medicare not scaled to MCBS | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $134,608 | $149,490 | $35,058 | $43,640 | $185,746 | $234,519 | $2,153 |
| Medicare from FFS only | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $149,507 | $166,629 | $35,058 | $43,640 | $185,746 | $234,519 | $2,153 |
| Medicare at Trustees level (x1.59) | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $246,855 | $273,965 | $35,058 | $43,640 | $185,746 | $234,519 | $2,153 |
| no end-of-life concentration | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $158,661 | $180,732 | $35,058 | $43,640 | $185,746 | $234,519 | $2,153 |
| mortality not calibrated | 17.6 | 20.4 | 41% | 57% | 15% | 23% | $150,734 | $169,616 | $33,804 | $43,025 | $179,906 | $233,112 | $2,232 |
| calibration on H and C only | 18.3 | 20.8 | 44% | 58% | 15% | 23% | $154,815 | $172,180 | $34,974 | $43,816 | $184,598 | $235,877 | $2,024 |
| mortality improvement 1% a year | 19.2 | 21.8 | 49% | 63% | 16% | 25% | $159,268 | $177,012 | $37,144 | $47,117 | $199,785 | $257,055 | $2,352 |
| independent out-of-pocket draws | 18.2 | 20.7 | 43% | 58% | 16% | 25% | $154,072 | $172,104 | $35,067 | $44,130 | $119,229 | $158,542 | $1,197 |
| no end-of-life step | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $154,778 | $171,775 | $31,755 | $40,706 | $167,370 | $219,115 | $1,939 |
| end of life not by state | 18.3 | 20.7 | 44% | 58% | 15% | 23% | $154,778 | $171,775 | $34,660 | $43,256 | $181,678 | $231,138 | $2,074 |
| out-of-pocket from all waves | 18.3 | 20.7 | 44% | 58% | 15% | 24% | $155,530 | $172,574 | $37,233 | $47,470 | $206,564 | $265,687 | $2,430 |
| no spend-down | 18.3 | 20.7 | 44% | 58% | 6% | 9% | $154,778 | $171,775 | $35,815 | $45,589 | $193,566 | $251,851 | $2,386 |
| income meets 0% of out-of-pocket | 18.3 | 20.7 | 44% | 58% | 19% | 29% | $154,778 | $171,775 | $34,762 | $43,021 | $183,532 | $231,360 | $2,133 |
| income meets 20% of out-of-pocket | 18.3 | 20.7 | 44% | 58% | 14% | 22% | $154,778 | $171,775 | $35,141 | $43,829 | $186,553 | $235,836 | $2,161 |
| Medicaid asset limit $10,000 | 18.3 | 20.7 | 44% | 58% | 17% | 26% | $154,778 | $171,775 | $34,950 | $43,427 | $185,384 | $234,139 | $2,144 |
| sex-only model | 18.3 | 20.8 | 47% | 61% | 15% | 24% | $155,574 | $172,943 | $35,760 | $45,178 | $191,226 | $246,060 | $2,486 |


# Appendix tables


**Table A2.** Observations by state at the start (rows) and at the end (columns).

| From | Alive, state unknown | Healthy | Chronic illness | Disability | Severe disability at home | Nursing home | Dead |
|---|---:|---:|---:|---:|---:|---:|---:|
| Healthy | 1,535 | 24,442 | 5,796 | 766 | 122 | 108 | 424 |
| Chronic illness | 5,761 | 0 | 119,456 | 11,680 | 2,149 | 1,144 | 7,425 |
| Disability | 844 | 331 | 8,520 | 9,118 | 3,163 | 709 | 3,390 |
| Severe disability at home | 335 | 20 | 817 | 2,136 | 4,023 | 496 | 2,608 |
| Nursing home | 73 | 7 | 130 | 108 | 132 | 1,885 | 2,313 |

**Table A3.** One-year transition probabilities from the fitted model, reference covariates, before calibration.

| Sex | Age | From | Healthy | Chronic illness | Disability | Severe disability at home | Nursing home | Dead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| male | 65 | Healthy | 0.875 | 0.109 | 0.010 | 0.001 | 0.000 | 0.005 |
| male | 65 | Chronic illness | 0.000 | 0.938 | 0.042 | 0.003 | 0.001 | 0.016 |
| male | 65 | Disability | 0.006 | 0.254 | 0.599 | 0.086 | 0.004 | 0.051 |
| male | 65 | Severe disability at home | 0.001 | 0.043 | 0.220 | 0.609 | 0.026 | 0.100 |
| male | 65 | Nursing home | 0.000 | 0.011 | 0.059 | 0.026 | 0.717 | 0.186 |
| male | 75 | Healthy | 0.848 | 0.119 | 0.019 | 0.001 | 0.000 | 0.013 |
| male | 75 | Chronic illness | 0.000 | 0.904 | 0.056 | 0.004 | 0.004 | 0.031 |
| male | 75 | Disability | 0.004 | 0.219 | 0.580 | 0.095 | 0.013 | 0.088 |
| male | 75 | Severe disability at home | 0.001 | 0.028 | 0.159 | 0.586 | 0.052 | 0.174 |
| male | 75 | Nursing home | 0.000 | 0.006 | 0.038 | 0.014 | 0.671 | 0.270 |
| male | 85 | Healthy | 0.785 | 0.114 | 0.058 | 0.006 | 0.003 | 0.034 |
| male | 85 | Chronic illness | 0.000 | 0.806 | 0.096 | 0.010 | 0.018 | 0.070 |
| male | 85 | Disability | 0.003 | 0.165 | 0.532 | 0.121 | 0.047 | 0.132 |
| male | 85 | Severe disability at home | 0.000 | 0.015 | 0.103 | 0.528 | 0.077 | 0.276 |
| male | 85 | Nursing home | 0.000 | 0.004 | 0.027 | 0.009 | 0.610 | 0.350 |
| female | 65 | Healthy | 0.878 | 0.109 | 0.010 | 0.001 | 0.000 | 0.002 |
| female | 65 | Chronic illness | 0.000 | 0.941 | 0.046 | 0.003 | 0.001 | 0.009 |
| female | 65 | Disability | 0.004 | 0.261 | 0.612 | 0.084 | 0.006 | 0.032 |
| female | 65 | Severe disability at home | 0.001 | 0.042 | 0.210 | 0.653 | 0.027 | 0.068 |
| female | 65 | Nursing home | 0.000 | 0.009 | 0.048 | 0.037 | 0.776 | 0.130 |
| female | 75 | Healthy | 0.856 | 0.118 | 0.018 | 0.001 | 0.000 | 0.006 |
| female | 75 | Chronic illness | 0.000 | 0.911 | 0.062 | 0.005 | 0.004 | 0.018 |
| female | 75 | Disability | 0.003 | 0.227 | 0.599 | 0.094 | 0.020 | 0.057 |
| female | 75 | Severe disability at home | 0.000 | 0.027 | 0.154 | 0.644 | 0.055 | 0.119 |
| female | 75 | Nursing home | 0.000 | 0.005 | 0.031 | 0.020 | 0.753 | 0.191 |
| female | 85 | Healthy | 0.804 | 0.115 | 0.056 | 0.006 | 0.004 | 0.016 |
| female | 85 | Chronic illness | 0.000 | 0.822 | 0.105 | 0.011 | 0.020 | 0.041 |
| female | 85 | Disability | 0.002 | 0.171 | 0.540 | 0.121 | 0.077 | 0.089 |
| female | 85 | Severe disability at home | 0.000 | 0.015 | 0.101 | 0.605 | 0.086 | 0.193 |
| female | 85 | Nursing home | 0.000 | 0.003 | 0.022 | 0.012 | 0.711 | 0.251 |

**Table A4.** State prevalence by age band: the weighted HRS cross-section (2006 to 2022) against the calibrated model (percent of survivors).

| Sex | Age | H HRS | H model | C HRS | C model | D HRS | D model | L HRS | L model | N HRS | N model |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| female | 65-69 | 10.9% | 11.8% | 75.2% | 74.1% | 9.5% | 9.8% | 3.6% | 3.6% | 0.8% | 0.7% |
| female | 70-74 | 6.9% | 6.8% | 77.7% | 77.1% | 10.2% | 10.9% | 3.8% | 3.9% | 1.3% | 1.3% |
| female | 75-79 | 5.0% | 4.0% | 73.8% | 74.8% | 13.5% | 13.5% | 5.5% | 5.3% | 2.2% | 2.5% |
| female | 80-84 | 3.6% | 2.4% | 67.8% | 68.4% | 16.2% | 16.5% | 7.4% | 7.5% | 5.0% | 5.1% |
| female | 85-89 | 2.7% | 1.6% | 58.4% | 59.1% | 19.2% | 19.0% | 10.3% | 10.2% | 9.4% | 10.0% |
| female | 90-99 | 1.9% | 1.2% | 41.9% | 43.8% | 23.4% | 21.7% | 17.4% | 15.6% | 15.4% | 17.7% |
| male | 65-69 | 11.5% | 12.1% | 76.7% | 75.6% | 8.6% | 9.0% | 2.5% | 2.7% | 0.6% | 0.6% |
| male | 70-74 | 7.0% | 7.2% | 79.2% | 79.2% | 10.1% | 9.7% | 2.6% | 3.1% | 1.0% | 0.9% |
| male | 75-79 | 4.6% | 4.3% | 78.1% | 77.6% | 11.9% | 12.2% | 3.5% | 4.2% | 1.8% | 1.7% |
| male | 80-84 | 4.0% | 2.8% | 71.3% | 72.2% | 16.2% | 15.4% | 5.6% | 6.1% | 2.9% | 3.5% |
| male | 85-89 | 4.8% | 2.0% | 63.9% | 64.1% | 17.7% | 18.6% | 8.5% | 8.5% | 5.2% | 6.8% |
| male | 90-99 | 4.8% | 1.7% | 52.7% | 49.9% | 20.2% | 22.8% | 12.8% | 13.3% | 9.6% | 12.2% |

**Table A5.** Medicare per person-year and Medicaid in long-term care: model against MCBS, the Trustees and HRS.

*The MCBS ratio is a consistency check (the level is scaled to it); the Trustees' figure covers all beneficiaries including the disabled under 65 and all services.*

| Age | Before scaling | Model | MCBS | Model / MCBS | Trustees 2024 | Model / Trustees |
|---|---:|---:|---:|---:|---:|---:|
| 65-74 | $8,548 | $9,920 | $9,920 | 1.000 | $17,837 | 0.556 |
| 75+ | $10,916 | $12,448 | $12,343 | 1.009 | $17,837 | 0.698 |

| Sex | LTC person-years on Medicaid, model | HRS | Ever Medicaid, model | Medicaid at 65 |
|---|---:|---:|---:|---:|
| male | 23.5% | 30.5% | 15.3% | 7.1% |
| female | 31.0% | 30.5% | 23.2% | 10.4% |

**Table A6.** Life expectancy at 65 by covariate profile and health state at 65, fitted model before calibration.

| Sex | Any college | Nonwhite or Hispanic | Healthy | Chronic illness | Disability | Severe disability at home | Nursing home |
|---|---:|---:|---:|---:|---:|---:|---:|
| female | no | no | 21.2 | 19.3 | 17.1 | 14.1 | 8.7 |
| female | no | yes | 20.8 | 19.0 | 17.5 | 15.5 | 8.9 |
| female | yes | no | 23.6 | 21.7 | 19.6 | 15.5 | 11.4 |
| female | yes | yes | 23.2 | 21.4 | 19.7 | 16.8 | 11.5 |
| male | no | no | 18.3 | 16.3 | 13.9 | 11.0 | 6.4 |
| male | no | yes | 17.6 | 16.0 | 14.2 | 12.2 | 6.5 |
| male | yes | no | 20.8 | 18.6 | 16.3 | 12.2 | 8.8 |
| male | yes | yes | 20.1 | 18.1 | 16.3 | 13.3 | 8.6 |

**Table A7.** MCBS Cost Supplement: annual spending per beneficiary by payer, 2019 and 2021 to 2023 pooled.

*Medicare includes fee-for-service and Medicare Advantage payments. The All row includes beneficiaries under 65. Standard errors from Fay-adjusted BRR with 100 replicates.*

| Cell | n | In MA | Medicare | SE | Medicare, FFS only | Out of pocket | All payers | IP + HH / Medicare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| All | 29,144 | 44.2% | $11,802 | $278 | $11,135 | $2,717 | $17,406 | 25.9% |
| 65-74 | 10,346 | 42.4% | $9,920 | $357 | $9,095 | $2,510 | $14,974 | 24.4% |
| 75 and over | 14,033 | 46.3% | $12,343 | $349 | $12,463 | $3,228 | $18,330 | 27.7% |
| 65-74, 0-1 chronic conditions | 2,239 | 34.9% | $4,418 | $493 | $3,275 | $1,624 | $7,264 | 22.0% |
| 65-74, 2-3 chronic conditions | 4,282 | 42.2% | $8,217 | $445 | $8,153 | $2,389 | $12,909 | 25.4% |
| 65-74, 4+ chronic conditions | 3,824 | 47.6% | $15,499 | $720 | $15,026 | $3,229 | $22,414 | 24.2% |
| 75 and over, 0-1 chronic conditions | 1,791 | 43.9% | $5,976 | $405 | $5,939 | $2,445 | $9,718 | 27.1% |
| 75 and over, 2-3 chronic conditions | 5,402 | 44.9% | $9,648 | $402 | $9,702 | $2,868 | $14,575 | 25.2% |
| 75 and over, 4+ chronic conditions | 6,840 | 48.0% | $15,930 | $542 | $16,391 | $3,690 | $23,267 | 28.8% |
| 65+, 0-1 chronic conditions, Income $25,000 or less | 824 | 40.2% | $5,516 | $835 | $5,595 | $818 | $7,137 | 17.8% |
| 65+, 0-1 chronic conditions, Income over $25,000 | 3,206 | 36.6% | $4,685 | $399 | $3,565 | $2,067 | $8,090 | 25.2% |
| 65+, 2-3 chronic conditions, Income $25,000 or less | 2,239 | 58.8% | $9,743 | $998 | $10,562 | $1,336 | $12,591 | 22.1% |
| 65+, 2-3 chronic conditions, Income over $25,000 | 7,445 | 39.4% | $8,520 | $372 | $8,419 | $2,874 | $13,776 | 26.2% |
| 65+, 4+ chronic conditions, Income $25,000 or less | 3,377 | 61.8% | $16,001 | $702 | $17,169 | $1,872 | $21,208 | 25.8% |
| 65+, 4+ chronic conditions, Income over $25,000 | 7,287 | 42.2% | $15,594 | $626 | $15,302 | $4,088 | $23,482 | 26.8% |

**Table A8.** 2023 US period life table, selected ages (NCHS).

| Age | qx, male | ex, male | qx, female | ex, female |
|---|---:|---:|---:|---:|
| 65 | 0.01620 | 18.19 | 0.01013 | 20.71 |
| 70 | 0.02264 | 14.74 | 0.01476 | 16.82 |
| 75 | 0.03352 | 11.48 | 0.02371 | 13.15 |
| 80 | 0.05416 | 8.53 | 0.04049 | 9.85 |
| 85 | 0.09216 | 6.06 | 0.07093 | 7.04 |
| 90 | 0.15990 | 4.14 | 0.12854 | 4.82 |
| 95 | 0.25628 | 2.83 | 0.21598 | 3.26 |
| 100 | 1.00000 | 2.01 | 1.00000 | 2.26 |
