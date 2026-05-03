"""
generate_fake_dialogue.py — Synthesize a fake collaborative-learning dialogue
dataset for the ONA guide examples. Two conditions, five codes, two speakers.
The transition matrices differ between conditions so the resulting ONA networks
show a meaningful (but entirely fabricated) separation.

Output: fake_dialogue_long.csv with one row per turn.
Schema:
  user_id (P001..P100), cond (treatment/control), turn_idx (1..N),
  speaker (A or B), ASK, EXPLAIN, EXAMPLE, AGREE, ELABORATE  (0/1)
"""
from __future__ import annotations
import csv
import random
from pathlib import Path

random.seed(20260502)

CODES = ["ASK", "EXPLAIN", "EXAMPLE", "AGREE", "ELABORATE"]
N_PER_GROUP = 50
TURNS_RANGE = (24, 60)

# Two transition matrices over the 5 codes (rows = current code, cols = next).
# treatment promotes EXPLAIN -> EXAMPLE -> ELABORATE chains; control leans on
# ASK <-> EXPLAIN with looser ELABORATE structure. Differences are intentional
# so the comparison views show something visible — but values are made up.
TRANS = {
    "treatment": [
        # ASK  EXPLAIN EXAMPLE AGREE ELABORATE
        [0.05, 0.50, 0.10, 0.05, 0.30],   # from ASK
        [0.10, 0.10, 0.45, 0.10, 0.25],   # from EXPLAIN
        [0.15, 0.10, 0.10, 0.20, 0.45],   # from EXAMPLE
        [0.10, 0.30, 0.15, 0.10, 0.35],   # from AGREE
        [0.20, 0.20, 0.20, 0.20, 0.20],   # from ELABORATE
    ],
    "control": [
        [0.15, 0.55, 0.05, 0.15, 0.10],
        [0.50, 0.10, 0.15, 0.15, 0.10],
        [0.20, 0.30, 0.10, 0.30, 0.10],
        [0.30, 0.25, 0.10, 0.20, 0.15],
        [0.30, 0.30, 0.10, 0.20, 0.10],
    ],
}
START_DIST = {"treatment": [0.45, 0.20, 0.05, 0.10, 0.20],
              "control":   [0.55, 0.15, 0.05, 0.15, 0.10]}


def sample_code(probs):
    r = random.random()
    cum = 0.0
    for i, p in enumerate(probs):
        cum += p
        if r < cum:
            return i
    return len(probs) - 1


def speaker_for(turn_idx, last_speaker):
    # Loosely alternate A/B with 70% prob, otherwise repeat
    if random.random() < 0.7:
        return "B" if last_speaker == "A" else "A"
    return last_speaker


def generate():
    rows = []
    pid = 1
    for cond in ("treatment", "control"):
        for _ in range(N_PER_GROUP):
            uid = f"P{pid:03d}"
            n_turns = random.randint(*TURNS_RANGE)
            cur = sample_code(START_DIST[cond])
            speaker = "A"
            for t in range(1, n_turns + 1):
                row = {
                    "user_id": uid,
                    "cond": cond,
                    "turn_idx": t,
                    "speaker": speaker,
                    **{c: 0 for c in CODES},
                }
                row[CODES[cur]] = 1
                rows.append(row)
                cur = sample_code(TRANS[cond][cur])
                speaker = speaker_for(t + 1, speaker)
            pid += 1
    return rows


def main():
    rows = generate()
    out = Path(__file__).parent / "fake_dialogue_long.csv"
    fields = ["user_id", "cond", "turn_idx", "speaker"] + CODES
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    n_treat = sum(1 for r in rows if r["cond"] == "treatment")
    n_ctrl = sum(1 for r in rows if r["cond"] == "control")
    n_users = len({r["user_id"] for r in rows})
    print(f"[saved] {out}")
    print(f"        rows={len(rows)}  users={n_users}  "
          f"treatment_turns={n_treat}  control_turns={n_ctrl}")


if __name__ == "__main__":
    main()
