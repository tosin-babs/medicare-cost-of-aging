"""
The HRS panel: one row per person-interview with a health state, and the
interval file the multi-state model is fitted to.

Source: RAND HRS Longitudinal File 1992-2022 (V1), waves 4 to 16 (1998 to
2022), respondents aged 50 and over at interview. Earlier waves lack the
functional items in the form used here.

States (spec Section 5.2), assessed at each interview:
  H  no chronic condition ever diagnosed and no ADL limitation
  C  at least one condition and no ADL limitation
  D  one or two ADL limitations, living in the community
  L  three or more ADL limitations, or living in a nursing home at interview
  X  dead, dated to the month from the RAND death date

Conditions are the eight RAND "ever had" indicators (hypertension, diabetes,
cancer, lung disease, heart problems, stroke, psychiatric problems,
arthritis), so C -> H cannot occur and is not allowed in the model. ADL
limitations are the RAND 0-5 count (walking across a room, dressing, bathing,
eating, getting in or out of bed).

Intervals. For each person, consecutive observed interviews form an interval
with the state at each end and the exact duration between interview end
dates (obstype 1). A death is a further interval from the last interview to
the death date (obstype 3). A person last seen alive is right-censored at
that interview and contributes nothing further. Missed interviews simply
lengthen the interval.

Writes data/derived/hrs_person_wave.pkl, hrs_intervals.pkl and Table 1.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config

WAVES = list(range(4, 17))
WAVE_YEAR = {w: 1992 + 2 * (w - 1) for w in WAVES}
CONDS = ["hibpe", "diabe", "cancre", "lunge", "hearte", "stroke", "psyche", "arthre"]
FILE = config.HRS / "randhrs1992_2022v1.dta"


def columns():
    base = ["hhidpn", "rabyear", "rabmonth", "ragender", "raracem", "rahispan",
            "raeduc", "raedyrs", "radyear", "radmonth", "raestrat", "raehsamp"]
    per_wave = ["iwstat", "iwendy", "iwendm", "agem_e", "wtresp", "wtr_nh",
                "adl5a", "iadl5a", "nhmliv", "conde", "shlt", "oopmd", "govmd",
                "higov", "hosp", "nrshom"] + CONDS
    cols = list(base)
    for w in WAVES:
        cols += [f"r{w}{v}" for v in per_wave] + [f"h{w}itot", f"h{w}atotb"]
    return cols


def load():
    it = pd.read_stata(FILE, iterator=True)
    have = set(it.variable_labels())
    cols = [c for c in columns() if c in have]
    missing = sorted(set(columns()) - have)
    if missing:
        print(f"  {len(missing)} requested variables absent, e.g. {missing[:6]}")
    return pd.read_stata(FILE, columns=cols, convert_categoricals=False)


def to_long(d):
    rows = []
    for w in WAVES:
        c = {v: f"r{w}{v}" for v in ["iwstat", "iwendy", "iwendm", "agem_e", "wtresp",
                                     "wtr_nh", "adl5a", "iadl5a", "nhmliv", "conde",
                                     "shlt", "oopmd", "govmd", "higov", "hosp", "nrshom"]}
        s = pd.DataFrame({"hhidpn": d["hhidpn"], "wave": w})
        for v, col in c.items():
            s[v] = pd.to_numeric(d[col], errors="coerce") if col in d else np.nan
        s["n_conditions_ever"] = sum(pd.to_numeric(d[f"r{w}{k}"], errors="coerce").fillna(0)
                                     for k in CONDS if f"r{w}{k}" in d)
        s["hh_income"] = pd.to_numeric(d.get(f"h{w}itot"), errors="coerce")
        s["hh_assets"] = pd.to_numeric(d.get(f"h{w}atotb"), errors="coerce")
        rows.append(s)
    long = pd.concat(rows, ignore_index=True)
    # iwstat 1 = responded, alive. 5 = died this wave, 6 = died previous wave.
    long = long[long["iwstat"] == 1].copy()
    long = long[long["iwendy"].notna() & long["iwendm"].notna() & long["agem_e"].notna()]
    long["age"] = long["agem_e"] / 12.0
    long["t"] = long["iwendy"] + (long["iwendm"] - 0.5) / 12.0
    return long


def assign_state(long):
    adl = long["adl5a"]
    nh = long["nhmliv"] == 1
    cond = long["n_conditions_ever"]
    state = pd.Series(np.nan, index=long.index)
    known = adl.notna()
    state[known & (adl == 0) & (cond == 0)] = 0
    state[known & (adl == 0) & (cond >= 1)] = 1
    state[known & adl.between(config.ADL_DISABILITY[0], config.ADL_DISABILITY[1])] = 2
    state[known & (adl >= config.ADL_LTC_MIN)] = 3
    if config.NURSING_HOME_IS_L:
        state[nh] = 3
    long["state"] = state
    return long


def build_intervals(long, people):
    long = long.sort_values(["hhidpn", "t"])
    long = long[long["state"].notna()]
    dead = people.set_index("hhidpn")
    rows = []
    for pid, g in long.groupby("hhidpn", sort=False):
        t = g["t"].to_numpy(); s = g["state"].to_numpy(int); a = g["age"].to_numpy()
        for i in range(1, len(g)):
            rows.append((pid, s[i - 1], s[i], t[i] - t[i - 1], a[i - 1], 1, t[i - 1]))
        dy, dm = dead.at[pid, "radyear"], dead.at[pid, "radmonth"]
        if np.isfinite(dy) and dy > 0:
            dm = dm if np.isfinite(dm) and dm > 0 else 6.5
            td = dy + (dm - 0.5) / 12.0
            if td > t[-1]:
                rows.append((pid, s[-1], 4, td - t[-1], a[-1], 3, t[-1]))
    iv = pd.DataFrame(rows, columns=["hhidpn", "from_state", "to_state", "duration",
                                     "age_start", "obstype", "t_start"])
    iv = iv[iv["duration"] > 0]
    return iv


def main():
    d = load()
    print(f"loaded {len(d):,} respondents, {d.shape[1]} columns")
    people = d[["hhidpn", "rabyear", "ragender", "raracem", "rahispan", "raeduc",
                "raedyrs", "radyear", "radmonth", "raestrat", "raehsamp"]].copy()
    for c in people.columns[1:]:
        people[c] = pd.to_numeric(people[c], errors="coerce")
    people["female"] = (people["ragender"] == 2).astype(int)
    people["college"] = (people["raeduc"] >= 4).astype(int)      # some college or more
    people["nonwhite"] = ((people["raracem"] != 1) | (people["rahispan"] == 1)).astype(int)

    long = assign_state(to_long(d))
    long = long[long["age"] >= 50]
    long = long.merge(people[["hhidpn", "female", "college", "nonwhite", "rabyear"]], on="hhidpn")
    iv = build_intervals(long, people)
    iv = iv.merge(people[["hhidpn", "female", "college", "nonwhite"]], on="hhidpn")

    long.to_pickle(config.DERIVED / "hrs_person_wave.pkl")
    iv.to_pickle(config.DERIVED / "hrs_intervals.pkl")

    # Table 1: sample, states and crude transitions.
    obs = long[long["state"].notna()]
    n_people = obs["hhidpn"].nunique()
    prev = (obs.assign(state=obs["state"].astype(int))
               .groupby("state")["wtresp"].sum())
    prev = 100 * prev / prev.sum()
    crude = pd.crosstab(iv["from_state"], iv["to_state"])
    crude.to_csv(config.TABLES / "table1b_crude_transitions.csv")
    rows = [{"quantity": "Respondents with at least one classified interview", "value": n_people},
            {"quantity": "Person-interviews with a classified state", "value": len(obs)},
            {"quantity": "Intervals between interviews", "value": int((iv["obstype"] == 1).sum())},
            {"quantity": "Deaths with an exact date", "value": int((iv["obstype"] == 3).sum())},
            {"quantity": "Mean interval length, years", "value": float(iv["duration"].mean())},
            {"quantity": "Waves", "value": f"{WAVES[0]}-{WAVES[-1]} ({WAVE_YEAR[WAVES[0]]}-{WAVE_YEAR[WAVES[-1]]})"}]
    for k, lab in config.STATE_LABELS.items():
        if k != "X":
            rows.append({"quantity": f"Weighted share of person-interviews in {lab}, %",
                         "value": float(prev.get(config.STATES.index(k), 0))})
    pd.DataFrame(rows).to_csv(config.TABLES / "table1_sample.csv", index=False)

    print(f"\n=== HRS panel ===")
    for r in rows:
        v = r["value"]
        print(f"  {r['quantity']:<58} {v:,.1f}" if isinstance(v, float) else f"  {r['quantity']:<58} {v:,}" if isinstance(v, int) else f"  {r['quantity']:<58} {v}")
    print("\n  crude transitions (rows from, columns to; 4 = dead):")
    print(crude.to_string())
    unc = int(long["state"].isna().sum())
    print(f"\n  interviews with ADL count missing (state unclassified): {unc:,}")
    print("wrote hrs_person_wave.pkl, hrs_intervals.pkl, tables 1 and 1b")


if __name__ == "__main__":
    main()
