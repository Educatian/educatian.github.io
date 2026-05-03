"""
render_ona_kaleido.py - Render plotly JSON saved by the ona R template to PNG
via the kaleido 1.x Python API (Windows-safe; never downgrade to 0.2.1).

Usage:
    python render_ona_kaleido.py <input.json> <output.png> [width] [height]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import kaleido
    import plotly.graph_objects as go
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "[ona-skill] missing dep: %s\n"
        "Install with: pip install -U plotly kaleido\n" % exc
    )
    sys.exit(2)


def render(json_path: Path, png_path: Path,
           width: int = 1200, height: int = 750) -> None:
    raw = Path(json_path).read_text(encoding="utf-8")
    fig_dict = json.loads(raw)
    # plotly::plotly_json from R sometimes wraps in htmlwidget {x:{data,layout}}
    if "x" in fig_dict and isinstance(fig_dict["x"], dict):
        fig_dict = fig_dict["x"]
    if "data" not in fig_dict:
        raise ValueError(
            f"No 'data' key in JSON; top-level keys: {list(fig_dict.keys())}"
        )
    fig = go.Figure(
        data=fig_dict["data"],
        layout=fig_dict.get("layout", {}),
        skip_invalid=True,
    )
    kaleido.write_fig_sync(
        fig, str(png_path),
        opts={"format": "png", "width": int(width), "height": int(height)},
    )
    print(f"[saved] {png_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write(
            "Usage: python render_ona_kaleido.py <in.json> <out.png> "
            "[width] [height]\n"
        )
        sys.exit(2)
    in_json = Path(sys.argv[1])
    out_png = Path(sys.argv[2])
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 750
    render(in_json, out_png, width=w, height=h)
