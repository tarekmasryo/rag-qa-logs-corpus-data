# Changelog

## [1.0.2] - 2026-02-08
### Fixed
- Ruff/CI lint issues in `scripts/validate_dataset.py` (import sorting + line length).
- Removed accidental `__pycache__` artifact; added `.gitignore` to prevent reintroduction.

## [1.0.1] - 2026-02-08
### Added
- Canonical table-aligned filenames (`rag_qa_eval_runs.csv`, `rag_qa_scenarios.csv`).
- Dataset validation script (`scripts/validate_dataset.py`) + CI workflow (`.github/workflows/data-quality.yml`).
- Root `data_dictionary.csv` (canonical copy) and `checksums.sha256` for integrity verification.
- `CITATION.cff` for citation metadata.

## [1.0.0] - 2026-02-08
### Initial release
- Multi-table dataset: corpus documents, chunks, retrieval events, eval runs, scenarios.
- Data dictionary and join map.
