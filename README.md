# labid-base / openalex-pipeline

Fetches raw academic works from the [OpenAlex](https://openalex.org) API and extracts deduplicated affiliation strings. Output is published as a Kaggle dataset.

**Part of [LabID](https://github.com/labid-base)** — an open knowledge graph of research laboratories.

---

## Scripts

| Script | Input | Output |
|--------|-------|--------|
| `main.py` | OpenAlex API | JSONL chunks (10,000 works each) |
| `extract_unique_raw_affiliations.py` | JSONL chunks | Per-chunk CSV of unique affiliation strings |
| `convert_to_csv.py` | JSONL chunks | Full authorship CSV (one row per author) |

---

## Usage

### 1. Fetch works from OpenAlex

```bash
python main.py \
  --mailto you@example.com \
  --year 2025 --month 12 \
  --output-dir data/2025-12/raw
```

Or via environment variables:

```bash
export OPENALEX_MAILTO=you@example.com
export OPENALEX_YEAR=2025
export OPENALEX_MONTH=12
export OPENALEX_OUTPUT_DIR=data/2025-12/raw
python main.py
```

Output: `works_2025_12_chunk_XXXX.jsonl` files, 10,000 works per chunk.

### 2. Extract unique affiliation strings

```bash
python extract_unique_raw_affiliations.py \
  --input-dir  data/2025-12/raw \
  --output-dir data/2025-12/unique
```

Processes each chunk separately. Output: one CSV per chunk, columns: `work_id`, `raw_affiliation_string`. `work_id` is the first work the string appeared in within that chunk.

### 3. (Optional) Flatten to full authorship CSV

```bash
python convert_to_csv.py \
  --input-dir  data/2025-12/raw \
  --output-dir data/2025-12/csv
```

One row per authorship. Columns: `work_id`, `doi`, `title`, `type`, `language`, `primary_topic_id`, `primary_topic_name`, `cited_by_count`, `author_position`, `author_id`, `author_orcid`, `author_name`, `is_corresponding`, `raw_affiliation_string`, `institution_ids`, `institution_names`, `country_codes`.

---

## Dataset

Collected data is published on Kaggle:
**[emirhanserbest/openalex-affiliation-dataset](https://www.kaggle.com/datasets/emirhanserbest/openalex-affiliation-dataset)**

---

## Next step: NER

To run AffilGood NER on the unique affiliation strings and prepare annotation tasks for Label Studio, see:
**[labid-base/LabNER](https://github.com/labid-base/LabNER)**

---

## Notes

- Requires `has_raw_affiliation_strings:true` filter — works without affiliation strings are skipped.
- `convert_to_csv.py` excludes works with `cited_by_count > 2000` to filter noise from unusually high-citation entries.
- Data files (`.jsonl`, `.csv`) are excluded from version control via `.gitignore`.
