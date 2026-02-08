#!/usr/bin/env python3
"""Build a single "flat" table for analytics (one row per retrieved chunk per run).

Usage:
    python scripts/build_flat_table.py --data-dir data --out data/derived/flat_rag_events.parquet

The output is convenient for dashboards and quick EDA:
- joins retrieval events with run-level labels
- attaches chunk + document metadata
- attaches scenario metadata
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


def _ensure_parent(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory with dataset CSVs",
    )
    ap.add_argument(
        "--out",
        type=str,
        default="data/derived/flat_rag_events.parquet",
        help="Output file path",
    )
    ap.add_argument(
        "--format",
        type=str,
        default="auto",
        choices=["auto", "parquet", "csv"],
        help="Output format. auto=parquet if available else csv",
    )
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out_path = Path(args.out)

    docs = _read_csv(data_dir / RAW_FILES["documents"])
    chunks = _read_csv(data_dir / RAW_FILES["chunks"])
    runs = _read_csv(data_dir / RAW_FILES["runs"])
    scenarios = _read_csv(data_dir / RAW_FILES["scenarios"])
    events = _read_csv(data_dir / RAW_FILES["events"])

    # Core joins
    df = events.merge(
        runs,
        on="run_id",
        how="left",
        suffixes=("", "_run"),
        validate="m:1",
    )
    df = df.merge(
        chunks,
        on="chunk_id",
        how="left",
        suffixes=("", "_chunk"),
        validate="m:1",
    )
    if "doc_id" in df.columns and "doc_id" in docs.columns:
        df = df.merge(
            docs,
            on="doc_id",
            how="left",
            suffixes=("", "_doc"),
            validate="m:1",
        )

    # scenario_id can appear in multiple tables; prefer run-level if duplicated
    if "scenario_id" in df.columns and "scenario_id" in scenarios.columns:
        df = df.merge(
            scenarios,
            on="scenario_id",
            how="left",
            suffixes=("", "_scenario"),
            validate="m:1",
        )

    # Simple derived features
    if "total_latency_ms" in df.columns:
        df["latency_bucket"] = pd.cut(
            df["total_latency_ms"],
            bins=[-0.1, 250, 500, 1000, 2000, 5000, float("inf")],
            labels=["<=250", "251-500", "501-1000", "1001-2000", "2001-5000", ">5000"],
        )
    if "total_cost_usd" in df.columns:
        df["cost_bucket"] = pd.cut(
            df["total_cost_usd"],
            bins=[-0.000001, 0.001, 0.01, 0.05, 0.1, 0.25, float("inf")],
            labels=[
                "<=0.001",
                "0.001-0.01",
                "0.01-0.05",
                "0.05-0.1",
                "0.1-0.25",
                ">0.25",
            ],
        )

    _ensure_parent(out_path)

    fmt = args.format
    if fmt == "auto":
        fmt = "parquet"
        try:
            import pyarrow  # noqa: F401
        except Exception:
            fmt = "csv"

    if fmt == "parquet":
        df.to_parquet(out_path, index=False)
        print(f"✅ Wrote parquet: {out_path}  (rows={len(df):,}, cols={df.shape[1]:,})")
    else:
        csv_out = out_path.with_suffix(".csv")
        df.to_csv(csv_out, index=False)
        print(f"✅ Wrote csv: {csv_out}  (rows={len(df):,}, cols={df.shape[1]:,})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
