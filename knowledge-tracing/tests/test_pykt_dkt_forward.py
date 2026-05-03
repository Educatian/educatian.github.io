from __future__ import annotations

import json
from pathlib import Path

import torch
from pykt.models.dkt import DKT


ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "tests" / "results"
OUTDIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    torch.manual_seed(42)
    model = DKT(num_c=8, emb_size=16)
    q = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 5]], dtype=torch.long)
    r = torch.tensor([[0, 1, 0, 1, 1], [1, 0, 1, 1, 0]], dtype=torch.long)
    with torch.no_grad():
        logits = model(q, r)
        probs = torch.sigmoid(logits)

    result = {
        "model": "DKT",
        "num_concepts": 8,
        "embedding_size": 16,
        "input_shape_q": list(q.shape),
        "output_shape": list(logits.shape),
        "probability_range": [float(probs.min()), float(probs.max())],
        "sample_step_0": [round(float(x), 6) for x in probs[0, 0, :4]],
    }
    (OUTDIR / "pykt_dkt_forward.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
