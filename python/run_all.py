"""
Run the whole analysis, in order.

    ../.venv/bin/python python/run_all.py

Seeded from config.SEED. The transition-model fit is the slow step (an hour
or more for the two models on 221,966 observations); the robustness refits
and the model extensions (fit_extensions.py, run separately) add about as
much each. Set P5_ROBUST_REFIT=0 to skip the refits.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import config  # noqa: E402

STEPS = [
    ("US life tables for validation", "lifetables"),
    ("MCBS payer-specific costs", "mcbs_costs"),
    ("HRS panel and health states", "build_hrs"),
    ("RQ1: transition intensities", "fit_transitions"),
    ("Goodness of fit of the transition model", "gof"),
    ("State-specific costs", "costs"),
    ("Entry sample and mortality calibration", "population"),
    ("RQ2 and RQ3: lifetime cost microsimulation, income and tail risk", "simulate"),
    ("RQ4: financing scenarios and Medicaid spend-down", "scenarios"),
    ("Validation against life tables, prevalence, spending and the literature", "validate"),
    ("Robustness", "robustness"),
    ("Figures", "exhibits"),
    ("Calculator payload", "export_tool_data"),
]


def main():
    started, timings = time.time(), []
    for title, module in STEPS:
        script = HERE / f"{module}.py"
        if not script.exists():
            print(f"\n[skipping {module}: not written yet]")
            continue
        print("\n" + "=" * 78 + f"\n{title}\n" + "=" * 78, flush=True)
        t0 = time.time()
        r = subprocess.run([sys.executable, "-u", str(script)], cwd=HERE)
        if r.returncode != 0:
            sys.exit(f"step {module} failed with exit code {r.returncode}")
        timings.append({"step": title, "seconds": round(time.time() - t0, 1)})
        print(f"[{title}: {timings[-1]['seconds']:.0f}s]", flush=True)
    versions = {"python": platform.python_version()}
    for mod in ("numpy", "pandas", "scipy", "torch"):
        try:
            versions[mod] = __import__(mod).__version__
        except Exception:
            versions[mod] = "unavailable"
    params = {k: str(v) for k, v in vars(config).items() if k.isupper()}
    (config.ROOT / "output" / "params_used.json").write_text(json.dumps(
        {"params": params, "versions": versions, "timings": timings}, indent=2))
    print(f"\nDone in {time.time() - started:.0f}s.")


if __name__ == "__main__":
    main()
