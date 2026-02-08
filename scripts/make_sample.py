#!/usr/bin/env python3
"""Create a small relational sample (keeps joins valid) for quick demos/tests.

Usage:
    python scripts/make_sample.py --data-dir data --out data/sample --n-events 5000 --seed 42

Sampling strategy:
- sample N rows from rag_retrieval_events (the fact table)
- keep dependent rows from runs, chunks, documents, scenarios
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

RAW_FILES = {
    "documents": "rag_corpus_documents.csv",
    "chunks": "rag_corpus_chunks.csv",
    "runs": "rag_qa_eval_runs.csv",
    "scenarios": "rag_qa_scenarios.csv",
    "events": "rag_retrieval_events.csv",
}


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=str, default="data")
    ap.add_argument("--out", type=str, default="data/sample")
    ap.add_argument("--n-events", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    docs = _read_csv(data_dir / RAW_FILES["documents"])
    chunks = _read_csv(data_dir / RAW_FILES["chunks"])
    runs = _read_csv(data_dir / RAW_FILES["runs"])
    scenarios = _read_csv(data_dir / RAW_FILES["scenarios"])
    events = _read_csv(data_dir / RAW_FILES["events"])

    n = min(args.n_events, len(events))
    events_s = events.sample(n=n, random_state=args.seed).copy()

    run_ids = set(events_s["run_id"].dropna().astype(str).unique())
    chunk_ids = set(events_s["chunk_id"].dropna().astype(str).unique())
    scenario_series = events_s.get("scenario_id", pd.Series(dtype=str))
    scenario_ids = set(scenario_series.dropna().astype(str).unique())

    runs_s = runs[runs["run_id"].astype(str).isin(run_ids)].copy()
    if "scenario_id" in runs_s.columns:
        scenario_ids |= set(runs_s["scenario_id"].dropna().astype(str).unique())

    chunks_s = chunks[chunks["chunk_id"].astype(str).isin(chunk_ids)].copy()
    if "doc_id" in chunks_s.columns:
        doc_ids = set(chunks_s["doc_id"].dropna().astype(str).unique())
    else:
        doc_ids = set()

    if "doc_id" in docs.columns:
        docs_s = docs[docs["doc_id"].astype(str).isin(doc_ids)].copy()
    else:
        docs_s = docs.iloc[0:0].copy()

    scenarios_s = scenarios[scenarios["scenario_id"].astype(str).isin(scenario_ids)].copy()

    # Write
    _write_csv(docs_s, out_dir / RAW_FILES["documents"])
    _write_csv(chunks_s, out_dir / RAW_FILES["chunks"])
    _write_csv(runs_s, out_dir / RAW_FILES["runs"])
    _write_csv(scenarios_s, out_dir / RAW_FILES["scenarios"])
    _write_csv(events_s, out_dir / RAW_FILES["events"])

    print("✅ Sample created:")
    print(f"- events:     {len(events_s):,}")
    print(f"- runs:       {len(runs_s):,}")
    print(f"- chunks:     {len(chunks_s):,}")
    print(f"- documents:  {len(docs_s):,}")
    print(f"- scenarios:  {len(scenarios_s):,}")
    print(f"Output dir: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
