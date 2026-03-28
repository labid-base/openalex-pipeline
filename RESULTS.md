# Pipeline Results

Run statistics for each processed dataset batch.

---

## 2025-12 (December 2025)

**Date processed:** 2026-03-28

### Step 1 — Fetch from OpenAlex (`main.py`)

| Metric | Value |
|--------|-------|
| Filter | `publication_year:2025, from_publication_date:2025-12-01, to_publication_date:2025-12-31, has_raw_affiliation_strings:true` |
| Chunk size | 10,000 works |
| Chunks produced | 71 |
| Output directory | `OpenAlex_Affilation_Dataset/2025-12-raw/` |

### Step 2 — Deduplication (`extract_unique_raw_affiliations.py`)

| Metric | Value |
|--------|-------|
| Works scanned | 704,702 |
| Total raw affiliation entries | 3,595,056 |
| Unique raw affiliation strings | 1,263,694 |
| Deduplication ratio | ~65% reduction |
| Output file | `OpenAlex_Affilation_Dataset/2025-12-unique/raw_affiliation_unique.csv` |
| Output columns | `work_id`, `raw_affiliation_string` |

### Step 3 — AffilGood NER (`run_no_nel_csv.py`)

| Metric | Value |
|--------|-------|
| Status | Pending |
| Input | `OpenAlex_Affilation_Dataset/2025-12-unique/raw_affiliation_unique.csv` (1,263,694 rows) |
| Output directory | `OpenAlex_Affilation_Dataset/2025-12-affilgood/` |

### Step 4 — Label Studio upload

| Metric | Value |
|--------|-------|
| Status | Pending |
| Filter | Regex keyword filter (lab, laboratory, research group, center, institute, ...) |
| Project | LabNER (ID: 3) at https://label.labra.com.tr |

---

## 2025-11 (November 2025)

**Date processed:** 2026-03 (earlier session)

### Step 2 — Deduplication

| Metric | Value |
|--------|-------|
| JSONL chunks | 82 |
| Unique raw affiliation strings | 51,698 |
| Output file | `LabNER/raw_affiliation_unique.csv` |

### Step 3 — AffilGood NER

| Metric | Value |
|--------|-------|
| Input rows | 51,698 |
| Output rows | 54,397 |
| Rows with SUBORG entity | 40,969 |
| SUBORGs matching lab keywords | 4,542 |
| Standalone ORGs matching lab keywords | 956 |
| Output file | `LabNER/affilgood_no_nel_output.csv` |
