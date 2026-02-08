# Schema & Join Map

This dataset is **relational** (multiple linked tables). Use stable IDs to join:

- `doc_id` → documents ↔ chunks  
- `chunk_id` → chunks ↔ retrieval events  
- `run_id` → eval runs ↔ retrieval events  
- `scenario_id` → scenarios ↔ eval runs / retrieval events  
- `example_id` → per-question example (carried in eval runs + retrieval events)  
- `query_id` → stable query identifier (carried in eval runs + retrieval events)

## Mermaid ER-style overview

```mermaid
erDiagram
  RAG_CORPUS_DOCUMENTS ||--o{ RAG_CORPUS_CHUNKS : contains
  RAG_CORPUS_CHUNKS ||--o{ RAG_RETRIEVAL_EVENTS : retrieved
  RAG_QA_EVAL_RUNS ||--o{ RAG_RETRIEVAL_EVENTS : logs
  RAG_QA_SCENARIOS ||--o{ RAG_QA_EVAL_RUNS : defines
  RAG_QA_SCENARIOS ||--o{ RAG_RETRIEVAL_EVENTS : referenced

  RAG_CORPUS_DOCUMENTS {
    string doc_id PK
    string domain
  }
  RAG_CORPUS_CHUNKS {
    string chunk_id PK
    string doc_id FK
    text chunk_text
  }
  RAG_QA_SCENARIOS {
    string scenario_id PK
    string domain
    string task_type
  }
  RAG_QA_EVAL_RUNS {
    string run_id PK
    string scenario_id FK
    string example_id
    string query_id
    text query
    int is_correct
  }
  RAG_RETRIEVAL_EVENTS {
    string run_id FK
    string chunk_id FK
    int rank
    float retrieval_score
    int is_relevant
  }
```

## “Flat table” view

If you want a **single table** for analytics / dashboards, run:

```bash
python scripts/build_flat_table.py --data-dir data --out data/derived/flat_rag_events.parquet
```

This produces one row per **retrieved chunk per run**, with run-level labels replicated.
