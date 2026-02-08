#!/usr/bin/env python3
"""Dataset validation for RAG QA Logs & Corpus (multi-table).

Usage:
    python scripts/validate_dataset.py --data-dir data

This script focuses on:
- Primary key uniqueness
- Foreign key integrity across tables
- Enum / boolean sanity checks
- Basic range checks for cost/latency/metrics
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Sequence

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


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _assert_columns(df: pd.DataFrame, cols: Sequence[str], table: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    _assert(not missing, f"{table}: missing required columns: {missing}")


def _assert_unique(df: pd.DataFrame, cols: Sequence[str], table: str) -> None:
    dup = df.duplicated(list(cols), keep=False)
    if dup.any():
        sample = df.loc[dup, list(cols)].head(5).to_dict("records")
        raise AssertionError(f"{table}: duplicate key {list(cols)}. Sample: {sample}")


def _assert_not_null(df: pd.DataFrame, cols: Sequence[str], table: str) -> None:
    for c in cols:
        if c in df.columns:
            n = int(df[c].isna().sum())
            _assert(n == 0, f"{table}.{c}: contains {n} nulls")


def _assert_fk(
    child: pd.DataFrame,
    child_col: str,
    parent: pd.DataFrame,
    parent_col: str,
    name: str,
) -> None:
    if child_col not in child.columns or parent_col not in parent.columns:
        return
    child_vals = set(child[child_col].dropna().astype(str).unique())
    parent_vals = set(parent[parent_col].dropna().astype(str).unique())
    missing = sorted(list(child_vals - parent_vals))[:10]
    _assert(len(missing) == 0, f"{name}: missing FK targets (showing up to 10): {missing}")


def _assert_in_set(series: pd.Series, allowed: Iterable, name: str) -> None:
    s = series.dropna()
    bad = s[~s.isin(list(allowed))]
    if not bad.empty:
        sample = bad.head(10).tolist()
        raise AssertionError(f"{name}: values outside allowed set. Sample: {sample}")


def _assert_range(series: pd.Series, lo: float | None, hi: float | None, name: str) -> None:
    s = pd.to_numeric(series, errors="coerce")
    s = s.dropna()
    if s.empty:
        return
    if lo is not None:
        bad = s[s < lo]
        if not bad.empty:
            raise AssertionError(f"{name}: values < {lo}. Sample: {bad.head(10).tolist()}")
    if hi is not None:
        bad = s[s > hi]
        if not bad.empty:
            raise AssertionError(f"{name}: values > {hi}. Sample: {bad.head(10).tolist()}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=str, default="data", help="Directory with dataset CSVs")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)

    documents = _read(data_dir / FILES["documents"])
    chunks = _read(data_dir / FILES["chunks"])
    runs = _read(data_dir / FILES["runs"])
    scenarios = _read(data_dir / FILES["scenarios"])
    events = _read(data_dir / FILES["events"])

    # Required columns
    _assert_columns(documents, ["doc_id"], "rag_corpus_documents")
    _assert_columns(chunks, ["chunk_id", "doc_id"], "rag_corpus_chunks")
    _assert_columns(scenarios, ["scenario_id"], "rag_qa_scenarios")
    _assert_columns(
        runs,
        ["run_id", "scenario_id", "example_id", "query_id"],
        "rag_qa_eval_runs",
    )
    _assert_columns(
        events,
        ["run_id", "chunk_id", "rank", "is_relevant"],
        "rag_retrieval_events",
    )

    # PK uniqueness
    _assert_unique(documents, ["doc_id"], "rag_corpus_documents")
    _assert_unique(chunks, ["chunk_id"], "rag_corpus_chunks")
    _assert_unique(scenarios, ["scenario_id"], "rag_qa_scenarios")
    _assert_unique(runs, ["run_id"], "rag_qa_eval_runs")
    _assert_unique(events, ["run_id", "chunk_id", "rank"], "rag_retrieval_events")

    # Not-null policy (keys)
    _assert_not_null(documents, ["doc_id"], "rag_corpus_documents")
    _assert_not_null(chunks, ["chunk_id", "doc_id"], "rag_corpus_chunks")
    _assert_not_null(scenarios, ["scenario_id"], "rag_qa_scenarios")
    _assert_not_null(
        runs,
        ["run_id", "scenario_id", "example_id", "query_id"],
        "rag_qa_eval_runs",
    )
    _assert_not_null(events, ["run_id", "chunk_id", "rank"], "rag_retrieval_events")

    # Foreign keys
    _assert_fk(chunks, "doc_id", documents, "doc_id", "chunks.doc_id -> documents.doc_id")
    _assert_fk(
        runs,
        "scenario_id",
        scenarios,
        "scenario_id",
        "runs.scenario_id -> scenarios.scenario_id",
    )
    _assert_fk(events, "run_id", runs, "run_id", "events.run_id -> runs.run_id")
    _assert_fk(events, "chunk_id", chunks, "chunk_id", "events.chunk_id -> chunks.chunk_id")
    if "scenario_id" in events.columns:
        _assert_fk(
            events,
            "scenario_id",
            scenarios,
            "scenario_id",
            "events.scenario_id -> scenarios.scenario_id",
        )

    # Enums / booleans
    bool_allowed = {0, 1}
    for table_name, df in [
        ("rag_qa_eval_runs", runs),
        ("rag_retrieval_events", events),
    ]:
        for col in [
            "is_correct",
            "hallucination_flag",
            "has_answer_in_corpus",
            "is_noanswer_probe",
            "answered_without_retrieval",
            "is_relevant",
        ]:
            if col in df.columns:
                s = pd.to_numeric(df[col], errors="coerce")
                _assert_in_set(s, bool_allowed, f"{table_name}.{col}")

    if "split" in events.columns:
        _assert_in_set(events["split"], {"train", "val", "test"}, "rag_retrieval_events.split")

    # Range checks
    if "rank" in events.columns:
        _assert_range(events["rank"], 1, None, "rag_retrieval_events.rank")

    if "retrieval_score" in events.columns:
        # allow negative scores for some retrievers, so only check "not all non-finite"
        finite = events["retrieval_score"].replace(
            [float("inf"), -float("inf")],
            pd.NA,
        )
        _assert(
            finite.notna().any(),
            "rag_retrieval_events.retrieval_score: all non-finite/NaN?",
        )

    for col in ["total_latency_ms", "retrieval_latency_ms", "generation_latency_ms"]:
        if col in runs.columns:
            _assert_range(runs[col], 0.0, None, f"rag_qa_eval_runs.{col}")

    if "total_cost_usd" in runs.columns:
        _assert_range(runs["total_cost_usd"], 0.0, None, "rag_qa_eval_runs.total_cost_usd")

    for col in ["recall_at_k", "mrr_at_10", "faithfulness_score"]:
        if col in runs.columns:
            _assert_range(runs[col], 0.0, 1.0, f"rag_qa_eval_runs.{col}")

    # Text sanity
    if "chunk_text" in chunks.columns:
        empty = (chunks["chunk_text"].astype(str).str.len() == 0).sum()
        _assert(int(empty) == 0, "rag_corpus_chunks.chunk_text: empty strings present")

    if "query" in runs.columns:
        empty = (runs["query"].astype(str).str.len() == 0).sum()
        _assert(int(empty) == 0, "rag_qa_eval_runs.query: empty strings present")

    print("✅ Dataset validation passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as e:
        print(f"❌ {e}", file=sys.stderr)
        raise SystemExit(1)
