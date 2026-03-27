# openalex-pipeline

OpenAlex'ten ham affiliation verisi çeken ve AffilGood'a hazır CSV formatına dönüştüren pipeline.

## Akış

```
main.py  →  works_YYYY_MM_chunk_XXXX.jsonl
    ↓
convert_to_csv.py  →  works_YYYY_MM_chunk_XXXX.csv
    ↓
AffilGood
```

## Kullanım

### 1. Ham veri çekme

```bash
# Tüm yıl
python main.py --mailto emirhan@unige.ch --year 2025 --output-dir data/jsonl

# Tek ay
python main.py --mailto emirhan@unige.ch --year 2025 --month 3 --output-dir data/jsonl
```

### 2. CSV'ye dönüştürme

```bash
python convert_to_csv.py --input-dir data/jsonl --output-dir data/csv
```

## Çıktı

Her CSV satırı bir `raw_affiliation_string`'e karşılık gelir. Sütunlar:

| Sütun | Açıklama |
|-------|----------|
| `work_id` | OpenAlex work ID |
| `raw_affiliation_string` | Ham affiliation string (AffilGood input) |
| `institution_ids` | OpenAlex kurum ID'leri |
| `institution_names` | OpenAlex kurum isimleri |
| `language` | Yayın dili |
| `primary_topic_name` | Birincil konu |

## Not

Veri dosyaları (`.jsonl`, `.csv`) `.gitignore` kapsamındadır, repoya push edilmez.
