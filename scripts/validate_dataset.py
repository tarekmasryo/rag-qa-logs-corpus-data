#!/usr/bin/env python3
"""Dataset validation for RAG QA Logs & Corpus (multi-table).

Usage:
    python scripts/validate_dataset.py --data-dir data

This script focuses on:
- Primary key uniqueness
- Foreign key integrity across tables
- Basic range / enum sanity checks
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd


def _fail(msg: str) -> None:
    raise AssertionError(msg)


def _read_csv(path: Path) -> pd.DataFrame:
    # Keep it simple and robust. We avoid aggressive dtype casting to reduce
    # accidental parse failures on mixed columns.
    return pd.read_csv(path, low_memory=False)


def _assert_columns(df: pd.DataFrame, required: Iterable[str], table: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        _fail(f"[{table}] missing required columns: {missing}")


def _assert_unique(df: pd.DataFrame, col: str, table: str) -> None:
    if col not in df.columns:
        _fail(f"[{table}] expected primary key column '{col}' but it is missing")
    dup = df[col].duplicated(keep=False)
    if dup.any():
        sample = df.loc[dup, col].astype(str).head(10).tolist()
        _fail(f"[{table}] primary key '{col}' has duplicates. Sample: {sample}")


def _assert_fk(
    child: pd.DataFrame,
    child_col: str,
    parent: pd.DataFrame,
    parent_col: str,
    child_table: str,
    parent_table: str,
) -> None:
    _assert_columns(child, [child_col], child_table)
    _assert_columns(parent, [parent_col], parent_table)

    child_vals = set(child[child_col].dropna().unique())
    parent_vals = set(parent[parent_col].dropna().unique())

    missing = child_vals - parent_vals
    if missing:
        sample = list(sorted(missing))[:10]
        _fail(
            f"[{child_table}] FK violation: '{child_col}' has {len(missing)} values not present in "
            f"[{parent_table}].{parent_col}. Sample: {sample}"
        )


def _assert_in_set(series: pd.Series, allowed: set[object], label: str) -> None:
    values = series.dropna().unique().tolist()
    bad = [v for v in values if v not in allowed]
    if bad:
        sample = [str(v) for v in bad[:10]]
        _fail(f"[{label}] contains unexpected values. Sample: {sample}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate dataset integrity for RAG QA Logs & Corpus"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Path to dataset data directory",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        _fail(f"Data directory not found: {data_dir.resolve()}")

    paths = {
        "rag_corpus_documents": data_dir / "rag_corpus_documents.csv",
        "rag_corpus_chunks": data_dir / "rag_corpus_chunks.csv",
        "rag_retrieval_events": data_dir / "rag_retrieval_events.csv",
        "rag_qa_eval_runs": data_dir / "rag_qa_eval_runs.csv",
        "rag_qa_scenarios": data_dir / "rag_qa_scenarios.csv",
    }

    for name, p in paths.items():
        if not p.exists():
            _fail(f"Missing required file for [{name}]: {p}")

    docs = _read_csv(paths["rag_corpus_documents"])
    chunks = _read_csv(paths["rag_corpus_chunks"])
    events = _read_csv(paths["rag_retrieval_events"])
    runs = _read_csv(paths["rag_qa_eval_runs"])
    scenarios = _read_csv(paths["rag_qa_scenarios"])

    # Primary keys
    _assert_unique(docs, "doc_id", "rag_corpus_documents")
    _assert_unique(chunks, "chunk_id", "rag_corpus_chunks")
    _assert_unique(runs, "example_id", "rag_qa_eval_runs")
    _assert_unique(scenarios, "scenario_id", "rag_qa_scenarios")

    # Foreign keys (joins)
    _assert_fk(chunks, "doc_id", docs, "doc_id", "rag_corpus_chunks", "rag_corpus_documents")
    _assert_fk(events, "chunk_id", chunks, "chunk_id", "rag_retrieval_events", "rag_corpus_chunks")
    _assert_fk(events, "example_id", runs, "example_id", "rag_retrieval_events", "rag_qa_eval_runs")
    _assert_fk(
        runs,
        "scenario_id",
        scenarios,
        "scenario_id",
        "rag_qa_eval_runs",
        "rag_qa_scenarios",
    )

    # Basic checks
    for table_name, df in [
        ("rag_retrieval_events", events),
        ("rag_qa_eval_runs", runs),
        ("rag_qa_scenarios", scenarios),
    ]:
        if "split" in df.columns:
            _assert_in_set(
                df["split"],
                {"train", "val", "test", "validation"},
                f"{table_name}.split",
            )

    # rank should be >= 1 if present
    if "rank" in events.columns:
        if (events["rank"].dropna() < 1).any():
            _fail("[rag_retrieval_events.rank] contains values < 1")

    # Boolean-like columns: accept 0/1 and True/False (and string variants)
    bool_allowed: set[object] = {0, 1, True, False, "0", "1", "True", "False", "true", "false"}

    bool_specs = [
        ("rag_corpus_documents", docs, ["is_active", "contains_tables"]),
        ("rag_qa_scenarios", scenarios, ["has_answer_in_corpus", "is_used_in_eval"]),
        (
            "rag_qa_eval_runs",
            runs,
            [
                "is_correct",
                "has_answer_in_corpus",
                "is_noanswer_probe",
                "has_relevant_in_top5",
                "has_relevant_in_top10",
                "answered_without_retrieval",
            ],
        ),
    ]
    for table_name, df, cols in bool_specs:
        for col in cols:
            if col in df.columns:
                _assert_in_set(df[col], bool_allowed, f"{table_name}.{col}")

    print("✅ Dataset validation passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as e:
        print(f"❌ {e}", file=sys.stderr)
        raise SystemExit(1)
