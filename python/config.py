"""
Every analytic choice in Paper 5, in one place.

A parameter that is an assumption rather than an estimate lives here so it can
be changed in one line and so the robustness table can vary it.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
HRS = RAW / "hrs"
MCBS = RAW / "mcbs"
TRUSTEES = RAW / "trustees"
DERIVED = ROOT / "data" / "derived"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"
for _p in (DERIVED, TABLES, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)

SEED = 2026

# --------------------------------------------------------- MCBS PUFs ----
# Cost Supplement PUF years on disk. 2020 is omitted: pandemic-year use and
# spending are not a basis for a lifetime projection.
MCBS_CS_YEARS = (2019, 2021, 2022, 2023)
MCBS_CS_FILE = "CSPUF{y}_Data/cspuf{y}.csv"
# Variance: balanced repeated replication with Fay's adjustment of 0.30, on
# CSPUFWGT with replicates CSPUF001-CSPUF100 (MCBS Cost Supplement PUF Data
# User's Guide, variance estimation section).
MCBS_REPLICATES = 100
MCBS_FAY = 0.30
# The Cost Supplement PUF excludes facility, hospice and institutional events
# (same guide). Its spending therefore describes community-dwelling use only
# and cannot supply long-term-care-state costs; those come from HRS.

# CPI-U, all items, World Bank FP.CPI.TOTL, rebased to 2024 dollars (the
# series used in Papers 3, 4 and 6).
BASE_YEAR = 2024
CPI_TO_BASE = {2018: 1.24922, 2019: 1.22699, 2020: 1.21204, 2021: 1.15765,
               2022: 1.07187, 2023: 1.02950, 2024: 1.00000}

# ------------------------------------------------- Trustees (2026 report) ----
# Read from the 2026 Medicare Trustees Report PDF (data/raw/trustees),
# 14 September 2026.
HI_DEPLETION = "second quarter of 2033"
HI_DEPLETION_YEAR = 2033
HI_PAYABLE_SHARE_AT_DEPLETION = 0.89
# The payable share is not constant. Report p. 37: "89 percent in 2033 (year
# of depletion), 85 percent in 2050 (25th projection year), and about 93
# percent in 2100". Interpolated linearly between these points.
HI_PAYABLE_PATH = {2033: 0.89, 2050: 0.85, 2100: 0.93}
MEDICARE_GDP_SHARE = {2025: 0.039, 2050: 0.065}

# Table II.C1, Key Assumptions 2050-2100, intermediate. Annual growth in per
# beneficiary Medicare expenditures excluding demographic impacts, nominal.
# The low-cost and high-cost columns of that table print a footnote marker
# ("3") for these rows, not a rate: alternative long-range projections are
# prepared only for Part A (report section III.B3). Do not read them as 3%.
TR_PER_BENEFICIARY_GROWTH_NOMINAL = {"A": 0.035, "B": 0.038, "D": 0.040, "total": 0.037}
# Same rows in real terms, deflated by the chain-weighted GDP price index
# (footnote 1 to Table II.C1). These drive real cost trend in projections.
TR_PER_BENEFICIARY_GROWTH_REAL = {"A": 0.014, "B": 0.017, "D": 0.019}
TR_REAL_INTEREST_RATE = 0.023
# Table II.B1, calendar year 2025: HI benefits $438.3 billion of $1,197.8
# billion total Medicare benefits (Parts A, B and D).
TR_HI_BENEFITS_2025_BN = 438.3
TR_TOTAL_BENEFITS_2025_BN = 1197.8
TR_HI_SHARE_OF_BENEFITS = TR_HI_BENEFITS_2025_BN / TR_TOTAL_BENEFITS_2025_BN
# Table V.D1, average incurred cost per beneficiary, calendar year 2024:
# HI $6,256, Part B $8,733, Part D $2,848, total $17,837. The HI share of all
# Medicare spending per beneficiary is the object a Hospital Insurance
# shortfall applies to, and it includes skilled nursing, hospice and the HI
# part of payments to Medicare Advantage plans.
TR_PER_BENEFICIARY_2024 = {"HI": 6256.0, "B": 8733.0, "D": 2848.0, "total": 17837.0}
HI_SHARE_OF_MEDICARE = TR_PER_BENEFICIARY_2024["HI"] / TR_PER_BENEFICIARY_2024["total"]
TR_CPI_GROWTH = 0.024
TR_GDP_DEFLATOR_GROWTH = 0.0205
TR_MEDICAL_PRICE_GROWTH = 0.028

# -------------------------------------------------------- health states ----
# Spec Section 5.2. Thresholds are levers; alternatives go to robustness.
STATES = ("H", "C", "D", "L", "N", "X")
STATE_LABELS = {"H": "Healthy", "C": "Chronic illness", "D": "Disability",
                "L": "Severe disability at home", "N": "Nursing home",
                "X": "Dead"}
LIVE_STATES = STATES[:-1]
DEAD = len(STATES) - 1
ADL_DISABILITY = (1, 2)       # ADL limitations counted as D (community)
ADL_LTC_MIN = 3               # ADL limitations at or above this count as L
# Nursing-home residence is its own state. Out-of-pocket spending for private
# paying residents (about $27,000 a year) and for people with three or more
# ADL limitations living at home (about $4,000) are different distributions,
# and pooling them made the long-term-care tail a nursing-home tail that the
# model could not see. NURSING_HOME_IS_L = True is the robustness variant.
NURSING_HOME_IS_L = False
# Long-term-care need for the headline statistics: either state.
LTC_STATES = ("L", "N")
# 27-point cognition score at or below this counts as dementia in the
# robustness variant that puts dementia into long-term-care need (Langa and
# Weir classification of the HRS cognition items).
COG_DEMENTIA_CUT = 6
# Log-intensity age slope may change at these ages (a linear spline in age).
# A single Gompertz slope under-predicted deaths from the C and L states past
# 85 and ran the wrong way for C to L, which rises about tenfold from the
# early sixties to the nineties; the goodness-of-fit check (gof.py) rejects
# the single slope.
AGE_KNOTS = (70, 85)
# Intervals longer than this are split into equal pieces, with the intensity
# matrix held at each piece's midpoint age, rather than at the midpoint of the
# whole interval. Most intervals are about two years; 6% exceed three years
# and 4,809 exceed four.
MAX_PIECE_YEARS = 3.0

# ---------------------------------------------------- projection ----
ENTRY_AGE = 65
MAX_AGE = 110
DISCOUNT_RATES = (0.02, 0.03, 0.04)
PRIMARY_DISCOUNT = 0.03
N_SIMULATIONS = 100_000
TAIL_LEVELS = (0.90, 0.95, 0.99)

# --------------------------------------------------------------- costs ----
# Out-of-pocket distributions are taken from wave 8 (2006) on: earlier waves
# precede Part D, and mean annual spending in the chronic state at 65-74 was
# $3,465 in 2004 against $1,263 in 2022 in 2024 dollars.
OOP_MIN_WAVE = 8
# Share of Medicare spending going to people in their last year of life:
# 25.1% in 2006 (Riley and Lubitz 2010, Health Services Research 45(2),
# fee-for-service beneficiaries aged 65 and over). The state costs are
# redistributed to match this without changing the overall level.
MEDICARE_DECEDENT_SHARE = 0.251
# Premiums, monthly, 2024: standard Part B $174.70 and the Part D base
# beneficiary premium $34.70 (CMS fact sheets). Medicaid pays them for dual
# eligibles, so the simulation charges them only in years without Medicaid.
PART_B_PREMIUM_MONTHLY_2024 = 174.70
PART_D_PREMIUM_MONTHLY_2024 = 34.70

# ------------------------------------------------- Medicaid and spend-down ----
# Countable assets for Medicaid long-term-care eligibility, single person.
MEDICAID_ASSET_LIMIT = 2000.0
# Households meet out-of-pocket costs from income up to this share of income
# before drawing on assets.
OOP_FROM_INCOME_SHARE = 0.10

FIG_DPI = 300
PALETTE = {"ink": "#1A1A1A", "muted": "#7F8C8D", "rule": "#D5D8DC",
           "H": "#117A65", "C": "#1B6CA8", "D": "#B7950B", "L": "#B03A2E",
           "N": "#6C3483", "X": "#5D6D7E"}
