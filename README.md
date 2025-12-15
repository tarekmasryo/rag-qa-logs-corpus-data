# 🧠 RAG QA Logs & Corpus — Synthetic Multi-Table RAG Benchmark

**Author:** [Tarek Masryo](https://github.com/tarekmasryo) · [Kaggle](https://www.kaggle.com/tarekmasryo)

End-to-end **RAG QA telemetry dataset** modeling a production-style  
**Retrieval-Augmented Generation (RAG)** system from:

> **corpus → chunks → retrieval → QA runs → scenarios**

The repository contains:

- Six **linked CSV files** (documents, chunks, retrieval events, QA runs, scenarios, data dictionary).
- Example **notebooks** for EDA, RAG evaluation, meta-modeling, and guardrail design.

It is designed as an **ML-ready playground** for:

- RAG quality analysis  
- retrieval strategy evaluation  
- hallucination and risk modeling  
- latency & cost trade-off studies  
- dashboards and teaching materials  

---

## 🔐 Privacy & Synthetic Data

All records in this project are **fully synthetic but realistic** system logs and corpus metadata.

- No real users, customers, patients, or organisations are involved.  
- No personally identifiable information (PII) is present.  
- All IDs, queries, documents, and logs were **programmatically generated** to mimic realistic RAG system behaviour while preserving privacy.

This makes the dataset suitable for **research, teaching, prototyping, and dashboard design**, without depending on production logs.

---

## 🧩 Dataset Overview

| Component | Description |
|:--|:--|
| **Dataset** | 6 linked tables: documents, chunks, retrieval events, QA evaluation runs, QA scenarios, and a data dictionary. |
| **Targets** | `is_correct`, `hallucination_flag`, `faithfulness_label`. |
| **Intended workflows** | EDA · Retrieval strategy evaluation · RAG QA meta-modeling · Latency & cost analysis · Teaching. |
| **Primary focus** | Understand and predict RAG answer quality, hallucinations, latency, and cost from system-side signals. |

---

## 📂 Files in This Repository

### Data files (CSV)

- `rag_corpus_documents.csv`  
- `rag_corpus_chunks.csv`  
- `rag_qa_eval_runs.csv`  
- `rag_retrieval_events.csv`  
- `rag_qa_scenarios.csv`  
- `rag_qa_data_dictionary.csv`  

All files:

- use **snake_case** column names  
- are **tabular and ML-ready**  
- join via `doc_id`, `chunk_id`, `run_id`, `example_id`, `scenario_id`.

### Notebooks (example analysis)

You can place notebooks such as:

- `notebooks/RAG_QA_RAG_Ops_Command_Center_and_Strategy_Report.ipynb`  
- `notebooks/RAG_QA_System_Risk_and_Guardrails_Report.ipynb`  
- `notebooks/RAG_QA_Telemetry_Atlas_and_Scenario_Explorer.ipynb`  
- `notebooks/RAG_QA_Hallucination_and_Failure_Anatomy_Lab.ipynb`  

These notebooks demonstrate how to:

- explore the multi-table schema  
- analyse domains, tasks, and difficulty  
- relate retrieval metrics to correctness & hallucinations  
- build simple meta-models & guardrail policies.

*(File names are suggestions; adjust to match your actual repo layout.)*

---

## 📊 Dataset Summary

| Table                       | Rows   | Columns | Granularity                                          |
|:----------------------------|:-------|:--------|:-----------------------------------------------------|
| `rag_corpus_documents.csv`  | 658    | 19      | One row per document in the RAG corpus.             |
| `rag_corpus_chunks.csv`     | 5,237  | 6       | One row per text chunk derived from a document.     |
| `rag_qa_eval_runs.csv`      | 3,824  | 46      | One row per QA evaluation example.                  |
| `rag_retrieval_events.csv`  | 93,375 | 9       | One row per retrieved chunk per QA example.         |
| `rag_qa_scenarios.csv`      | 88     | 11      | One row per scenario-level QA template / use case.  |
| `rag_qa_data_dictionary.csv`| 91     | 5       | One row per column definition across all tables.    |

---

## 🧱 Table Groups & Themes

### 🧾 Corpus (Documents & Chunks)

#### `rag_corpus_documents.csv` — Documents

High-level description of the RAG knowledge base:

- **Domain**: e.g. `support_faq`, `hr_policies`, `product_docs`, `developer_docs`, `policies`,  
  `financial_reports`, `medical_guides`, `research_papers`, `customer_success`,  
  `data_platform_docs`, `mlops_docs`, `marketing_analytics`
- **Text metadata**: `title`, `source_type`, `language`
- **Size & structure**: `n_sections`, `n_tokens`, `n_chunks`, `avg_chunk_tokens`
- **Operational**: `created_at_utc`, `last_updated_at_utc`, `is_active`, `contains_tables`
- **Risk & access**: `pii_risk_level`, `security_tier`
- **Ownership & indexing**: `owner_team`, `embedding_model`, `search_index`, `top_keywords`

Use this table to analyse which document profiles and domains perform better or worse in RAG.

#### `rag_corpus_chunks.csv` — Chunks

What the retriever actually works with:

- `chunk_id` (unique) and `doc_id` (foreign key to documents)
- `domain` and `chunk_index` (0-based position inside the document)
- `estimated_tokens` (approximate length in tokens)
- `chunk_text` (the text passed to retrieval and ranking)

Documents + chunks together support analysis of **corpus composition**, **chunking strategy**, and how content structure affects downstream performance.

---

### 🎯 QA Evaluation Runs

`rag_qa_eval_runs.csv` captures each **question–answer attempt** and its system context.

**IDs & context**

- `example_id`, `run_id`, `domain`, `task_type`, `difficulty`
- `scenario_id` (link to scenario template)
- `query` — user-style question text
- `gold_answer` — reference answer
- `has_answer_in_corpus` — whether the corpus actually contains sufficient evidence

**Quality labels**

- `is_correct` — binary correctness flag  
- `correctness_label` — `correct` / `partial` / `incorrect`  
- `faithfulness_label` — `faithful` / `unfaithful` / `unknown`  
- `hallucination_flag` — binary hallucination signal  
- `user_feedback_label` — simplified user-style feedback  
- `supervising_judge_label` — synthetic “expert” assessment  
- `is_noanswer_probe` — deliberately unanswerable queries

**Retrieval metrics**

- `retrieval_strategy`, `chunking_strategy`
- `n_retrieved_chunks` (top-k depth actually logged)
- `top1_score`, `mean_retrieved_score`
- `recall_at_5`, `recall_at_10`, `mrr_at_10`
- `has_relevant_in_top5`, `has_relevant_in_top10`

**Latency & resources**

- `latency_ms_retrieval`, `latency_ms_generation`, `total_latency_ms`
- `used_long_context_window`, `context_window_tokens`

**Configuration & cost**

- `embedding_model`, `reranker_model`, `generator_model`
- `temperature`, `top_p`, `max_new_tokens`, `stop_reason`
- `answer_tokens`, `prompt_tokens`, `total_cost_usd`

**Supervision & linkage**

- `doc_ids_used`, `chunk_ids_used`
- `eval_mode`, `created_at_utc`

This table is the **primary source** for studying answer quality, hallucinations, latency, and cost — and for building **meta-models** on top of RAG telemetry.

---

### 📡 Retrieval Events

`rag_retrieval_events.csv` records **which chunks were retrieved** for each QA example.

- Keys: `run_id`, `example_id`, `chunk_id`
- Ranking: `rank` (1 = top result), `retrieval_score`
- Relevance: `is_relevant` (binary label per chunk)
- Convenience fields: `domain`, `difficulty`, `retrieval_strategy`

From this table, you can:

- Reconstruct the full retrieved list for any QA example  
- Study how rank and score relate to relevance and correctness  
- Compute custom metrics or simulate alternative top-k / threshold policies

---

### 📚 Scenario-Level QA Definitions

`rag_qa_scenarios.csv` provides **human-readable QA templates and use cases**:

- `scenario_id` — links to `rag_qa_eval_runs.scenario_id`
- `domain`, `primary_doc_id`
- Canonical `query` and `gold_answer`
- `difficulty_level` — easy / medium / hard
- `scenario_type` — e.g. factual QA, policy lookup, multi-hop reasoning, monitoring, compliance
- `use_case` — short description of the business or product scenario
- `has_answer_in_corpus` — whether the scenario is designed to be answerable
- `n_eval_examples`, `is_used_in_eval` — connection to QA evaluation runs

This table adds a **narrative layer** on top of the logs, useful for teaching, dashboards, and case studies.

---

### 📙 Data Dictionary

`rag_qa_data_dictionary.csv` documents every column across all tables:

- `table_name`
- `column_name`
- `dtype` — `int`, `float`, `bool`, `category`, `datetime`, or `text`
- `description` — short human-readable meaning
- `allowed_values` — expected values or ranges where applicable

Use this as a **single source of truth** for the schema when exploring the dataset or building models.

---

## ⚙️ Quick Start (Python)

```python
import pandas as pd

base_path = "path/to/data"  # update to your local path or Kaggle input folder

docs = pd.read_csv(f"{base_path}/rag_corpus_documents.csv")
chunks = pd.read_csv(f"{base_path}/rag_corpus_chunks.csv")
runs = pd.read_csv(f"{base_path}/rag_qa_eval_runs.csv")
retrieval = pd.read_csv(f"{base_path}/rag_retrieval_events.csv")
scenarios = pd.read_csv(f"{base_path}/rag_qa_scenarios.csv")
dictionary = pd.read_csv(f"{base_path}/rag_qa_data_dictionary.csv")

print(docs.shape, chunks.shape, runs.shape, retrieval.shape, scenarios.shape, dictionary.shape)
```

This is enough to start doing **EDA, metric computation, or baseline meta-modeling**.

---

## 🚀 Example Workflows

Some ideas for how to use this repository:

- **RAG Quality & Retrieval Analysis**
  - Compare retrieval strategies across domains and difficulty levels  
  - Relate `recall_at_k`, `mrr_at_10`, and `top1_score` to correctness and hallucinations  

- **Meta-Modeling & Risk Scoring**
  - Train models on `is_correct`, `hallucination_flag`, or `faithfulness_label`  
  - Use retrieval, latency, and configuration features as predictors  
  - Design risk scores for block / escalate / rerun policies  

- **Latency & Cost vs Quality**
  - Study how `total_latency_ms`, `context_window_tokens`, and `total_cost_usd` vary by domain, task, and difficulty  
  - Prototype “fast vs careful” modes for RAG systems  

- **Teaching & Dashboards**
  - Build notebooks or dashboards that:
    - Explain how a RAG system is wired end-to-end  
    - Show how retrieval & configuration choices impact quality, latency, and cost  
    - Visualise behaviour per domain, scenario type, or difficulty  

---

## ⚠️ Limitations

- All content, queries, and logs are **fully synthetic**; this is **not** a production dataset.  
- It should **not** be used to make clinical, financial, legal, or other safety-critical decisions.  
- Intended use: **research, teaching, benchmarking, and prototyping**.

---

## 📜 License & Attribution

- **Data type:** realistic synthetic RAG corpus and system logs (no real users or organisations).  
- **Intended use:** research, teaching, benchmarking, prototyping RAG systems.  
- **License:** **CC BY 4.0**.  
- **Author:** **Tarek Masryo**.

If you use this dataset in research, teaching materials, or open-source projects, please include a reference to:

> *“RAG QA Evaluation Logs & Corpus — Synthetic Multi-Table Benchmark” by Tarek Masryo*
