# openalex-pipeline

Fetches raw affiliation data from OpenAlex and converts it to CSV format for AffilGood input.

## Pipeline

```
main.py  →  works_YYYY_MM_chunk_XXXX.jsonl
    ↓
convert_to_csv.py  →  works_YYYY_MM_chunk_XXXX.csv
    ↓
AffilGood
```

## Usage

### 1. Fetch works

```bash
# Full year
python main.py --mailto emirhan@unige.ch --year 2025 --output-dir data/jsonl

# Single month
python main.py --mailto emirhan@unige.ch --year 2025 --month 3 --output-dir data/jsonl
```

### 2. Convert to CSV

```bash
python convert_to_csv.py --input-dir data/jsonl --output-dir data/csv
```

## Output columns

Each CSV row corresponds to one `raw_affiliation_string`. Columns:

| Column | Description |
|--------|-------------|
| `work_id` | OpenAlex work ID |
| `doi` | DOI |
| `title` | Paper title |
| `type` | Publication type (article, preprint, etc.) |
| `language` | Publication language |
| `primary_topic_id` | Primary topic ID |
| `primary_topic_name` | Primary topic name |
| `cited_by_count` | Citation count |
| `author_position` | first / middle / last |
| `author_id` | OpenAlex author ID |
| `author_orcid` | Author ORCID (if available) |
| `author_name` | Author name |
| `is_corresponding` | Corresponding author flag |
| `raw_affiliation_string` | Raw affiliation string (AffilGood input) |
| `institution_ids` | OpenAlex institution IDs |
| `institution_names` | OpenAlex institution names |
| `country_codes` | Country codes |

## Notes

Data files (`.jsonl`, `.csv`) are excluded from version control via `.gitignore`.
