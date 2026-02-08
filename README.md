# 🧠 RAG QA Logs & Corpus — Synthetic Multi-Table RAG Benchmark

A **production-style, privacy-safe** synthetic dataset that mimics telemetry from a real **Retrieval-Augmented Generation (RAG)** system — from **corpus → chunks → retrieval lists → evaluation outcomes**.

This repository ships a **joinable, ML-ready multi-table benchmark** for:
- 🧪 **RAG quality analysis** (correctness, faithfulness, hallucination)
- 🥊 **Retrieval strategy evaluation** (dense / bm25 / hybrid / rerank variants)
- 🧯 **Risk & meta-modeling** (predict failure/hallucination from telemetry)
- ⚡ **Latency & cost trade-offs** (tokens, ms, USD)
- 📊 Dashboards and teaching materials

✅ All records are **fully synthetic** — no real users, customers, patients, or company data.

---

## Table of Contents
- Overview
- Dataset Files
- Dataset Summary (Exact)
- Join Map (Schema)
- Quickstart (Python)
- Recommended Analyses / Notebook Ideas
- Data Dictionary Notes
- Limitations
- License & Attribution

---

## Overview

- **Total size:** **103,255 rows** across **6 linked CSV tables**
- **Main labels:** `is_correct`, `hallucination_flag`, `faithfulness_label`
- **Primary joins:** `doc_id`, `chunk_id`, `example_id`, `run_id`, `scenario_id`, `query_id`
- **Splits:** `train`, `val`, `test`
- **Domains (12):**  
  `support_faq`, `hr_policies`, `product_docs`, `developer_docs`,  
  `policies`, `financial_reports`, `medical_guides`, `research_papers`,  
  `customer_success`, `data_platform_docs`, `mlops_docs`, `marketing_analytics`
- **Retrieval strategies:** `dense`, `bm25`, `hybrid`, `dense_then_rerank`, `bm25_then_rerank`
- **Task types:**  
  `factoid`, `explanation`, `summarization`, `multi_hop`, `table_qa`,  
  `temporal_reasoning`, `comparison`, `instruction_following`

> 🧾 Note: `run_id` is a per-example request/trace identifier (not a single run spanning many examples).

---

## Dataset Files

This repository contains the following CSV files:

- `rag_corpus_documents.csv`
- `rag_corpus_chunks.csv`
- `rag_retrieval_events.csv`
- `rag_qa_eval_runs.csv`
- `rag_qa_scenarios.csv`
- `data_dictionary.csv` (canonical; a copy also lives in `docs/data_dictionary.csv`)

All files:
- use **snake_case** column names
- are **tidy tabular data** (one row per entity/event)
- can be joined through stable IDs

---

## Dataset Summary (Exact)

| File | Rows | Columns | Granularity |
|---|---:|---:|---|
| `rag_corpus_documents.csv` | 658 | 19 | One row per document in the corpus |
| `rag_corpus_chunks.csv` | 5,237 | 6 | One row per chunk derived from a document |
| `rag_retrieval_events.csv` | 93,375 | 12 | One row per retrieved chunk per example (rank/score/relevance) |
| `rag_qa_eval_runs.csv` | 3,824 | 49 | One row per QA evaluation example (quality + cost + latency + config) |
| `rag_qa_scenarios.csv` | 62 | 13 | One row per scenario template / use case |
| `data_dictionary.csv` | 99 | 5 | One row per column definition across all tables |

---

## 🔗 Join Map (Schema)

### Documents → Chunks
- `rag_corpus_documents.doc_id = rag_corpus_chunks.doc_id`

### Retrieval Events → Chunks
- `rag_retrieval_events.chunk_id = rag_corpus_chunks.chunk_id`

### Eval Runs → Retrieval Events
- `rag_qa_eval_runs.example_id = rag_retrieval_events.example_id`  
  (also `run_id`, `scenario_id`, `query_id`, `split` are available for consistency checks)

### Eval Runs → Scenarios
- `rag_qa_eval_runs.scenario_id = rag_qa_scenarios.scenario_id`  
  (and `query_id`)

---

## 🚀 Quickstart (Python)

### Install
```bash
pip install pandas
```

### Load data
```python
import pandas as pd

docs = pd.read_csv("data/rag_corpus_documents.csv")
chunks = pd.read_csv("data/rag_corpus_chunks.csv")
events = pd.read_csv("data/rag_retrieval_events.csv")
runs = pd.read_csv("data/rag_qa_eval_runs.csv")
scenarios = pd.read_csv("data/rag_qa_scenarios.csv")

print(docs.shape, chunks.shape, events.shape, runs.shape, scenarios.shape)
```

### Example join: runs → retrieval events → chunks → docs
```python
df = (
    runs.merge(events, on="example_id", how="left", suffixes=("", "_evt"))
        .merge(
            chunks[["chunk_id", "doc_id", "domain", "chunk_index", "estimated_tokens"]],
            on="chunk_id",
            how="left",
        )
        .merge(
            docs[["doc_id", "domain", "title", "source_type", "pii_risk_level", "security_tier"]],
            on="doc_id",
            how="left",
            suffixes=("", "_doc"),
        )
)

df.head()
```

### Quick metrics: accuracy + hallucination rate by retrieval strategy
```python
by_strategy = (
    runs.groupby("retrieval_strategy", dropna=False)
        .agg(
            n=("example_id", "count"),
            accuracy=("is_correct", "mean"),
            hallucination_rate=("hallucination_flag", "mean"),
            avg_total_latency_ms=("total_latency_ms", "mean"),
            avg_cost_usd=("total_cost_usd", "mean"),
        )
        .sort_values("n", ascending=False)
)

by_strategy
```

---

## 🎯 Recommended Analyses / Notebook Ideas

### 1) 🥊 Retrieval strategy showdown
- Compare `dense` vs `bm25` vs `hybrid` vs rerank variants
- Analyze quality vs `recall_at_5`, `recall_at_10`, `mrr_at_10`, `top1_score`
- Segment results by domain + difficulty

### 2) 🧯 Hallucination & failure anatomy
- Where hallucinations happen (domain/task/difficulty)
- Link failures to missing relevance signals:
  - `has_relevant_in_top5`, `has_relevant_in_top10`
  - `recall_at_10`, `mrr_at_10`

### 3) 📈 Risk scoring / meta-modeling
- Predict `hallucination_flag` or `is_correct` using:
  - retrieval evidence (scores, ranks, recall/mrr)
  - system config (models/params)
  - latency/cost signals

### 4) ⚡ Cost & latency policies
- Build routing rules like:
  - “fast vs careful” modes based on `total_latency_ms`, `total_cost_usd`
  - “escalate if risk is high” using a risk score model

### 5) 🚫 No-answer behavior (abstention)
- Use `is_noanswer_probe` and `has_answer_in_corpus`
- Evaluate abstention rules based on retrieval evidence

---

## 📘 Data Dictionary Notes

`data_dictionary.csv` contains:
- `table_name`, `column_name`, `dtype`, `description`, `allowed_values`

**Important:** `table_name` may use logical names (e.g., `rag_qa_eval_runs`, `rag_qa_scenarios`) even though the actual filenames are:
- `rag_qa_eval_runs.csv`
- `rag_qa_scenarios.csv`

If you want strict 1:1 naming:
- either rename the CSV files to match the dictionary, **or**
- update `table_name` values inside `data_dictionary.csv` to match your filenames.

---

## 🔐 Privacy & Synthetic Data

- No real users/customers/patients/organizations
- No PII
- All IDs, queries, documents, and telemetry are synthetic and programmatically generated

Safe for public release, teaching, and demos without exposing production logs.

---

## ⚠️ Limitations

- This dataset is **synthetic**; it mimics production telemetry but is not real production data.
- Text in `rag_corpus_chunks.chunk_text` may be **more templated / less diverse** than real-world corpora.
- Synthetic telemetry is designed to be realistic, but it won’t cover every edge case found in production systems.
- Not intended for high-stakes clinical, legal, or financial decision-making.

---

## 📜 License & Attribution

- **License:** CC BY 4.0 (Attribution required)
- Suggested citation:  
  *“RAG QA Logs & Corpus — Synthetic Multi-Table RAG Benchmark” — Tarek Masryo*
