#!/usr/bin/env python3
"""Generate a short dataset stats report (Markdown).

Usage:
    python scripts/summarize_dataset.py --data-dir data --out docs/dataset_stats.md
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import pandas as pd

FILES = {
    "documents": "rag_corpus_documents.csv",
    "chunks": "rag_corpus_chunks.csv",
    "runs": "rag_qa_eval_runs.csv",
    "scenarios": "rag_qa_scenarios.csv",
    "events": "rag_retrieval_events.csv",
}


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _pct(x: float) -> str:
    return f"{100.0 * x:.2f}%"


def _p(df: pd.DataFrame, col: str, qs=(0.5, 0.9, 0.95, 0.99)) -> Dict[str, float]:
    s = df[col].dropna()
    if s.empty:
        return {}
    return {f"p{int(q * 100):02d}": float(s.quantile(q)) for q in qs}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=str, default="data")
    ap.add_argument("--out", type=str, default="docs/dataset_stats.md")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    docs = _read(data_dir / FILES["documents"])
    chunks = _read(data_dir / FILES["chunks"])
    runs = _read(data_dir / FILES["runs"])
    scenarios = _read(data_dir / FILES["scenarios"])
    events = _read(data_dir / FILES["events"])

    # Headline counts
    total_rows = len(docs) + len(chunks) + len(runs) + len(scenarios) + len(events)

    # Key distributions
    by_strategy = runs["retrieval_strategy"].value_counts(dropna=False)
    by_domain = runs["domain"].value_counts(dropna=False).head(20)

    acc = float(runs["is_correct"].mean()) if "is_correct" in runs.columns else float("nan")
    hall = (
        float(runs["hallucination_flag"].mean())
        if "hallucination_flag" in runs.columns
        else float("nan")
    )

    cost_ps = _p(runs, "total_cost_usd") if "total_cost_usd" in runs.columns else {}
    lat_ps = _p(runs, "total_latency_ms") if "total_latency_ms" in runs.columns else {}

    # Retrieval relevance @k from events
    has_rank_rel = {"rank", "is_relevant"} <= set(events.columns)
    if has_rank_rel:
        rel_at_5 = float(events.loc[events["rank"] <= 5, "is_relevant"].mean())
        rel_at_10 = float(events.loc[events["rank"] <= 10, "is_relevant"].mean())
    else:
        rel_at_5 = float("nan")
        rel_at_10 = float("nan")

    md = []
    md.append("# Dataset Stats\n")
    md.append(f"- **Total rows:** **{total_rows:,}** across 5 data tables (+ data dictionary)\n")
    md.append("## Table sizes\n")
    md.append("| Table | Rows |\n|---|---:|\n")
    md.append(f"| rag_corpus_documents | {len(docs):,} |\n")
    md.append(f"| rag_corpus_chunks | {len(chunks):,} |\n")
    md.append(f"| rag_qa_scenarios | {len(scenarios):,} |\n")
    md.append(f"| rag_qa_eval_runs | {len(runs):,} |\n")
    md.append(f"| rag_retrieval_events | {len(events):,} |\n")

    md.append("\n## Labels & quality signals\n")
    if not pd.isna(acc):
        md.append(f"- **Accuracy (mean is_correct):** {_pct(acc)}\n")
    if not pd.isna(hall):
        md.append(f"- **Hallucination rate (mean hallucination_flag):** {_pct(hall)}\n")

    md.append("\n## Retrieval relevance @k\n")
    if not pd.isna(rel_at_5):
        md.append(f"- **rel@5 (mean is_relevant where rank<=5):** {_pct(rel_at_5)}\n")
    if not pd.isna(rel_at_10):
        md.append(f"- **rel@10 (mean is_relevant where rank<=10):** {_pct(rel_at_10)}\n")

    if cost_ps:
        p50 = cost_ps.get("p50", float("nan"))
        p90 = cost_ps.get("p90", float("nan"))
        p95 = cost_ps.get("p95", float("nan"))
        p99 = cost_ps.get("p99", float("nan"))

        md.append("\n## Cost percentiles (USD)\n")
        md.append("| p50 | p90 | p95 | p99 |\n|---:|---:|---:|---:|\n")
        md.append(f"| {p50:.6f} | {p90:.6f} | {p95:.6f} | {p99:.6f} |\n")

    if lat_ps:
        p50 = lat_ps.get("p50", float("nan"))
        p90 = lat_ps.get("p90", float("nan"))
        p95 = lat_ps.get("p95", float("nan"))
        p99 = lat_ps.get("p99", float("nan"))

        md.append("\n## Latency percentiles (ms)\n")
        md.append("| p50 | p90 | p95 | p99 |\n|---:|---:|---:|---:|\n")
        md.append(f"| {p50:.2f} | {p90:.2f} | {p95:.2f} | {p99:.2f} |\n")

    md.append("\n## Top retrieval strategies\n")
    md.append("| retrieval_strategy | count |\n|---|---:|\n")
    for k, v in by_strategy.items():
        md.append(f"| {k} | {int(v):,} |\n")

    md.append("\n## Top domains (runs)\n")
    md.append("| domain | count |\n|---|---:|\n")
    for k, v in by_domain.items():
        md.append(f"| {k} | {int(v):,} |\n")

    out_path.write_text("".join(md), encoding="utf-8")
    print(f"✅ Wrote stats: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
