"""
US period life tables by sex, for validating the multi-state model's mortality.

Source: Arias E, Xu J. United States Life Tables, 2023. National Vital
Statistics Reports, Vol. 74, No. 6 (NCHS, July 2025), Tables 2 (males) and 3
(females), downloaded as spreadsheets from the NVSR FTP folder 74-06.

The multi-state model's implied life expectancy at 65 is compared with e65
here, and its implied one-year death probabilities by age with qx. The HRS
sample is not the whole population (it excludes people who entered nursing
homes before their first interview, among others), so an exact match is not
expected; a gap of more than about a year at 65 would call for explanation.

Writes data/derived/lifetable_us_2023.csv and Table A1.
"""

from __future__ import annotations

import re

import pandas as pd

import config

FILES = {"male": "US_life_table_2023_Table02.xlsx",
         "female": "US_life_table_2023_Table03.xlsx"}


def load():
    frames = []
    for sex, f in FILES.items():
        raw = pd.read_excel(config.RAW / "lifetables" / f, header=None)
        body = raw.iloc[3:, :7].copy()
        body.columns = ["age_label", "qx", "lx", "dx", "Lx", "Tx", "ex"]
        body = body[body["age_label"].notna()]
        body["age"] = body["age_label"].astype(str).map(
            lambda s: int(re.match(r"\d+", s).group()) if re.match(r"\d+", s) else None)
        body = body.dropna(subset=["age"])
        for c in ("qx", "lx", "dx", "Lx", "Tx", "ex"):
            body[c] = pd.to_numeric(body[c], errors="coerce")
        body["sex"] = sex
        frames.append(body[["sex", "age", "qx", "lx", "ex"]])
    d = pd.concat(frames, ignore_index=True)
    d["age"] = d["age"].astype(int)
    return d


def main():
    d = load()
    d.to_csv(config.DERIVED / "lifetable_us_2023.csv", index=False)
    check = d[d["age"].isin([65, 70, 75, 80, 85, 90, 95, 100])]
    t = check.pivot_table(index="age", columns="sex", values=["qx", "ex"])
    t.columns = [f"{a}_{b}" for a, b in t.columns]
    t = t.reset_index()
    t.to_csv(config.TABLES / "tableA1_us_life_table_2023.csv", index=False)
    print("=== US life table 2023 (NCHS NVSR 74-6) ===")
    print(t.round(4).to_string(index=False))
    e65 = d[d["age"] == 65].set_index("sex")["ex"]
    print(f"\n  e65: male {e65['male']:.2f}, female {e65['female']:.2f}")
    print("wrote data/derived/lifetable_us_2023.csv and table A1")


if __name__ == "__main__":
    main()
