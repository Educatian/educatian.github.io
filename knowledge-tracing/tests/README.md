# Knowledge Tracing smoke tests

These scripts are the reproducibility backbone for the guide.

- `test_pybkt_python.py`: fits `pyBKT` on the toy long dataframe and writes JSON output.
- `test_pykt_dkt_forward.py`: runs a minimal DKT forward pass with `pykt-toolkit`.
- `test_bkt_r.R`: fits the CRAN `BKT` package on the same toy long dataframe.
- `test_lkt_r.R`: fits `LKT()` on a minimal dataset and captures a known failure mode for `buildLKTModel()`.

Outputs are written to `tests/results/`.
