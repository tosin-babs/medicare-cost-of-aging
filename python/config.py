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
TR_CPI_GROWTH = 0.024
TR_GDP_DEFLATOR_GROWTH = 0.0205
TR_MEDICAL_PRICE_GROWTH = 0.028

# -------------------------------------------------------- health states ----
# Spec Section 5.2. Thresholds are levers; alternatives go to robustness.
STATES = ("H", "C", "D", "L", "X")
STATE_LABELS = {"H": "Healthy", "C": "Chronic illness", "D": "Disability",
                "L": "Long-term-care need", "X": "Dead"}
ADL_DISABILITY = (1, 2)       # ADL limitations counted as D (community)
ADL_LTC_MIN = 3               # ADL limitations at or above this count as L
NURSING_HOME_IS_L = True

# ---------------------------------------------------- projection ----
ENTRY_AGE = 65
MAX_AGE = 110
DISCOUNT_RATES = (0.02, 0.03, 0.04)
PRIMARY_DISCOUNT = 0.03
N_SIMULATIONS = 100_000
TAIL_LEVELS = (0.90, 0.95, 0.99)

FIG_DPI = 300
PALETTE = {"ink": "#1A1A1A", "muted": "#7F8C8D", "rule": "#D5D8DC",
           "H": "#117A65", "C": "#1B6CA8", "D": "#B7950B", "L": "#B03A2E",
           "X": "#5D6D7E"}
