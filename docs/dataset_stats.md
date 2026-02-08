# Dataset Stats
- **Total rows:** **103,156** across 5 data tables (+ data dictionary)
## Table sizes
| Table | Rows |
|---|---:|
| rag_corpus_documents | 658 |
| rag_corpus_chunks | 5,237 |
| rag_qa_scenarios | 62 |
| rag_qa_eval_runs | 3,824 |
| rag_retrieval_events | 93,375 |

## Labels & quality signals
- **Accuracy (mean is_correct):** 74.40%
- **Hallucination rate (mean hallucination_flag):** 19.01%

## Retrieval relevance @k
- **rel@5 (mean is_relevant where rank<=5):** 70.05%
- **rel@10 (mean is_relevant where rank<=10):** 73.07%

## Cost percentiles (USD)
| p50 | p90 | p95 | p99 |
|---:|---:|---:|---:|
| 0.000235 | 0.003508 | 0.004360 | 0.005813 |

## Latency percentiles (ms)
| p50 | p90 | p95 | p99 |
|---:|---:|---:|---:|
| 859.00 | 1629.70 | 1849.85 | 2204.08 |

## Top retrieval strategies
| retrieval_strategy | count |
|---|---:|
| dense_then_rerank | 808 |
| dense | 783 |
| bm25 | 765 |
| bm25_then_rerank | 741 |
| hybrid | 727 |

## Top domains (runs)
| domain | count |
|---|---:|
| financial_reports | 771 |
| developer_docs | 737 |
| hr_policies | 598 |
| medical_guides | 471 |
| product_docs | 362 |
| policies | 346 |
| support_faq | 275 |
| research_papers | 264 |
