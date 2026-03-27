import json
import csv
import glob
import os
import argparse

CITATION_THRESHOLD = 2000

FIELDNAMES = [
    "work_id",
    "doi",
    "title",
    "type",
    "language",
    "primary_topic_id",
    "primary_topic_name",
    "cited_by_count",
    "author_position",
    "author_id",
    "author_orcid",
    "author_name",
    "is_corresponding",
    "raw_affiliation_string",
    "institution_ids",
    "institution_names",
    "country_codes",
]


def extract_rows(work):
    rows = []

    topic = work.get("primary_topic") or {}
    base = {
        "work_id":             work.get("id", ""),
        "doi":                 work.get("doi", ""),
        "title":               work.get("title", ""),
        "type":                work.get("type", ""),
        "language":            work.get("language", ""),
        "primary_topic_id":    topic.get("id", ""),
        "primary_topic_name":  topic.get("display_name", ""),
        "cited_by_count":      work.get("cited_by_count", 0),
    }

    for authorship in work.get("authorships", []):
        author       = authorship.get("author") or {}
        institutions = authorship.get("institutions", [])
        countries    = authorship.get("countries", [])
        affiliations = authorship.get("affiliations", [])

        inst_map = {inst["id"]: inst for inst in institutions if inst.get("id")}

        auth_base = {
            **base,
            "author_position":  authorship.get("author_position", ""),
            "author_id":        author.get("id", ""),
            "author_orcid":     author.get("orcid", ""),
            "author_name":      authorship.get("raw_author_name", "") or author.get("display_name", ""),
            "is_corresponding": authorship.get("is_corresponding", False),
            "country_codes":    "|".join(countries),
        }

        if affiliations:
            for aff in affiliations:
                raw_str  = aff.get("raw_affiliation_string", "")
                inst_ids = aff.get("institution_ids", [])

                inst_names = []
                inst_codes = []
                for iid in inst_ids:
                    inst = inst_map.get(iid, {})
                    inst_names.append(inst.get("display_name") or "")
                    inst_codes.append(inst.get("country_code") or "")

                rows.append({
                    **auth_base,
                    "raw_affiliation_string": raw_str,
                    "institution_ids":        "|".join(inst_ids),
                    "institution_names":      "|".join(inst_names),
                    "country_codes":          "|".join(inst_codes) if inst_codes else auth_base["country_codes"],
                })
        else:
            rows.append({
                **auth_base,
                "raw_affiliation_string": "",
                "institution_ids":        "",
                "institution_names":      "",
            })

    return rows


def process_chunk(input_path, output_path):
    total = filtered_out = written_rows = 0

    with open(input_path, encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
        writer.writeheader()

        for line in infile:
            line = line.strip()
            if not line:
                continue
            total += 1
            work = json.loads(line)

            if work.get("cited_by_count", 0) > CITATION_THRESHOLD:
                filtered_out += 1
                continue

            rows = extract_rows(work)
            writer.writerows(rows)
            written_rows += len(rows)

    return total, filtered_out, written_rows


def main(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    input_files = sorted(glob.glob(os.path.join(input_dir, "works_*_chunk_*.jsonl")))
    print(f"{len(input_files)} chunk bulundu.\n")

    grand_total = grand_filtered = grand_rows = 0

    for input_path in input_files:
        chunk_name  = os.path.basename(input_path).replace(".jsonl", ".csv")
        output_path = os.path.join(output_dir, chunk_name)

        total, filtered, rows = process_chunk(input_path, output_path)
        grand_total   += total
        grand_filtered += filtered
        grand_rows     += rows

        print(f"{chunk_name}: {total} work → {filtered} filtrelendi → {rows} satır yazıldı")

    print(f"\nTamamlandı.")
    print(f"  Toplam work    : {grand_total:,}")
    print(f"  Filtrelenen    : {grand_filtered:,} (cited_by_count > {CITATION_THRESHOLD})")
    print(f"  Yazılan satır  : {grand_rows:,}")
    print(f"  Çıktı klasörü  : {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSONL chunk'larını CSV'ye dönüştür")
    parser.add_argument("--input-dir",  required=True, help="JSONL chunk klasörü")
    parser.add_argument("--output-dir", required=True, help="CSV çıktı klasörü")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir)
