"""
Payer-specific annual costs for Medicare beneficiaries, from the MCBS Cost
Supplement public use files.

The Cost Supplement PUF reports each beneficiary's annual spending by payer:
Medicare fee-for-service, Medicare Advantage, Medicaid, private insurance,
out of pocket, discounts and other. Its only health measure is a count of
ever-diagnosed chronic conditions in three bands (0-1, 2-3, 4+), and it
excludes facility, hospice and institutional services. It therefore supplies
community-dwelling costs by chronic-condition burden, which maps to the
Healthy and Chronic-illness states, and nothing for long-term-care need.

Estimates pool 2019, 2021, 2022 and 2023 in 2024 dollars. Each year's weights
are divided by the number of pooled years, so a pooled estimate describes an
average year. Standard errors use the survey's balanced repeated replication
with Fay's adjustment of 0.30; for pooled estimates the replicate estimates
are formed from the pooled replicate weights.

Writes Tables 3a (cell means by payer) and 3b (out-of-pocket distribution).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config

PAYERS = {"PAMTCARE": "Medicare fee-for-service", "PAMTMADV": "Medicare Advantage",
          "PAMTCAID": "Medicaid", "PAMTALPR": "Private insurance",
          "PAMTOOP": "Out of pocket", "PAMTDISC": "Discounts",
          "PAMTOTH": "Other", "PAMTTOT": "Total"}
AGE = {1: "Under 65", 2: "65-74", 3: "75 and over"}
SEX = {1: "Male", 2: "Female"}
NCHRN = {1: "0-1 chronic conditions", 2: "2-3 chronic conditions", 3: "4+ chronic conditions"}
INCOME = {1: "Income $25,000 or less", 2: "Income over $25,000"}
REPS = [f"CSPUF{i:03d}" for i in range(1, config.MCBS_REPLICATES + 1)]


def load():
    frames = []
    for y in config.MCBS_CS_YEARS:
        f = config.MCBS / config.MCBS_CS_FILE.format(y=y)
        d = pd.read_csv(f, low_memory=False)
        d.columns = [c.upper() for c in d.columns]
        keep = ["PUF_ID", "CSP_AGE", "CSP_SEX", "CSP_RACE", "CSP_INCOME",
                "CSP_NCHRNCND", "CSPUFWGT", "PAMTIP", "PAMTHH"] + list(PAYERS) + REPS
        d = d[[c for c in keep if c in d.columns]].copy()
        # Categorical items carry SAS special missing codes (".", ".R", ".D",
        # ".N") in some years; coerce and count rather than drop silently.
        for c in ("CSP_AGE", "CSP_SEX", "CSP_RACE", "CSP_INCOME", "CSP_NCHRNCND"):
            raw = d[c]
            d[c] = pd.to_numeric(raw, errors="coerce")
            bad = int(d[c].isna().sum())
            if bad:
                print(f"  {y}: {c} missing or special-coded for {bad} beneficiaries "
                      f"({sorted(raw[d[c].isna()].astype(str).unique())[:4]})")
        for c in list(PAYERS) + ["PAMTIP", "PAMTHH"]:
            d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0) * config.CPI_TO_BASE[y]
        d["year"] = y
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    k = len(config.MCBS_CS_YEARS)
    extra = {c: pd.to_numeric(d[c], errors="coerce").fillna(0) / k
             for c in ["CSPUFWGT"] + REPS}
    extra["medicare_total"] = d["PAMTCARE"] + d["PAMTMADV"]
    extra["in_ma"] = (d["PAMTMADV"] > 0).astype(int)
    d = pd.concat([d.drop(columns=["CSPUFWGT"] + REPS), pd.DataFrame(extra)], axis=1)
    return d


def brr_se(values, frame, stat):
    """Fay-adjusted BRR standard error of stat(values, weights)."""
    full = stat(values, frame["CSPUFWGT"].to_numpy(float))
    reps = np.array([stat(values, frame[r].to_numpy(float)) for r in REPS])
    k = config.MCBS_FAY
    return full, float(np.sqrt(np.sum((reps - full) ** 2)
                               / (config.MCBS_REPLICATES * (1 - k) ** 2)))


def wmean(v, w):
    return float(np.sum(w * v) / np.sum(w)) if np.sum(w) > 0 else np.nan


def wquantile(v, w, q):
    o = np.argsort(v)
    cw = np.cumsum(w[o]) / np.sum(w)
    return float(np.interp(q, cw, v[o]))


def main():
    d = load()
    print(f"MCBS Cost Supplement PUF, {', '.join(map(str, config.MCBS_CS_YEARS))}: "
          f"{len(d):,} beneficiary-years, average weighted population "
          f"{d['CSPUFWGT'].sum() / 1e6:,.1f} million")

    rows = []
    cells = [("All", None)] + [(f"{AGE[a]}", ("CSP_AGE", a)) for a in (2, 3)]
    for a in (2, 3):
        for n in (1, 2, 3):
            cells.append((f"{AGE[a]}, {NCHRN[n]}", (("CSP_AGE", a), ("CSP_NCHRNCND", n))))
    for n in (1, 2, 3):
        for inc in (1, 2):
            cells.append((f"65+, {NCHRN[n]}, {INCOME[inc]}",
                          (("CSP_AGE", (2, 3)), ("CSP_NCHRNCND", n), ("CSP_INCOME", inc))))
    for label, spec in cells:
        m = np.ones(len(d), bool)
        conds = [] if spec is None else ([spec] if isinstance(spec[0], str) else list(spec))
        for col, val in conds:
            m &= d[col].isin(val if isinstance(val, tuple) else (val,)).to_numpy()
        s = d[m]
        row = {"cell": label, "n": int(len(s)),
               "weighted_millions": s["CSPUFWGT"].sum() / 1e6,
               "share_in_ma": wmean(s["in_ma"].to_numpy(float), s["CSPUFWGT"].to_numpy(float))}
        for col in ["medicare_total"] + list(PAYERS):
            est, se = brr_se(s[col].to_numpy(float), s, wmean)
            key = "medicare_total" if col == "medicare_total" else col.lower()
            row[f"{key}_mean"], row[f"{key}_se"] = est, se
        # Part A share: inpatient plus home health events over all events.
        # SNF and hospice are outside the Cost Supplement PUF, so this
        # understates Part A for the frail.
        # Inpatient plus home health, as a share of all-payer spending and of
        # Medicare spending. Neither is the Hospital Insurance share of
        # Medicare: skilled nursing and hospice, both Part A, are outside the
        # Cost Supplement, and most home health is paid by Part B. The
        # Trustees' per-beneficiary HI share (config.HI_SHARE_OF_MEDICARE) is
        # the object the scenarios use; this is the community lower bound.
        parta = (s["PAMTIP"] + s["PAMTHH"]).to_numpy(float)
        parta_mean = wmean(parta, s["CSPUFWGT"].to_numpy(float))
        row["part_a_share_of_total"] = parta_mean / row["pamttot_mean"]
        row["part_a_share_of_medicare"] = parta_mean / row["medicare_total_mean"]
        # Fee-for-service beneficiaries only: Medicare Advantage payments in
        # the PUF are capitation amounts, not costs incurred, so the FFS-only
        # mean is the cost-based alternative used in robustness.
        ffs = s[s["in_ma"] == 0]
        row["n_ffs"] = int(len(ffs))
        row["medicare_ffs_only_mean"], row["medicare_ffs_only_se"] = brr_se(
            ffs["medicare_total"].to_numpy(float), ffs, wmean)
        rows.append(row)
    t3a = pd.DataFrame(rows)
    t3a.to_csv(config.TABLES / "table3a_mcbs_costs.csv", index=False)

    q_rows = []
    for label, a in (("65 and over", (2, 3)), ("65-74", (2,)), ("75 and over", (3,))):
        for n in (1, 2, 3, None):
            m = d["CSP_AGE"].isin(a) & (True if n is None else d["CSP_NCHRNCND"] == n)
            s = d[m]
            v, w = s["PAMTOOP"].to_numpy(float), s["CSPUFWGT"].to_numpy(float)
            q_rows.append({"age": label, "chronic": "All" if n is None else NCHRN[n],
                           "n": int(len(s)), "oop_mean": wmean(v, w),
                           "oop_zero_share": wmean((v == 0).astype(float), w),
                           **{f"oop_p{int(q * 100)}": wquantile(v, w, q)
                              for q in (0.5, 0.9, 0.95, 0.99)}})
    t3b = pd.DataFrame(q_rows)
    t3b.to_csv(config.TABLES / "table3b_mcbs_oop_distribution.csv", index=False)

    print("\n=== Annual spending per beneficiary, 2024 dollars (BRR-Fay SE) ===")
    show = ["cell", "n", "medicare_total_mean", "medicare_total_se", "pamtoop_mean",
            "pamtoop_se", "pamttot_mean", "share_in_ma"]
    fmt = {c: "{:,.0f}".format for c in show if c not in ("cell", "n", "share_in_ma")}
    fmt["share_in_ma"] = "{:.1%}".format
    with pd.option_context("display.width", 200):
        print(t3a[show].to_string(index=False, formatters=fmt))
    print("\n=== Out-of-pocket distribution, 65 and over ===")
    with pd.option_context("display.width", 200, "display.float_format", "{:,.2f}".format):
        print(t3b.to_string(index=False))
    print("\nwrote tables 3a and 3b")


if __name__ == "__main__":
    main()
