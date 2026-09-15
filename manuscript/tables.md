# Tables

*Generated from `output/tables/*.csv` by `python/make_tables.py`. Dollar amounts are 2024 dollars; present values are discounted at 3% a year to age 65. HRS estimates use the respondent analysis weight, or the nursing-home resident weight for residents; MCBS estimates use the Cost Supplement weight with Fay-adjusted balanced repeated replication.*


**Table 1.** The HRS panel, waves 4 to 16 (1998 to 2022), respondents aged 50 and over.

| Quantity | Value |
|---|---:|
| Respondents with at least one classified interview | 40,354 |
| Person-interviews with a classified state | 237,944 |
| Intervals between interviews | 197,590 |
| Deaths with an exact date | 15,962 |
| Mean interval length, years | 2.0 |
| Waves | 4-16 (1998-2022) |
| Weighted share of person-interviews in Healthy, % | 16.5 |
| Weighted share of person-interviews in Chronic illness, % | 68.6 |
| Weighted share of person-interviews in Disability, % | 10.8 |
| Weighted share of person-interviews in Long-term-care need, % | 4.1 |

**Table 2.** Transition intensities among health states.

*Log-linear intensities fitted by maximum likelihood to interval-censored transitions. Reference: male, no college, non-Hispanic white, age 65. Hazard ratios with 95% intervals from the inverse observed information. Likelihood-ratio test of the education and race-ethnicity terms: 1,512.4 on 24 degrees of freedom.*

| Transition | Term | Estimate | SE | Hazard ratio | 95% low | 95% high |
|---|---:|---:|---:|---:|---:|---:|
| H to C | log rate at 65 | -2.178 | 0.029 |  |  |  |
| H to C | age, per 10 years | 0.123 | 0.017 | 1.13 | 1.09 | 1.17 |
| H to C | female | -0.006 | 0.028 | 0.99 | 0.94 | 1.05 |
| H to C | any college | -0.127 | 0.029 | 0.88 | 0.83 | 0.93 |
| H to C | nonwhite or Hispanic | 0.029 | 0.031 | 1.03 | 0.97 | 1.09 |
| H to D | log rate at 65 | -4.217 | 0.109 |  |  |  |
| H to D | age, per 10 years | 0.758 | 0.049 | 2.13 | 1.94 | 2.35 |
| H to D | female | -0.098 | 0.098 | 0.91 | 0.75 | 1.10 |
| H to D | any college | -0.246 | 0.100 | 0.78 | 0.64 | 0.95 |
| H to D | nonwhite or Hispanic | 0.513 | 0.102 | 1.67 | 1.37 | 2.04 |
| H to X | log rate at 65 | -5.416 | 0.204 |  |  |  |
| H to X | age, per 10 years | 0.853 | 0.103 | 2.35 | 1.92 | 2.87 |
| H to X | female | -0.858 | 0.230 | 0.42 | 0.27 | 0.67 |
| H to X | any college | -0.781 | 0.239 | 0.46 | 0.29 | 0.73 |
| H to X | nonwhite or Hispanic | 0.332 | 0.224 | 1.39 | 0.90 | 2.16 |
| C to D | log rate at 65 | -2.900 | 0.022 |  |  |  |
| C to D | age, per 10 years | 0.504 | 0.011 | 1.65 | 1.62 | 1.69 |
| C to D | female | 0.112 | 0.020 | 1.12 | 1.08 | 1.16 |
| C to D | any college | -0.291 | 0.020 | 0.75 | 0.72 | 0.78 |
| C to D | nonwhite or Hispanic | 0.295 | 0.021 | 1.34 | 1.29 | 1.40 |
| C to L | log rate at 65 | -6.109 | 0.173 |  |  |  |
| C to L | age, per 10 years | -1.803 | 0.143 | 0.16 | 0.12 | 0.22 |
| C to L | female | -0.228 | 0.121 | 0.80 | 0.63 | 1.01 |
| C to L | any college | -0.907 | 0.134 | 0.40 | 0.31 | 0.53 |
| C to L | nonwhite or Hispanic | 0.854 | 0.130 | 2.35 | 1.82 | 3.03 |
| C to X | log rate at 65 | -4.149 | 0.038 |  |  |  |
| C to X | age, per 10 years | 0.730 | 0.019 | 2.07 | 2.00 | 2.15 |
| C to X | female | -0.563 | 0.036 | 0.57 | 0.53 | 0.61 |
| C to X | any college | -0.222 | 0.036 | 0.80 | 0.75 | 0.86 |
| C to X | nonwhite or Hispanic | 0.104 | 0.041 | 1.11 | 1.02 | 1.20 |
| D to H | log rate at 65 | -4.573 | 0.105 |  |  |  |
| D to H | age, per 10 years | -0.451 | 0.055 | 0.64 | 0.57 | 0.71 |
| D to H | female | -0.367 | 0.106 | 0.69 | 0.56 | 0.85 |
| D to H | any college | 0.224 | 0.109 | 1.25 | 1.01 | 1.55 |
| D to H | nonwhite or Hispanic | 0.187 | 0.110 | 1.21 | 0.97 | 1.50 |
| D to C | log rate at 65 | -1.126 | 0.023 |  |  |  |
| D to C | age, per 10 years | -0.086 | 0.011 | 0.92 | 0.90 | 0.94 |
| D to C | female | 0.018 | 0.023 | 1.02 | 0.97 | 1.07 |
| D to C | any college | 0.079 | 0.024 | 1.08 | 1.03 | 1.13 |
| D to C | nonwhite or Hispanic | -0.034 | 0.024 | 0.97 | 0.92 | 1.01 |
| D to L | log rate at 65 | -1.924 | 0.035 |  |  |  |
| D to L | age, per 10 years | 0.438 | 0.014 | 1.55 | 1.51 | 1.59 |
| D to L | female | 0.015 | 0.030 | 1.02 | 0.96 | 1.08 |
| D to L | any college | -0.071 | 0.031 | 0.93 | 0.88 | 0.99 |
| D to L | nonwhite or Hispanic | 0.165 | 0.031 | 1.18 | 1.11 | 1.25 |
| D to X | log rate at 65 | -2.870 | 0.076 |  |  |  |
| D to X | age, per 10 years | 0.353 | 0.036 | 1.42 | 1.32 | 1.53 |
| D to X | female | -0.438 | 0.085 | 0.65 | 0.55 | 0.76 |
| D to X | any college | -0.363 | 0.096 | 0.70 | 0.58 | 0.84 |
| D to X | nonwhite or Hispanic | -0.452 | 0.104 | 0.64 | 0.52 | 0.78 |
| L to D | log rate at 65 | -1.217 | 0.044 |  |  |  |
| L to D | age, per 10 years | -0.393 | 0.017 | 0.67 | 0.65 | 0.70 |
| L to D | female | -0.087 | 0.041 | 0.92 | 0.85 | 0.99 |
| L to D | any college | -0.035 | 0.043 | 0.97 | 0.89 | 1.05 |
| L to D | nonwhite or Hispanic | 0.101 | 0.041 | 1.11 | 1.02 | 1.20 |
| L to X | log rate at 65 | -1.788 | 0.039 |  |  |  |
| L to X | age, per 10 years | 0.429 | 0.014 | 1.54 | 1.49 | 1.58 |
| L to X | female | -0.385 | 0.031 | 0.68 | 0.64 | 0.72 |
| L to X | any college | 0.013 | 0.032 | 1.01 | 0.95 | 1.08 |
| L to X | nonwhite or Hispanic | -0.277 | 0.034 | 0.76 | 0.71 | 0.81 |

**Table 3.** Mortality: the fitted model, the calibrated model and the 2023 US period life table.

*Entry mix of HRS respondents aged 64 to 66. The multiplier scales death intensities from every live state and equals exp(c0 + c1 (age - 65)/10) at the calibrated values.*

| Sex | e65, fitted | e65, calibrated | e65, life table | Multiplier at 65 | 75 | 85 | 95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| male | 16.72 | 18.31 | 18.19 | 0.70 | 0.77 | 0.84 | 0.92 |
| female | 19.54 | 20.87 | 20.71 | 0.64 | 0.76 | 0.89 | 1.05 |

| Sex | Age | qx, fitted | qx, calibrated | qx, life table |
|---|---:|---:|---:|---:|
| male | 65 | 0.0198 | 0.0141 | 0.0162 |
| male | 70 | 0.0302 | 0.0230 | 0.0226 |
| male | 75 | 0.0459 | 0.0371 | 0.0335 |
| male | 80 | 0.0688 | 0.0587 | 0.0542 |
| male | 85 | 0.1009 | 0.0904 | 0.0922 |
| male | 90 | 0.1441 | 0.1348 | 0.1599 |
| male | 95 | 0.2002 | 0.1939 | 0.2563 |
| female | 65 | 0.0133 | 0.0086 | 0.0101 |
| female | 70 | 0.0207 | 0.0150 | 0.0148 |
| female | 75 | 0.0325 | 0.0260 | 0.0237 |
| female | 80 | 0.0505 | 0.0439 | 0.0405 |
| female | 85 | 0.0766 | 0.0719 | 0.0709 |
| female | 90 | 0.1128 | 0.1129 | 0.1285 |
| female | 95 | 0.1609 | 0.1696 | 0.2160 |

**Table 4.** Annual cost by health state and age band: Medicare and out of pocket.

*Medicare: MCBS Cost Supplement cells (age by chronic-condition count) weighted by each HRS state's condition-count mix; it excludes facility, hospice and institutional events and is a lower bound for the disability and long-term-care states. Out of pocket: HRS, annualized from the two-year recall, premiums excluded.*

| State | Age | Share 0-1 conditions | 2-3 | 4+ | Medicare | Out of pocket, mean |
|---|---:|---:|---:|---:|---:|---:|
| Healthy | 65-74 | 1.00 | 0.00 | 0.00 | $5,291 | $1,216 |
| Healthy | 75+ | 1.00 | 0.00 | 0.00 | $7,010 | $1,313 |
| Chronic illness | 65-74 | 0.28 | 0.55 | 0.17 | $10,000 | $2,032 |
| Chronic illness | 75+ | 0.21 | 0.57 | 0.22 | $12,029 | $2,256 |
| Disability | 65-74 | 0.13 | 0.48 | 0.39 | $12,658 | $2,730 |
| Disability | 75+ | 0.12 | 0.50 | 0.38 | $13,625 | $3,078 |
| Long-term-care need | 65-74 | 0.09 | 0.39 | 0.53 | $14,048 | $5,018 |
| Long-term-care need | 75+ | 0.10 | 0.41 | 0.49 | $14,527 | $10,364 |

**Table 4b.** The annual out-of-pocket distribution by state, age band and sex (HRS core interviews).

| State | Age | Sex | n | Mean | p50 | p90 | p95 | p99 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Healthy | 65-74 | female | 3,844 | $1,233 | $517 | $3,035 | $5,059 | $9,384 |
| Healthy | 65-74 | male | 3,412 | $1,198 | $374 | $2,766 | $4,592 | $11,467 |
| Healthy | 75+ | female | 1,877 | $1,227 | $450 | $3,093 | $4,892 | $11,922 |
| Healthy | 75+ | male | 1,575 | $1,425 | $435 | $3,198 | $4,856 | $16,385 |
| Chronic illness | 65-74 | female | 28,618 | $2,085 | $1,005 | $4,685 | $7,007 | $15,606 |
| Chronic illness | 65-74 | male | 22,432 | $1,972 | $909 | $4,489 | $7,019 | $15,699 |
| Chronic illness | 75+ | female | 24,613 | $2,316 | $1,046 | $4,991 | $7,486 | $19,126 |
| Chronic illness | 75+ | male | 17,988 | $2,174 | $1,030 | $5,021 | $7,508 | $16,070 |
| Disability | 65-74 | female | 4,222 | $2,814 | $1,093 | $6,156 | $9,277 | $23,505 |
| Disability | 65-74 | male | 2,917 | $2,623 | $1,017 | $6,824 | $9,191 | $22,779 |
| Disability | 75+ | female | 6,822 | $3,143 | $1,262 | $6,656 | $10,000 | $30,663 |
| Disability | 75+ | male | 4,038 | $2,965 | $1,292 | $6,454 | $10,629 | $24,592 |
| Long-term-care need | 65-74 | female | 1,901 | $5,073 | $991 | $10,930 | $19,606 | $83,499 |
| Long-term-care need | 65-74 | male | 1,123 | $4,929 | $635 | $10,417 | $24,931 | $62,414 |
| Long-term-care need | 75+ | female | 6,177 | $10,829 | $1,763 | $33,612 | $56,427 | $122,600 |
| Long-term-care need | 75+ | male | 2,601 | $9,228 | $1,764 | $25,519 | $49,953 | $101,341 |

**Table 4c.** Out-of-pocket spending in the last year of life (HRS exit interviews).

*Spending from the last core interview to death, pro-rated to twelve months where that window is longer. Unweighted; age band at death.*

| Age at death | Sex | n | Months, median | Mean | p50 | p90 | p95 | p99 | Whole window, mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 65-74 | male | 1,664 | 14 | $6,340 | $1,216 | $15,935 | $28,273 | $82,128 | $9,444 |
| 65-74 | female | 1,438 | 15 | $7,429 | $1,188 | $17,069 | $33,652 | $104,425 | $11,414 |
| 75+ | male | 4,986 | 15 | $9,913 | $1,650 | $24,853 | $50,660 | $125,678 | $14,483 |
| 75+ | female | 6,488 | 15 | $12,641 | $1,805 | $32,970 | $67,776 | $151,655 | $18,814 |

**Table 5.** Expected lifetime cost from age 65 by sex and health state at 65, present value at 3%.

*100,000 simulated lives per row, calibrated mortality. Intervals are the 2.5th and 97.5th percentiles of the analytic expected value over 200 draws of the transition parameters. The analytic column is the forward recursion the simulation mean must match.*

| Sex | State at 65 | e65 | Ever LTC need | Medicare | low | high | Out of pocket | analytic | low | high | OOP median | Part B premium |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| male | Healthy | 20.4 | 43.3% | $140,295 | $138,892 | $141,466 | $35,373 | $35,401 | $35,083 | $35,691 | $28,827 | $31,993 |
| male | Chronic illness | 18.4 | 43.5% | $157,627 | $156,219 | $158,575 | $38,205 | $38,128 | $37,809 | $38,409 | $31,997 | $29,399 |
| male | Disability | 16.0 | 55.3% | $147,323 | $145,578 | $148,872 | $38,046 | $37,839 | $37,435 | $38,256 | $30,803 | $25,979 |
| male | Long-term-care need | 12.5 | 100.0% | $126,204 | $123,775 | $128,520 | $38,065 | $38,131 | $37,307 | $38,773 | $27,543 | $20,917 |
| male | Population mix | 18.3 | 46.4% | $153,316 | $151,948 | $154,224 | $37,660 | $37,703 | $37,398 | $38,002 | $31,282 | $29,224 |
| female | Healthy | 23.0 | 56.9% | $157,174 | $156,126 | $158,443 | $44,736 | $44,575 | $44,249 | $44,978 | $35,152 | $34,855 |
| female | Chronic illness | 21.0 | 58.5% | $176,905 | $176,074 | $178,149 | $49,450 | $49,349 | $49,048 | $49,797 | $39,378 | $32,442 |
| female | Disability | 18.8 | 68.0% | $170,146 | $169,087 | $171,684 | $50,378 | $50,601 | $50,195 | $51,198 | $39,203 | $29,554 |
| female | Long-term-care need | 15.7 | 100.0% | $153,454 | $151,444 | $155,697 | $51,752 | $52,147 | $51,387 | $52,990 | $38,550 | $25,170 |
| female | Population mix | 20.8 | 60.6% | $172,481 | $171,643 | $173,609 | $48,975 | $48,889 | $48,580 | $49,354 | $38,684 | $32,221 |

**Table 5b.** Expected years in each health state from 65, and the end-of-life component of out-of-pocket cost.

| Sex | State at 65 | e65 | Healthy | Chronic illness | Disability | LTC need | End-of-life increment, PV |
|---|---:|---:|---:|---:|---:|---:|---:|
| male | Healthy | 20.4 | 7.4 | 9.6 | 2.0 | 1.4 | $2,691 |
| male | Chronic illness | 18.4 | 0.1 | 14.7 | 2.3 | 1.4 | $2,766 |
| male | Disability | 16.0 | 0.2 | 9.2 | 4.4 | 2.1 | $2,582 |
| male | Long-term-care need | 12.5 | 0.1 | 5.3 | 2.6 | 4.5 | $2,030 |
| male | Population mix | 18.3 | 1.2 | 13.2 | 2.5 | 1.6 | $2,663 |
| female | Healthy | 23.0 | 7.6 | 10.6 | 2.5 | 2.2 | $3,155 |
| female | Chronic illness | 21.0 | 0.1 | 15.6 | 2.9 | 2.4 | $3,170 |
| female | Disability | 18.8 | 0.2 | 10.2 | 5.1 | 3.3 | $2,997 |
| female | Long-term-care need | 15.7 | 0.1 | 6.3 | 3.2 | 6.0 | $2,549 |
| female | Population mix | 20.8 | 1.2 | 14.0 | 3.1 | 2.6 | $3,072 |

**Table 5c.** Lifetime cost and tail risk by household income tertile at 65, population mix.

*Income tertiles within interview wave and age group. Out-of-pocket draws come from the same tertile at every age. The transition model has no income term, so life-expectancy differences by income are understated.*

| Sex | Income | Healthy at 65 | LTC need at 65 | Any college | e65 | Ever LTC need | Medicare | Out of pocket | OOP median | CVaR95 | CVaR99 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| male | low | 12.0% | 6.8% | 37% | 17.4 | 51.1% | $144,095 | $30,387 | $24,262 | $112,297 | $172,784 |
| female | low | 9.9% | 8.0% | 36% | 20.1 | 64.7% | $164,936 | $42,713 | $32,503 | $163,939 | $270,549 |
| male | middle | 13.5% | 2.3% | 53% | 18.2 | 45.8% | $153,486 | $36,836 | $30,849 | $123,238 | $184,223 |
| female | middle | 13.9% | 2.3% | 53% | 21.0 | 59.1% | $173,588 | $52,606 | $41,465 | $177,706 | $254,695 |
| male | high | 17.5% | 0.8% | 76% | 19.1 | 43.6% | $161,087 | $44,277 | $36,358 | $151,791 | $226,115 |
| female | high | 21.2% | 0.8% | 73% | 21.8 | 57.4% | $179,788 | $59,647 | $46,831 | $214,186 | $352,606 |

**Table 6.** The tail of lifetime out-of-pocket cost.

*VaR is the quantile of the present value of lifetime out-of-pocket cost; CVaR is the mean beyond it. LTC columns are the percentages of lives that ever entered the long-term-care-need state, in the tail and overall. The end-of-life share is the part of the tail's present value that comes from the final year's excess over an ordinary year.*

| Sex | State at 65 | Level | VaR | CVaR | CVaR / mean | LTC in tail | LTC overall | End-of-life share of tail |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| male | Healthy | 95% | $86,637 | $121,865 | 3.4 | 72.9% | 43.3% | 21.4% |
| male | Healthy | 99% | $143,643 | $185,781 | 5.3 | 66.6% | 43.3% | 22.0% |
| male | Chronic illness | 95% | $92,141 | $127,813 | 3.3 | 75.0% | 43.5% | 19.9% |
| male | Chronic illness | 99% | $146,630 | $193,398 | 5.1 | 74.3% | 43.5% | 21.3% |
| male | Disability | 95% | $99,727 | $137,762 | 3.6 | 84.6% | 55.3% | 18.1% |
| male | Disability | 99% | $159,174 | $203,938 | 5.4 | 82.8% | 55.3% | 19.9% |
| male | Long-term-care need | 95% | $116,010 | $158,274 | 4.2 | 100.0% | 100.0% | 12.6% |
| male | Long-term-care need | 99% | $184,878 | $225,998 | 5.9 | 100.0% | 100.0% | 13.8% |
| male | Population mix | 95% | $92,761 | $127,541 | 3.4 | 77.8% | 46.4% | 19.8% |
| male | Population mix | 99% | $148,529 | $188,051 | 5.0 | 72.9% | 46.4% | 23.1% |
| female | Healthy | 95% | $110,499 | $158,291 | 3.5 | 85.9% | 56.9% | 19.1% |
| female | Healthy | 99% | $181,042 | $253,353 | 5.7 | 81.6% | 56.9% | 22.1% |
| female | Chronic illness | 95% | $121,535 | $173,995 | 3.5 | 85.9% | 58.5% | 16.6% |
| female | Chronic illness | 99% | $200,697 | $277,558 | 5.6 | 80.1% | 58.5% | 18.4% |
| female | Disability | 95% | $131,855 | $186,309 | 3.7 | 91.2% | 68.0% | 13.4% |
| female | Disability | 99% | $208,306 | $296,705 | 5.9 | 88.5% | 68.0% | 15.9% |
| female | Long-term-care need | 95% | $146,020 | $197,908 | 3.8 | 100.0% | 100.0% | 11.0% |
| female | Long-term-care need | 99% | $222,409 | $294,386 | 5.7 | 100.0% | 100.0% | 14.0% |
| female | Population mix | 95% | $122,555 | $174,866 | 3.6 | 88.3% | 60.6% | 16.1% |
| female | Population mix | 99% | $198,738 | $282,008 | 5.8 | 84.0% | 60.6% | 18.4% |

**Table 7.** Financing scenarios: lifetime out-of-pocket cost for a cohort turning 65 in 2026, population mix.

*S1: from 2033, Part A pays 89% of scheduled benefits and the stated share of the shortfall falls on beneficiaries. S2: the whole cohort shortfall falls on person-years in long-term-care need. S3: S1 at 50% with real cost growth at the Trustees' Part B per-beneficiary rate.*

| Sex | Scenario | Mean | VaR95 | CVaR95 | CVaR99 | Change in mean | Change in CVaR95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| male | S0 baseline | $37,660 | $92,761 | $127,541 | $188,051 | $0 | $0 |
| male | S1 Part A payable 89% from 2033, shift 0% | $37,660 | $92,761 | $127,541 | $188,051 | $0 | $0 |
| male | S1 Part A payable 89% from 2033, shift 25% | $38,096 | $93,416 | $128,139 | $188,622 | $436 | $598 |
| male | S1 Part A payable 89% from 2033, shift 50% | $38,532 | $94,123 | $128,739 | $189,195 | $872 | $1,198 |
| male | S1 Part A payable 89% from 2033, shift 100% | $39,404 | $95,302 | $129,944 | $190,346 | $1,743 | $2,403 |
| male | S2 shortfall on long-term-care state | $39,404 | $97,468 | $133,487 | $194,797 | $1,743 | $5,945 |
| male | S3 real growth 1.7% and shift 50% | $47,089 | $120,209 | $164,531 | $239,987 | $9,428 | $36,990 |
| female | S0 baseline | $48,975 | $122,555 | $174,866 | $282,008 | $0 | $0 |
| female | S1 Part A payable 89% from 2033, shift 0% | $48,975 | $122,555 | $174,866 | $282,008 | $0 | $0 |
| female | S1 Part A payable 89% from 2033, shift 25% | $49,496 | $123,198 | $175,547 | $282,682 | $521 | $681 |
| female | S1 Part A payable 89% from 2033, shift 50% | $50,017 | $123,847 | $176,230 | $283,357 | $1,042 | $1,363 |
| female | S1 Part A payable 89% from 2033, shift 100% | $51,059 | $125,192 | $177,598 | $284,713 | $2,084 | $2,732 |
| female | S2 shortfall on long-term-care state | $51,059 | $127,870 | $181,247 | $288,305 | $2,084 | $6,380 |
| female | S3 real growth 1.7% and shift 50% | $62,756 | $161,692 | $230,086 | $367,038 | $13,781 | $55,219 |

**Table 7b.** Exhausting household assets at 65 through out-of-pocket cost, by household income tertile at 65.

*Undiscounted cumulative out-of-pocket cost against household net assets at 65 in 2024 dollars, with no asset returns or income. The exhaustion share is among households with positive assets.*

| Sex | Income | Scenario | Median assets | No positive assets | Exhaust assets | Median age at exhaustion |
|---|---:|---:|---:|---:|---:|---:|
| male | low | S0 baseline | $66,192 | 19.0% | 32.2% | 70 |
| male | low | S1 shift 50% | $66,192 | 19.0% | 32.6% | 70 |
| male | middle | S0 baseline | $304,270 | 4.3% | 11.3% | 75 |
| male | middle | S1 shift 50% | $304,270 | 4.3% | 11.6% | 75 |
| male | high | S0 baseline | $817,677 | 1.7% | 3.6% | 77 |
| male | high | S1 shift 50% | $817,677 | 1.7% | 3.7% | 77 |
| female | low | S0 baseline | $66,388 | 18.8% | 36.9% | 71 |
| female | low | S1 shift 50% | $66,388 | 18.8% | 37.4% | 71 |
| female | middle | S0 baseline | $305,424 | 4.3% | 14.4% | 77 |
| female | middle | S1 shift 50% | $305,424 | 4.3% | 14.6% | 77 |
| female | high | S0 baseline | $816,875 | 1.7% | 4.8% | 79 |
| female | high | S1 shift 50% | $816,875 | 1.7% | 4.9% | 79 |

**Table 8.** Robustness: each row changes one decision.

*Population mix at 65, calibrated mortality unless stated; 40,000 lives per sex. Refits use the sex-only covariate set and rebuild the entry mix, state costs and calibration from the variant panel; compare them with the sex-only row.*

| Variant | e65 M | e65 F | Ever LTC M | Ever LTC F | Medicare M | Medicare F | OOP M | OOP F | CVaR95 M | CVaR95 F |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 18.3 | 20.9 | 46% | 61% | $153,106 | $172,744 | $37,606 | $49,194 | $128,011 | $173,690 |
| discount 2% | 18.3 | 20.9 | 46% | 61% | $169,324 | $192,785 | $42,087 | $55,911 | $146,755 | $201,653 |
| discount 4% | 18.3 | 20.9 | 46% | 61% | $139,336 | $155,907 | $33,848 | $43,644 | $113,192 | $151,794 |
| Trustees real growth 1.7% | 18.3 | 20.9 | 46% | 61% | $182,867 | $209,680 | $45,869 | $61,657 | $163,364 | $226,780 |
| D and L Medicare +25% | 18.3 | 20.9 | 46% | 61% | $162,628 | $185,857 | $37,606 | $49,194 | $128,011 | $173,690 |
| Medicare not scaled to MCBS | 18.3 | 20.9 | 46% | 61% | $129,102 | $145,787 | $37,606 | $49,194 | $128,011 | $173,690 |
| mortality not calibrated | 16.7 | 19.5 | 41% | 56% | $141,280 | $161,842 | $34,435 | $45,169 | $122,640 | $162,970 |
| no end-of-life step | 18.4 | 20.9 | 46% | 61% | $153,446 | $172,474 | $35,162 | $45,957 | $121,323 | $165,063 |
| sex-only model | 18.3 | 20.9 | 49% | 63% | $153,547 | $173,164 | $38,237 | $50,215 | $131,093 | $177,181 |
| L at 2+ ADLs (refit) | 18.3 | 20.8 | 60% | 72% | $153,730 | $172,475 | $38,371 | $49,448 | $130,977 | $171,743 |
| nursing home not L (refit) | 18.3 | 20.8 | 46% | 60% | $153,772 | $173,129 | $38,405 | $49,987 | $130,254 | $175,784 |
| waves 9-16 only (refit) | 18.3 | 20.8 | 48% | 62% | $153,036 | $172,062 | $35,392 | $44,363 | $118,334 | $155,362 |


# Appendix tables


**Table A1.** Observed transitions between consecutive interviews, and deaths.

*Counts of intervals by state at the start (rows) and at the end (columns). Deaths are dated to the month.*

| From | Healthy | Chronic illness | Disability | Long-term-care need | Dead |
|---|---:|---:|---:|---:|---:|
| Healthy | 24,501 | 5,808 | 768 | 232 | 423 |
| Chronic illness | 0 | 119,618 | 11,702 | 3,296 | 7,384 |
| Disability | 332 | 8,537 | 9,149 | 3,877 | 3,362 |
| Long-term-care need | 27 | 950 | 2,248 | 6,545 | 4,793 |

**Table A2.** One-year transition probabilities from the fitted model, reference covariates, before calibration.

| Sex | Age | From | Healthy | Chronic | Disability | LTC need | Dead |
|---|---:|---:|---:|---:|---:|---:|---:|
| male | 65 | Healthy | 0.875 | 0.105 | 0.014 | 0.001 | 0.006 |
| male | 65 | Chronic illness | 0.000 | 0.935 | 0.042 | 0.005 | 0.017 |
| male | 65 | Disability | 0.007 | 0.242 | 0.602 | 0.092 | 0.056 |
| male | 65 | Long-term-care need | 0.001 | 0.033 | 0.178 | 0.644 | 0.144 |
| male | 75 | Healthy | 0.842 | 0.115 | 0.027 | 0.003 | 0.013 |
| male | 75 | Chronic illness | 0.000 | 0.891 | 0.066 | 0.008 | 0.036 |
| male | 75 | Disability | 0.004 | 0.209 | 0.562 | 0.137 | 0.088 |
| male | 75 | Long-term-care need | 0.000 | 0.020 | 0.116 | 0.646 | 0.218 |
| male | 85 | Healthy | 0.786 | 0.123 | 0.051 | 0.008 | 0.032 |
| male | 85 | Chronic illness | 0.000 | 0.813 | 0.097 | 0.017 | 0.073 |
| male | 85 | Disability | 0.003 | 0.171 | 0.496 | 0.192 | 0.138 |
| male | 85 | Long-term-care need | 0.000 | 0.011 | 0.071 | 0.599 | 0.319 |
| female | 65 | Healthy | 0.879 | 0.104 | 0.013 | 0.001 | 0.003 |
| female | 65 | Chronic illness | 0.000 | 0.937 | 0.048 | 0.005 | 0.010 |
| female | 65 | Disability | 0.005 | 0.248 | 0.612 | 0.098 | 0.037 |
| female | 65 | Long-term-care need | 0.001 | 0.032 | 0.171 | 0.695 | 0.101 |
| female | 75 | Healthy | 0.850 | 0.115 | 0.026 | 0.003 | 0.006 |
| female | 75 | Chronic illness | 0.000 | 0.895 | 0.075 | 0.009 | 0.021 |
| female | 75 | Disability | 0.003 | 0.215 | 0.575 | 0.148 | 0.058 |
| female | 75 | Long-term-care need | 0.000 | 0.019 | 0.113 | 0.713 | 0.155 |
| female | 85 | Healthy | 0.803 | 0.124 | 0.049 | 0.009 | 0.015 |
| female | 85 | Chronic illness | 0.000 | 0.825 | 0.111 | 0.021 | 0.043 |
| female | 85 | Disability | 0.002 | 0.178 | 0.513 | 0.213 | 0.094 |
| female | 85 | Long-term-care need | 0.000 | 0.011 | 0.071 | 0.687 | 0.231 |

**Table A3.** State prevalence by age band: the weighted HRS cross-section against the calibrated model (percent of survivors).

| Sex | Age | Healthy, HRS | Healthy, model | Chronic illness, HRS | Chronic illness, model | Disability, HRS | Disability, model | Long-term-care need, HRS | Long-term-care need, model |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| female | 65-69 | 11.9% | 11.8% | 74.1% | 73.1% | 9.7% | 10.5% | 4.3% | 4.7% |
| female | 70-74 | 8.7% | 6.9% | 75.6% | 72.9% | 10.5% | 13.1% | 5.2% | 7.1% |
| female | 75-79 | 6.4% | 4.1% | 72.1% | 69.6% | 13.7% | 15.4% | 7.7% | 10.9% |
| female | 80-84 | 4.8% | 2.5% | 66.0% | 64.4% | 16.6% | 17.3% | 12.6% | 15.9% |
| female | 85-89 | 3.3% | 1.6% | 55.7% | 58.3% | 20.5% | 18.6% | 20.6% | 21.6% |
| female | 90-99 | 2.0% | 1.0% | 39.9% | 50.4% | 23.6% | 19.5% | 34.4% | 29.1% |
| male | 65-69 | 12.7% | 12.1% | 75.7% | 74.8% | 8.5% | 9.6% | 3.1% | 3.5% |
| male | 70-74 | 8.8% | 7.3% | 77.3% | 75.6% | 10.1% | 11.7% | 3.8% | 5.4% |
| male | 75-79 | 6.2% | 4.4% | 76.1% | 73.5% | 12.2% | 13.9% | 5.6% | 8.2% |
| male | 80-84 | 5.2% | 2.8% | 70.0% | 69.6% | 16.0% | 15.9% | 8.8% | 11.7% |
| male | 85-89 | 5.4% | 1.9% | 62.9% | 64.7% | 17.7% | 17.5% | 14.0% | 15.9% |
| male | 90-99 | 4.8% | 1.3% | 51.6% | 58.1% | 20.3% | 19.1% | 23.3% | 21.5% |

**Table A4.** Medicare spending per person-year by age band: the model cohort against the MCBS Cost Supplement.

*The model applies the MCBS cells to the simulated cohort's state and condition mix; a gap reflects the difference between that mix and the MCBS population's.*

| Age | Model | MCBS | MCBS SE | Model / MCBS |
|---|---:|---:|---:|---:|
| 65-74 | $10,051 | $9,920 | $357 | 1.013 |
| 75+ | $12,544 | $12,343 | $349 | 1.016 |

**Table A5.** Life expectancy at 65 by covariate profile and health state at 65, fitted model before calibration.

| Sex | Any college | Nonwhite or Hispanic | Healthy | Chronic illness | Disability | LTC need |
|---|---:|---:|---:|---:|---:|---:|
| female | no | no | 20.6 | 18.5 | 16.0 | 12.1 |
| female | no | yes | 20.0 | 18.2 | 16.5 | 13.7 |
| female | yes | no | 23.2 | 20.9 | 18.4 | 13.4 |
| female | yes | yes | 22.3 | 20.3 | 18.5 | 14.9 |
| male | no | no | 17.7 | 15.5 | 13.0 | 9.2 |
| male | no | yes | 16.9 | 15.2 | 13.5 | 10.6 |
| male | yes | no | 20.3 | 17.9 | 15.3 | 10.4 |
| male | yes | yes | 19.3 | 17.2 | 15.4 | 11.7 |

**Table A6.** MCBS Cost Supplement: annual spending per beneficiary by payer, 2019 and 2021 to 2023 pooled.

*Medicare includes fee-for-service and Medicare Advantage payments. Standard errors from Fay-adjusted BRR with 100 replicates.*

| Cell | n | In MA | Medicare | SE | Medicaid | Out of pocket | SE | All payers | Part A share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All | 29,144 | 44.2% | $11,802 | $278 | $572 | $2,717 | $46 | $17,406 | 17.6% |
| 65-74 | 10,346 | 42.4% | $9,920 | $357 | $315 | $2,510 | $60 | $14,974 | 16.2% |
| 75 and over | 14,033 | 46.3% | $12,343 | $349 | $386 | $3,228 | $69 | $18,330 | 18.6% |
| 65-74, 0-1 chronic conditions | 2,239 | 34.9% | $4,418 | $493 | $42 | $1,624 | $65 | $7,264 | 13.4% |
| 65-74, 2-3 chronic conditions | 4,282 | 42.2% | $8,217 | $445 | $118 | $2,389 | $89 | $12,909 | 16.1% |
| 65-74, 4+ chronic conditions | 3,824 | 47.6% | $15,499 | $720 | $725 | $3,229 | $107 | $22,414 | 16.7% |
| 75 and over, 0-1 chronic conditions | 1,791 | 43.9% | $5,976 | $405 | $93 | $2,445 | $144 | $9,718 | 16.7% |
| 75 and over, 2-3 chronic conditions | 5,402 | 44.9% | $9,648 | $402 | $122 | $2,868 | $81 | $14,575 | 16.7% |
| 75 and over, 4+ chronic conditions | 6,840 | 48.0% | $15,930 | $542 | $656 | $3,690 | $98 | $23,267 | 19.7% |
| 65+, 0-1 chronic conditions, Income $25,000 or less | 824 | 40.2% | $5,516 | $835 | $265 | $818 | $69 | $7,137 | 13.7% |
| 65+, 0-1 chronic conditions, Income over $25,000 | 3,206 | 36.6% | $4,685 | $399 | $10 | $2,067 | $78 | $8,090 | 14.6% |
| 65+, 2-3 chronic conditions, Income $25,000 or less | 2,239 | 58.8% | $9,743 | $998 | $519 | $1,336 | $93 | $12,591 | 17.1% |
| 65+, 2-3 chronic conditions, Income over $25,000 | 7,445 | 39.4% | $8,520 | $372 | $22 | $2,874 | $81 | $13,776 | 16.2% |
| 65+, 4+ chronic conditions, Income $25,000 or less | 3,377 | 61.8% | $16,001 | $702 | $2,182 | $1,872 | $104 | $21,208 | 19.5% |
| 65+, 4+ chronic conditions, Income over $25,000 | 7,287 | 42.2% | $15,594 | $626 | $95 | $4,088 | $100 | $23,482 | 17.8% |

**Table A7.** 2023 US period life table, selected ages (NCHS).

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
