# Changelog

- Initial release of **RAG QA Evaluation Logs & Corpus** dataset.
- Added 6 linked tables:
  - Document corpus (`rag_corpus_documents.csv`)
  - Chunk index (`rag_corpus_chunks.csv`)
  - QA evaluation runs (`rag_qa_eval_runs.csv`)
  - Retrieval events (`rag_retrieval_events.csv`)
  - Scenario templates (`rag_qa_scenarios.csv`)
  - Data dictionary (`rag_qa_data_dictionary.csv`)
- Included core supervision targets:
  - `is_correct`, `hallucination_flag`, `faithfulness_label`
- Included key RAG telemetry:
  - retrieval metrics, latency, token usage, and approximate cost.
