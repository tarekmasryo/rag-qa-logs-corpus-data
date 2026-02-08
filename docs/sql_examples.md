# SQL Examples (RAG Ops Analytics)

These are **example queries** you can run after loading the CSVs into a SQL engine
(or after building the flattened table via `scripts/build_flat_table.py`).

Assume you have these tables:

- `rag_corpus_documents`
- `rag_corpus_chunks`
- `rag_qa_eval_runs`
- `rag_qa_scenarios`
- `rag_retrieval_events`

## 1) Accuracy by retrieval strategy

```sql
SELECT
  retrieval_strategy,
  AVG(is_correct) AS accuracy,
  COUNT(*) AS n_runs
FROM rag_qa_eval_runs
GROUP BY retrieval_strategy
ORDER BY accuracy DESC;
```

## 2) Cost vs accuracy (trade-off)

```sql
SELECT
  retrieval_strategy,
  AVG(total_cost_usd) AS avg_cost_usd,
  AVG(is_correct) AS accuracy,
  COUNT(*) AS n_runs
FROM rag_qa_eval_runs
GROUP BY retrieval_strategy
ORDER BY avg_cost_usd DESC;
```

## 3) Hallucination rate by domain

```sql
SELECT
  domain,
  AVG(hallucination_flag) AS hallucination_rate,
  COUNT(*) AS n_runs
FROM rag_qa_eval_runs
GROUP BY domain
ORDER BY hallucination_rate DESC;
```

## 4) Retrieval relevance @k (from retrieval events)

```sql
SELECT
  retrieval_strategy,
  AVG(CASE WHEN rank <= 5 THEN is_relevant ELSE NULL END) AS rel_at_5,
  AVG(CASE WHEN rank <= 10 THEN is_relevant ELSE NULL END) AS rel_at_10
FROM rag_retrieval_events
GROUP BY retrieval_strategy
ORDER BY rel_at_10 DESC;
```

## 5) Most expensive queries (debug slices)

```sql
SELECT
  run_id,
  query_id,
  total_cost_usd,
  total_latency_ms,
  retrieval_strategy,
  is_correct,
  hallucination_flag
FROM rag_qa_eval_runs
ORDER BY total_cost_usd DESC
LIMIT 50;
```
