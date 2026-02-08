# Release Guide

This repository is primarily a **dataset** repo. Releases should be repeatable and auditable.

## Checklist

1) Validate dataset integrity

```bash
python scripts/validate_dataset.py --data-dir data
```

2) (Optional) Regenerate dataset stats

```bash
python scripts/summarize_dataset.py --data-dir data --out docs/dataset_stats.md
```

3) Update checksums for tracked data assets

```bash
python scripts/make_checksums.py --data-dir data --out checksums.sha256
```

4) Update `CHANGELOG.md` (keep entries short and specific)

5) Tag and release
