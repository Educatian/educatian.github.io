from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyBKT.fit import EM_fit
from pyBKT.models import Model


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "example_data" / "toy_kt_long.csv"
OUTDIR = ROOT / "tests" / "results"
OUTDIR.mkdir(parents=True, exist_ok=True)


def patch_em_run() -> None:
    """Run pyBKT in serial on Windows; avoids the multiprocessing guard bug."""

    if getattr(EM_fit.run, "__name__", "") == "run_serial_patch":
        return

    def run_serial_patch(data, model, trans_softcounts, emission_softcounts, init_softcounts, num_outputs, parallel=True, fixed={}):  # noqa: ANN001, E501
        alldata = data["data"]
        big_t, num_subparts = len(alldata[0]), len(alldata)
        allresources = data["resources"]
        starts = data["starts"]
        lengths = data["lengths"]
        learns = model["learns"]
        forgets = model["forgets"]
        guesses = model["guesses"]
        slips = model["slips"]
        prior = model["prior"]
        num_sequences = len(starts)
        num_resources = len(learns)
        normalize_lengths = False

        if "prior" in fixed:
            prior = fixed["prior"]

        initial_distn = np.empty((2,), dtype="float")
        initial_distn[0] = 1 - prior
        initial_distn[1] = prior

        as_matrix = np.empty((2, 2 * num_resources))
        EM_fit.interleave(as_matrix[0], 1 - learns, forgets.copy())
        EM_fit.interleave(as_matrix[1], learns.copy(), 1 - forgets)

        bn_matrix = np.empty((2, 2 * num_subparts))
        EM_fit.interleave(bn_matrix[0], 1 - guesses, guesses.copy())
        EM_fit.interleave(bn_matrix[1], slips.copy(), 1 - slips)

        payload = {
            "As": as_matrix,
            "Bn": bn_matrix,
            "initial_distn": initial_distn,
            "allresources": allresources,
            "starts": starts,
            "lengths": lengths,
            "num_resources": num_resources,
            "num_subparts": num_subparts,
            "alldata": alldata,
            "normalizeLengths": normalize_lengths,
            "alpha_out": np.zeros((2, big_t)),
        }
        thread_counts = []
        blocklen = 1 + ((num_sequences - 1) // 1)
        sequence_idx_start = 0
        sequence_idx_end = min(sequence_idx_start + blocklen, num_sequences)
        item = {"sequence_idx_start": sequence_idx_start, "sequence_idx_end": sequence_idx_end}
        item.update(payload)
        thread_counts.append(item)

        results = [EM_fit.inner(item) for item in thread_counts]

        all_trans_softcounts = np.zeros((2, 2 * num_resources))
        all_emission_softcounts = np.zeros((2, 2 * num_subparts))
        all_initial_softcounts = np.zeros((2, 1))
        alpha_out = np.zeros((2, big_t))
        total_loglike = np.empty((1, 1))
        total_loglike.fill(0)

        for result in results:
            total_loglike += result[3]
            all_trans_softcounts += result[0]
            all_emission_softcounts += result[1]
            all_initial_softcounts += result[2]
            for sequence_start, t_len, alpha in result[4]:
                alpha_out[:, sequence_start: sequence_start + t_len] += alpha

        all_trans_softcounts = all_trans_softcounts.flatten(order="F")
        all_emission_softcounts = all_emission_softcounts.flatten(order="F")

        return {
            "total_loglike": float(total_loglike[0, 0]),
            "all_trans_softcounts": np.reshape(all_trans_softcounts, (num_resources, 2, 2), order="C"),
            "all_emission_softcounts": np.reshape(all_emission_softcounts, (num_subparts, 2, 2), order="C"),
            "all_initial_softcounts": all_initial_softcounts,
            "alpha_out": alpha_out.flatten(order="F").reshape(alpha_out.shape, order="C"),
        }

    EM_fit.run = run_serial_patch


def main() -> None:
    patch_em_run()
    df = pd.read_csv(DATA)
    model = Model(seed=42, num_fits=1)
    model.fit(data=df)
    params = model.params().reset_index().round(6)
    preds = model.predict(data=df)
    result = {
        "python_version": "3.11",
        "rows": int(len(df)),
        "students": int(df["user_id"].nunique()),
        "skills": sorted(df["skill_name"].unique().tolist()),
        "rmse": float(model.evaluate(data=df, metric="rmse")),
        "param_rows": params.to_dict(orient="records"),
        "prediction_head": preds[["user_id", "skill_name", "correct", "correct_predictions", "state_predictions"]]
        .head(8)
        .round(6)
        .to_dict(orient="records"),
        "note": "Uses a serial monkeypatch for pyBKT.fit.EM_fit.run on Windows to avoid multiprocessing/import issues.",
    }
    (OUTDIR / "pybkt_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
