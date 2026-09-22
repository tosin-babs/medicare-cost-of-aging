# Health-State Transitions and the Lifetime Cost of Aging

A multi-state actuarial model of lifetime Medicare spending and household out-of-pocket tail risk, built on the Health and Retirement Study (HRS) and the Medicare Current Beneficiary Survey (MCBS).

**Calculator:** https://medicare-cost-of-aging.vercel.app

## What it does

1. Fits a six-state continuous-time Markov model (healthy, chronic illness, disability, severe disability at home, nursing home, dead) to 197,258 intervals between HRS interviews, 1998 to 2022, by exact likelihood for interval-censored panel data: deaths dated to the month with the death intensity taken at the age at death, a linear spline in age with knots at 70 and 85, intensities held piecewise constant over pieces of at most three years, and standard errors clustered on the household.
2. Calibrates the model's mortality to the 2023 US period life table while keeping the relative mortality of the states, and tests the fit state by state against observed destinations.
3. Attaches annual Medicare cost by state from the MCBS Cost Supplement, with the concentration of spending in the last year of life imposed at the published share, and draws out-of-pocket cost from HRS by state, age band, sex, Medicaid status and income tertile, with a permanent component and an AR(1) so that costs persist, and the last year of life drawn from HRS exit interviews.
4. Projects lifetime cost from 65 by microsimulation with Medicaid reached through asset spend-down, checked against an exact recursion over the same cost cells, and reports Value-at-Risk and Conditional Value-at-Risk of lifetime out-of-pocket cost, the paths that produce the tail, and results by income.
5. Stresses household cost against scenarios for the Hospital Insurance shortfall projected in the 2026 Medicare Trustees Report, and reports who spends down to Medicaid, and when.

## Headline results

Present value at 65, 2024 dollars, 3% discount rate, a 65-year-old drawn from the population:

| | Men | Women |
|---|---:|---:|
| Life expectancy at 65 (years) | 18.2 | 20.7 |
| Ever in long-term care (severe disability at home or nursing home) | 44.2% | 57.9% |
| Ever on Medicaid after 65 | 15.3% | 23.2% |
| Lifetime Medicare spending | $154,423 | $171,804 |
| Lifetime out-of-pocket spending on care | $35,329 | $43,666 |
| Part B and Part D premiums | $32,195 | $33,977 |
| CVaR95 of lifetime out-of-pocket spending | $188,368 | $235,495 |
| CVaR95 as a multiple of the mean | 5.3 | 5.4 |
| Share of that tail passing through long-term care | 71.8% | 85.7% |
| Spend-down to Medicaid, lowest income tertile | 16% | 22% |

With out-of-pocket draws taken as independent across years, the way most cost
models treat them, CVaR95 falls to $119,229 and $158,542: persistence is the
single largest modeling choice for the tail.

## Data (not included)

HRS conditions of use do not allow redistribution, so no microdata is in this repository or in the calculator. To rebuild:

| Source | Where it goes |
|---|---|
| RAND HRS Longitudinal File 2022 (V1), Stata, from https://hrsdata.isr.umich.edu (free registration) | `data/raw/hrs/randhrs1992_2022v1.dta` |
| MCBS Cost Supplement PUF 2019, 2021, 2022, 2023, from cms.gov | `data/raw/mcbs/CSPUF{year}_Data/` |
| NCHS United States Life Tables, 2023, Tables 2 and 3 (NVSR 74-6) | `data/raw/lifetables/` |
| 2026 Medicare Trustees Report PDF | `data/raw/trustees/` |

## Running it

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python python/run_all.py          # about 45 minutes; the transition fits are the slow steps
.venv/bin/python -m pytest -q tests          # estimator recovery, calibration, cost recursion
.venv/bin/python python/check_manuscript.py  # every headline number in the paper against the tables
.venv/bin/python python/build_tool.py        # rebuild the calculator page
```

`P5_ROBUST_REFIT=0` skips the five robustness refits, which re-estimate the
transition model and take about an hour each.

## Layout

| Path | Contents |
|---|---|
| `python/multistate.py` | Continuous-time Markov estimator for interval-censored panel data (PyTorch matrix exponential, exact-death contributions, observed-information standard errors) |
| `python/build_hrs.py` | HRS states and interval file |
| `python/fit_transitions.py` | Intensity models, hazard ratios, health expectancies |
| `python/mcbs_costs.py`, `python/costs.py` | MCBS payer costs with replicate standard errors; HRS and exit-interview out-of-pocket distributions; Medicare cost by state |
| `python/population.py` | Entry mix at 65 and mortality calibration |
| `python/simulate.py` | Lifetime cost microsimulation with persistence and Medicaid spend-down, exact recursion, tail measures, parameter uncertainty, income tertiles |
| `python/validate.py` | Mortality, prevalence and spending validation |
| `python/scenarios.py` | Financing scenarios and asset exhaustion |
| `python/robustness.py` | One-change-at-a-time variants, including refits |
| `output/tables`, `output/figures` | Aggregate results |
| `manuscript/` | Paper source and rendered tables |
| `tool/` | Calculator (aggregate outputs only) |

## Citation

Babalola, O. D., Iroko, O. E., & Ansah, D. (2026). *Health-State Transitions and the Lifetime Cost of Aging: A Multi-State Actuarial Model of Medicare Spending and Household Out-of-Pocket Tail Risk.* Code: https://github.com/tosin-babs/medicare-cost-of-aging

The HRS (Health and Retirement Study) is sponsored by the National Institute on Aging (grant numbers NIA U01AG009740 and NIA R01AG073289) and is conducted by the University of Michigan.

## Authors

- Oluwatosin Dorcas Babalola, Department of Actuarial Science and Quantitative Risk Analysis and Management, Georgia State University, Atlanta, GA, USA, obabalola4@student.gsu.edu (corresponding)
- Oluwakemi Elizabeth Iroko, Department of Chemistry, University of Jos, Jos, Nigeria, Oluwakemi2345@gmail.com
- Doris Ansah, J. Mack Robinson College of Business, Georgia State University, Atlanta, GA, USA, dansah2@student.gsu.edu

## License

Code is MIT-licensed. Survey microdata are governed by their providers' terms of use and are not redistributed.
