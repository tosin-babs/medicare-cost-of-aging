# Health-State Transitions and the Lifetime Cost of Aging

A multi-state actuarial model of lifetime Medicare spending and household out-of-pocket tail risk, built on the Health and Retirement Study (HRS) and the Medicare Current Beneficiary Survey (MCBS).

**Calculator:** https://medicare-cost-of-aging.vercel.app

## What it does

1. Fits a five-state continuous-time Markov model (healthy, chronic illness, disability, long-term-care need, dead) to 213,552 intervals between HRS interviews, 1998 to 2022, by exact likelihood for interval-censored panel data, with deaths dated to the month and covariates for age, sex, education and race-ethnicity.
2. Calibrates the model's mortality to the 2023 US period life table while keeping the relative mortality of the states.
3. Attaches annual Medicare cost by state from the MCBS Cost Supplement and empirical out-of-pocket cost distributions from HRS core interviews, with the last year of life drawn from HRS exit interviews.
4. Projects lifetime cost from 65 by microsimulation, checked against an exact recursion, and reports Value-at-Risk and Conditional Value-at-Risk of lifetime out-of-pocket cost, the paths that produce the tail, and results by income.
5. Stresses household cost against scenarios for the Hospital Insurance shortfall projected in the 2026 Medicare Trustees Report, and measures asset exhaustion by income.

## Headline results

Present value at 65, 2024 dollars, 3% discount rate, a 65-year-old drawn from the population:

| | Men | Women |
|---|---:|---:|
| Life expectancy at 65 (years) | 18.3 | 20.8 |
| Ever in long-term-care need | 46.4% | 60.6% |
| Lifetime Medicare spending | $153,316 | $172,481 |
| Lifetime out-of-pocket spending on care | $37,660 | $48,975 |
| CVaR95 of lifetime out-of-pocket spending | $127,541 | $174,866 |
| Share of that tail passing through long-term-care need | 77.8% | 88.3% |

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

`P5_ROBUST_REFIT=0` skips the three robustness refits.

## Layout

| Path | Contents |
|---|---|
| `python/multistate.py` | Continuous-time Markov estimator for interval-censored panel data (PyTorch matrix exponential, exact-death contributions, observed-information standard errors) |
| `python/build_hrs.py` | HRS states and interval file |
| `python/fit_transitions.py` | Intensity models, hazard ratios, health expectancies |
| `python/mcbs_costs.py`, `python/costs.py` | MCBS payer costs with replicate standard errors; HRS and exit-interview out-of-pocket distributions; Medicare cost by state |
| `python/population.py` | Entry mix at 65 and mortality calibration |
| `python/simulate.py`, `python/income.py` | Lifetime cost microsimulation, exact recursion, tail measures, parameter uncertainty, income tertiles |
| `python/validate.py` | Mortality, prevalence and spending validation |
| `python/scenarios.py` | Financing scenarios and asset exhaustion |
| `python/robustness.py` | One-change-at-a-time variants, including refits |
| `output/tables`, `output/figures` | Aggregate results |
| `manuscript/` | Paper source and rendered tables |
| `tool/` | Calculator (aggregate outputs only) |

## Citation

Babalola, O. D. (2026). *Health-State Transitions and the Lifetime Cost of Aging: A Multi-State Actuarial Model of Medicare Spending and Household Out-of-Pocket Tail Risk.* Code: https://github.com/tosin-babs/medicare-cost-of-aging

The HRS (Health and Retirement Study) is sponsored by the National Institute on Aging (grant numbers NIA U01AG009740 and NIA R01AG073289) and is conducted by the University of Michigan.

## Author

Oluwatosin Dorcas Babalola, Department of Actuarial Science and Quantitative Risk Analysis and Management, Georgia State University. obabalola4@student.gsu.edu

## License

Code is MIT-licensed. Survey microdata are governed by their providers' terms of use and are not redistributed.
