"""
The HRS panel: one row per person-interview with a health state, and the
interval file the multi-state model is fitted to.

Source: RAND HRS Longitudinal File 1992-2022 (V1), waves 4 to 16 (1998 to
2022), respondents aged 50 and over at interview. Earlier waves lack the
functional items in the form used here.

States, assessed at each interview:
  H  no chronic condition ever diagnosed and no ADL limitation
  C  at least one condition and no ADL limitation
  D  one or two ADL limitations, living in the community
  L  three or more ADL limitations, living in the community
  N  living in a nursing home at interview
  X  dead, dated from the RAND death date

Conditions are the eight RAND "ever had" indicators (hypertension, diabetes,
cancer, lung disease, heart problems, stroke, psychiatric problems,
arthritis), so C -> H cannot occur and is not allowed in the model. ADL
limitations are the RAND 0-5 count (walking across a room, dressing, bathing,
eating, getting in or out of bed). Nursing-home residence takes precedence
over the ADL count, and residents with a missing ADL count are still
classified.

Observations the model is fitted to, per person:
  obstype 1  consecutive interviews: state at each end, exact duration
  obstype 3  death: from the last interview to the death date
  obstype 2  known alive, state unknown: from the last classified interview
             to the latest wave at which the person was recorded as alive
             (interview status 1 or 4) without a classified state

The last of these matters. Deaths are found through exit interviews and the
National Death Index even after a person stops being interviewed, so counting
them while dropping the years in which people are known to be alive but
unclassified biases mortality upward. Adding those censored rows raises
unadjusted life expectancy at 65 by about 0.6 years.

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
# Interview status codes: 1 responded, 4 alive but non-response, 5 died this
# wave, 6 died in a previous wave, 7 dropped from the sample, 0 not yet in it.
ALIVE_STATUS = (1, 4)
WAVE_COLS = ["iwstat", "iwendy", "iwendm", "agem_e", "wtresp", "wtr_nh", "adl5a",
             "iadl5a", "nhmliv", "conde", "shlt", "oopmd", "govmd", "higov",
             "hosp", "nrshom", "cogtot", "cog27", "proxy", "demen", "alzhe",
             "mstat", "hiltc"]
HH_COLS = {"hh_income": "itot", "hh_assets": "atotb", "hh_assets_nonhousing": "atotn",
           "hh_assets_financial": "atotf"}


def columns():
    base = ["hhidpn", "rabyear", "rabmonth", "ragender", "raracem", "rahispan",
            "raeduc", "raedyrs", "radyear", "radmonth", "raestrat", "raehsamp"]
    cols = list(base)
    for w in WAVES:
        cols += [f"r{w}{v}" for v in WAVE_COLS + CONDS]
        cols += [f"h{w}{v}" for v in HH_COLS.values()]
    return cols


def load():
    it = pd.read_stata(FILE, iterator=True)
    have = set(it.variable_labels())
    cols = [c for c in columns() if c in have]
    missing = sorted(set(columns()) - have)
    if missing:
        print(f"  {len(missing)} requested variables absent, e.g. {missing[:6]}")
    return pd.read_stata(FILE, columns=cols, convert_categoricals=False)


def to_long(d, statuses=(1,)):
    """One row per person-wave with the given interview statuses."""
    rows = []
    for w in WAVES:
        s = pd.DataFrame({"hhidpn": d["hhidpn"], "wave": w})
        for v in WAVE_COLS:
            col = f"r{w}{v}"
            s[v] = pd.to_numeric(d[col], errors="coerce") if col in d else np.nan
        s["n_conditions_ever"] = sum(pd.to_numeric(d[f"r{w}{k}"], errors="coerce").fillna(0)
                                     for k in CONDS if f"r{w}{k}" in d)
        for name, suffix in HH_COLS.items():
            s[name] = pd.to_numeric(d.get(f"h{w}{suffix}"), errors="coerce")
        rows.append(s)
    long = pd.concat(rows, ignore_index=True)
    long = long[long["iwstat"].isin(statuses)].copy()
    long["age"] = long["agem_e"] / 12.0
    long["t"] = long["iwendy"] + (long["iwendm"] - 0.5) / 12.0
    # A wave with status 4 (alive, not interviewed) has no interview date; take
    # the middle of the wave's field period.
    mid = long["wave"].map(WAVE_YEAR) + 0.5
    long["t"] = long["t"].fillna(mid)
    return long


def assign_state(long, nursing_home_is_l=None, dementia_is_ltc=False):
    """Health state per interview; NaN where it cannot be assigned."""
    nh_is_l = config.NURSING_HOME_IS_L if nursing_home_is_l is None else nursing_home_is_l
    adl, nh = long["adl5a"], long["nhmliv"] == 1
    cond = long["n_conditions_ever"]
    state = pd.Series(np.nan, index=long.index)
    known = adl.notna()
    state[known & (adl == 0) & (cond == 0)] = 0
    state[known & (adl == 0) & (cond >= 1)] = 1
    state[known & adl.between(*config.ADL_DISABILITY)] = 2
    state[known & (adl >= config.ADL_LTC_MIN)] = 3
    if dementia_is_ltc:
        # Self-respondents with a 27-point cognition score at or below the cut,
        # or a proxy report of dementia or Alzheimer's disease, count as needing
        # long-term care wherever they live. The score is not in wave 16 and the
        # diagnosis items start in wave 10, so a flag carries forward to later
        # interviews: otherwise the loss of the score reads as recovery.
        dem = ((long["cog27"] <= config.COG_DEMENTIA_CUT)
               | (long["demen"] == 1) | (long["alzhe"] == 1))
        order = long.sort_values(["hhidpn", "wave"]).index
        dem = (dem.loc[order].astype(int).groupby(long.loc[order, "hhidpn"]).cummax()
               .reindex(long.index).astype(bool))
        state[known & dem & state.isin([0, 1, 2])] = 3
    state[nh] = 3 if nh_is_l else 4
    long["state"] = state
    return long


def build_intervals(long, people, alive_after=None):
    """Interval file: transitions, deaths and known-alive censoring."""
    long = long[long["state"].notna()].sort_values(["hhidpn", "t"])
    dead = people.set_index("hhidpn")
    last_alive = {} if alive_after is None else alive_after
    dead_state = config.DEAD
    rows = []
    for pid, g in long.groupby("hhidpn", sort=False):
        t = g["t"].to_numpy(); s = g["state"].to_numpy(int); a = g["age"].to_numpy()
        for i in range(1, len(g)):
            rows.append((pid, s[i - 1], s[i], t[i] - t[i - 1], a[i - 1], 1, t[i - 1]))
        dy, dm = dead.at[pid, "radyear"], dead.at[pid, "radmonth"]
        if np.isfinite(dy) and dy > 0:
            dm = dm if np.isfinite(dm) and dm > 0 else 6.5
            td = dy + (dm - 0.5) / 12.0
            # A death dated on or before the last interview month is kept with
            # a nominal half-month duration rather than dropped.
            rows.append((pid, s[-1], dead_state, max(td - t[-1], 1 / 24.0), a[-1], 3, t[-1]))
        else:
            ta = last_alive.get(pid, -np.inf)
            if ta > t[-1] + 1 / 12.0:
                rows.append((pid, s[-1], -1, ta - t[-1], a[-1], 2, t[-1]))
    iv = pd.DataFrame(rows, columns=["hhidpn", "from_state", "to_state", "duration",
                                     "age_start", "obstype", "t_start"])
    return iv[iv["duration"] > 0]


def known_alive_dates(d):
    """Latest date at which each person was recorded alive (status 1 or 4)."""
    alive = to_long(d, statuses=ALIVE_STATUS)
    return alive.groupby("hhidpn")["t"].max().to_dict()


def person_table(d):
    people = d[["hhidpn", "rabyear", "ragender", "raracem", "rahispan", "raeduc",
                "raedyrs", "radyear", "radmonth", "raestrat", "raehsamp"]].copy()
    for c in people.columns[1:]:
        people[c] = pd.to_numeric(people[c], errors="coerce")
    people["female"] = (people["ragender"] == 2).astype(int)
    people["college"] = (people["raeduc"] >= 4).astype(int)      # some college or more
    # Race is missing for a few hundred respondents; they are coded missing and
    # dropped from the fitted sample rather than counted as nonwhite.
    nonwhite = np.where(people["raracem"].isna(), np.nan,
                        ((people["raracem"] != 1) | (people["rahispan"] == 1)).astype(float))
    people["nonwhite"] = nonwhite
    people["household"] = (people["hhidpn"] // 1000).astype("int64")
    return people


def main():
    d = load()
    print(f"loaded {len(d):,} respondents, {d.shape[1]} columns")
    people = person_table(d)
    long = assign_state(to_long(d))
    long = long[long["age"] >= 50]
    long = long.merge(people[["hhidpn", "female", "college", "nonwhite", "rabyear",
                              "household", "radyear"]], on="hhidpn")
    iv = build_intervals(long, people, known_alive_dates(d))
    iv = iv.merge(people[["hhidpn", "female", "college", "nonwhite", "household"]], on="hhidpn")
    dropped = int(iv["nonwhite"].isna().sum())
    iv = iv[iv["nonwhite"].notna()].copy()

    long.to_pickle(config.DERIVED / "hrs_person_wave.pkl")
    iv.to_pickle(config.DERIVED / "hrs_intervals.pkl")

    obs = long[long["state"].notna()]
    n_people = obs["hhidpn"].nunique()
    w = pd.to_numeric(obs["wtresp"], errors="coerce").fillna(0)
    w = w.where(w > 0, pd.to_numeric(obs["wtr_nh"], errors="coerce").fillna(0))
    prev = obs.assign(state=obs["state"].astype(int), w=w).groupby("state")["w"].sum()
    prev = 100 * prev / prev.sum()
    crude = pd.crosstab(iv["from_state"], iv["to_state"])
    crude.to_csv(config.TABLES / "table1b_crude_transitions.csv")
    no_month = int(((people["radyear"] > 0) & ~(people["radmonth"] > 0)).sum())
    rows = [{"quantity": "Respondents with at least one classified interview", "value": n_people},
            {"quantity": "Person-interviews with a classified state", "value": len(obs)},
            {"quantity": "Intervals between interviews", "value": int((iv["obstype"] == 1).sum())},
            {"quantity": "Deaths", "value": int((iv["obstype"] == 3).sum())},
            {"quantity": "Deaths dated to the year only, placed at mid-year", "value": no_month},
            {"quantity": "Known-alive censored observations", "value": int((iv["obstype"] == 2).sum())},
            {"quantity": "Person-years in censored observations",
             "value": float(iv.loc[iv["obstype"] == 2, "duration"].sum())},
            {"quantity": "Observations dropped for missing race", "value": dropped},
            {"quantity": "Mean interval length, years", "value": float(iv["duration"].mean())},
            {"quantity": "Waves", "value": f"{WAVES[0]}-{WAVES[-1]} ({WAVE_YEAR[WAVES[0]]}-{WAVE_YEAR[WAVES[-1]]})"}]
    for k in config.LIVE_STATES:
        rows.append({"quantity": f"Weighted share of person-interviews in {config.STATE_LABELS[k]}, %",
                     "value": float(prev.get(config.STATES.index(k), 0))})
    pd.DataFrame(rows).to_csv(config.TABLES / "table1_sample.csv", index=False)

    print("\n=== HRS panel ===")
    for r in rows:
        v = r["value"]
        print(f"  {r['quantity']:<58} {v:,.1f}" if isinstance(v, float)
              else f"  {r['quantity']:<58} {v:,}" if isinstance(v, int)
              else f"  {r['quantity']:<58} {v}")
    print(f"\n  crude transitions (rows from, columns to; {config.DEAD} = dead, -1 = alive, state unknown):")
    print(crude.to_string())
    print(f"\n  interviews with no state assigned: {int(long['state'].isna().sum()):,}")
    print("wrote hrs_person_wave.pkl, hrs_intervals.pkl, tables 1 and 1b")


if __name__ == "__main__":
    main()
