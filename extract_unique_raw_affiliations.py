#!/usr/bin/env python3

import argparse
import csv
import glob
import json
import os


def process_chunk(input_path: str, output_path: str) -> tuple[int, int, int]:
    """Extract unique raw affiliation strings from a single JSONL chunk."""
    seen = set()
    unique_rows = []  # list of (work_id, raw_affiliation_string)

    total_works = 0
    total_affiliations_seen = 0

    with open(input_path, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            total_works += 1
            work = json.loads(line)
            work_id = work.get("id", "")

            for authorship in work.get("authorships", []):
                for affiliation in authorship.get("affiliations", []):
                    raw_value = affiliation.get("raw_affiliation_string", "")
                    if not raw_value or not raw_value.strip():
                        continue

                    total_affiliations_seen += 1
                    if raw_value in seen:
                        continue

                    seen.add(raw_value)
                    unique_rows.append((work_id, raw_value))

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["work_id", "raw_affiliation_string"])
        for work_id, raw_value in unique_rows:
            writer.writerow([work_id, raw_value])

    return total_works, total_affiliations_seen, len(unique_rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract unique raw_affiliation_string values from OpenAlex JSONL chunks"
    )
    parser.add_argument("--input-dir",  required=True, help="Directory containing works_*_chunk_*.jsonl files")
    parser.add_argument("--output-dir", required=True, help="Output directory for per-chunk CSV files")
    args = parser.parse_args()

    input_files = sorted(glob.glob(os.path.join(args.input_dir, "works_*_chunk_*.jsonl")))
    if not input_files:
        raise FileNotFoundError(f"No input files found in {args.input_dir} matching works_*_chunk_*.jsonl")

    os.makedirs(args.output_dir, exist_ok=True)

    grand_works = grand_affiliations = grand_unique = 0

    for input_path in input_files:
        chunk_name  = os.path.basename(input_path).replace(".jsonl", ".csv")
        output_path = os.path.join(args.output_dir, chunk_name)

        total_works, total_affiliations, unique_count = process_chunk(input_path, output_path)
        grand_works       += total_works
        grand_affiliations += total_affiliations
        grand_unique      += unique_count

        print(f"{chunk_name}: {total_works:,} works | {total_affiliations:,} affiliations | {unique_count:,} unique")

    print()
    print("Done.")
    print(f"  Total works scanned     : {grand_works:,}")
    print(f"  Raw affiliation entries : {grand_affiliations:,}")
    print(f"  Unique per-chunk total  : {grand_unique:,}")
    print(f"  Output dir              : {args.output_dir}")


if __name__ == "__main__":
    main()
