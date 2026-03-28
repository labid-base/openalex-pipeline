# labid-base / openalex-pipeline

Open pipeline for building LabID — an open knowledge graph of research laboratories. Fetches raw affiliation strings from OpenAlex, deduplicates them, runs NER via AffilGood, and prepares data for manual annotation in Label Studio.

## Repository structure

```
openalex-pipeline/          # Scripts to fetch and flatten OpenAlex data
  main.py                   # Fetch works from OpenAlex API → JSONL chunks
  convert_to_csv.py         # Flatten JSONL chunks → CSV (one row per authorship)
  extract_unique_raw_affiliations.py  # Deduplicate raw affiliation strings per chunk

LabNER/                     # NER fine-tuning pipeline for LAB / CENTER entities
  affilgood/                # AffilGood fork (NER + entity linking)
    scripts/
      run_no_nel_csv.py     # Run AffilGood NER (no NEL) on affiliation CSV
  scripts/
    extract_lab_spans.py    # Filter AffilGood output for lab/center spans → Label Studio

OpenAlex_Affilation_Dataset/
  2025-12-raw/              # Raw JSONL chunks from OpenAlex (gitignored)
  2025-12-unique/           # Per-chunk deduplicated affiliation CSVs (gitignored)
  2025-12-affilgood/        # AffilGood NER output (gitignored)
```

## Full pipeline

```
OpenAlex API
    ↓  main.py  (--year 2025 --month 12)
OpenAlex_Affilation_Dataset/2025-12-raw/
    works_2025_12_chunk_XXXX.jsonl          (71 chunks, 10,000 works each)

    ↓  extract_unique_raw_affiliations.py   (per-chunk deduplication)
OpenAlex_Affilation_Dataset/2025-12-unique/
    works_2025_12_chunk_XXXX.csv
    columns: work_id | raw_affiliation_string

    ↓  LabNER/affilgood/scripts/run_no_nel_csv.py
OpenAlex_Affilation_Dataset/2025-12-affilgood/
    affilgood_output.csv
    columns: work_id | raw_text | span_index | span_input |
             institutions | subunits | location_city | location_country |
             language | confidence

    ↓  LabNER/scripts/extract_lab_spans.py  (regex keyword filter)
OpenAlex_Affilation_Dataset/2025-12-affilgood/
    lab_spans.csv
    columns: work_id | raw_text | span_input | institutions | subunits

    ↓  Label Studio (LabNER project) — import lab_spans.csv directly
    ↓  Manual annotation: LAB / CENTER on span_input
    ↓  Fine-tune LabNER model (transfer learning from AffilGood weights)
```

## Usage

### 1. Fetch works from OpenAlex

```bash
# Single month
python openalex-pipeline/main.py \
  --mailto you@example.com \
  --year 2025 --month 12 \
  --output-dir OpenAlex_Affilation_Dataset/2025-12-raw

# Environment variable alternative
export OPENALEX_MAILTO=you@example.com
export OPENALEX_YEAR=2025
export OPENALEX_MONTH=12
export OPENALEX_OUTPUT_DIR=OpenAlex_Affilation_Dataset/2025-12-raw
python openalex-pipeline/main.py
```

Output: `works_2025_12_chunk_XXXX.jsonl` files, 10,000 works each.

### 2. Deduplicate affiliation strings

```bash
python openalex-pipeline/extract_unique_raw_affiliations.py \
  --input-dir  OpenAlex_Affilation_Dataset/2025-12-raw \
  --output-dir OpenAlex_Affilation_Dataset/2025-12-unique
```

Processes each chunk separately. Output: one CSV per chunk (`works_2025_12_chunk_XXXX.csv`), columns: `work_id`, `raw_affiliation_string`. `work_id` is the first work the string appeared in within that chunk.

### 3. Run AffilGood NER

Run per chunk, or concatenate unique CSVs first and run on the combined file.

```bash
cd LabNER/affilgood
python scripts/run_no_nel_csv.py \
  --input-csv  ../../OpenAlex_Affilation_Dataset/2025-12-unique/works_2025_12_chunk_0001.csv \
  --output-csv ../../OpenAlex_Affilation_Dataset/2025-12-affilgood/works_2025_12_chunk_0001.csv \
  --batch-size 256 \
  --progress-every 100
```

Output CSV columns: `work_id`, `raw_text`, `span_index`, `span_input`, `institutions`, `subunits`, `location_city`, `location_country`, `language`, `confidence`.

AffilGood runs two models internally:
- **Span model** (`affilgood-span-multilingual-v2`) — splits the raw string into sub-affiliation units
- **NER model** (`affilgood-ner-multilingual-v2`) — labels entities (ORG, SUBORG, CITY, COUNTRY) within each span

### 4. Extract lab/center spans for annotation

```bash
python LabNER/scripts/extract_lab_spans.py \
  --input-csv  OpenAlex_Affilation_Dataset/2025-12-affilgood/affilgood_output.csv \
  --output-csv OpenAlex_Affilation_Dataset/2025-12-affilgood/lab_spans.csv
```

Filters rows where `span_input` or `subunits` matches lab/center keywords (laboratory, research group, center, institute, facility, platform, unit, ...). Output CSV is ready for direct import into Label Studio.

Output columns: `work_id`, `raw_text`, `span_input`, `institutions`, `subunits`.

In Label Studio, set `span_input` as the annotatable text field. Annotators label the entity in the span as **LAB** or **CENTER**.

### 5. (Optional) Flatten to full authorship CSV

```bash
python openalex-pipeline/convert_to_csv.py \
  --input-dir  OpenAlex_Affilation_Dataset/2025-12-raw \
  --output-dir OpenAlex_Affilation_Dataset/2025-12-csv
```

One row per authorship, includes DOI, title, author ORCID, citation count, etc.

## convert_to_csv.py output columns

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
| `raw_affiliation_string` | Raw affiliation string |
| `institution_ids` | OpenAlex institution IDs (pipe-separated) |
| `institution_names` | OpenAlex institution names (pipe-separated) |
| `country_codes` | Country codes (pipe-separated) |

## Notes

- Data files (`.jsonl`, `.csv`) are excluded from version control via `.gitignore`.
- `convert_to_csv.py` filters out works with `cited_by_count > 2000` to exclude noise from highly-cited works with unusual affiliation patterns.
- AffilGood is run without entity linking (NEL disabled) — only NER span detection is used. Entity linking will be added after LabNER fine-tuning.
- The goal of LabNER is to extend AffilGood's entity schema with two new types: **LAB** (laboratory, research group, research unit, research team) and **CENTER** (institute, center, facility, platform).
