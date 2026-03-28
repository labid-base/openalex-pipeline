#!/usr/bin/env python3

import requests
import json
import calendar
import argparse
import os
import math
from datetime import date


def fetch_works(mailto: str, year: int, month: int | None = None, chunk_size: int = 10000, output_dir: str = "."):
    base_url = "https://api.openalex.org/works"
    cursor = "*"
    total = 0
    chunk_index = 1
    current_chunk = []

    # OpenAlex filter examples:
    # - Single year: publication_year:2025
    # - Year range (e.g. 2012-2015): from_publication_date:2012-01-01,to_publication_date:2015-12-31
    #   (If you want this behavior, replace publication_year filter with the two date filters above.)
    # Base date/year filters in this script.
    base_filters = [f"publication_year:{year}"]

    if month is not None:
        # When month is provided, narrow results to that full month range.
        last_day = calendar.monthrange(year, month)[1]
        date_from = f"{year}-{month:02d}-01"
        date_to   = f"{year}-{month:02d}-{last_day:02d}"
        base_filters.append(f"from_publication_date:{date_from}")
        base_filters.append(f"to_publication_date:{date_to}")
        label = f"{year}_{month:02d}"
    else:
        label = str(year)

    total_filter_str = ",".join(base_filters)
    # Download only works that include raw affiliation strings.
    filters = base_filters + ["has_raw_affiliation_strings:true"]
    filter_str = ",".join(filters)
    os.makedirs(output_dir, exist_ok=True)

    # Pre-check counts to show scope before long-running download starts.
    total_response = requests.get(base_url, params={
        "filter": total_filter_str,
        "per_page": 1,
        "mailto": mailto,
    })
    total_response.raise_for_status()
    total_works = total_response.json().get("meta", {}).get("count", 0)

    with_aff_response = requests.get(base_url, params={
        "filter": filter_str,
        "per_page": 1,
        "mailto": mailto,
    })
    with_aff_response.raise_for_status()
    works_with_affiliation = with_aff_response.json().get("meta", {}).get("count", 0)
    estimated_chunks = math.ceil(works_with_affiliation / chunk_size) if works_with_affiliation else 0

    print("Pre-check summary")
    print(f"  Total works            : {total_works:,}")
    print(f"  Works with affiliation : {works_with_affiliation:,}")
    print(f"  Estimated chunks       : {estimated_chunks:,} (chunk_size={chunk_size:,})")

    print(f"Fetching: year={year}" + (f", month={month:02d}" if month else "") + f"  →  filter: {filter_str}\n")

    while cursor:
        response = requests.get(base_url, params={
            "filter": filter_str,
            "per_page": 200,
            "cursor": cursor,
            "mailto": mailto,
            "select": "id,doi,title,publication_year,type,language,primary_topic,topics,cited_by_count,authorships"
        })

        data = response.json()
        results = data.get("results", [])

        for work in results:
            current_chunk.append(work)

            if len(current_chunk) >= chunk_size:
                filename = os.path.join(output_dir, f"works_{label}_chunk_{chunk_index:04d}.jsonl")
                with open(filename, "w", encoding="utf-8") as f:
                    for w in current_chunk:
                        f.write(json.dumps(w) + "\n")
                print(f"Saved: {filename}")
                chunk_index += 1
                current_chunk = []

        total += len(results)
        print(f"Fetched: {total}")
        cursor = data.get("meta", {}).get("next_cursor")

    if current_chunk:
        filename = os.path.join(output_dir, f"works_{label}_chunk_{chunk_index:04d}.jsonl")
        with open(filename, "w", encoding="utf-8") as f:
            for w in current_chunk:
                f.write(json.dumps(w) + "\n")
        print(f"Saved: {filename}")

    print(f"\nDone. Total: {total} works")


if __name__ == "__main__":
    default_mailto = os.getenv("OPENALEX_MAILTO", "emirhan@unige.ch")
    default_year = int(os.getenv("OPENALEX_YEAR", str(date.today().year)))
    default_month = os.getenv("OPENALEX_MONTH")
    default_month = int(default_month) if default_month else None
    default_output_dir = os.getenv("OPENALEX_OUTPUT_DIR", "data/jsonl")

    parser = argparse.ArgumentParser(description="Fetch works from OpenAlex")
    parser.add_argument("--mailto",     default=default_mailto, help="Polite pool email (can come from OPENALEX_MAILTO)")
    parser.add_argument("--year",       default=default_year, type=int, help="Publication year (default: current year or OPENALEX_YEAR)")
    parser.add_argument("--month",      default=default_month, type=int, choices=range(1, 13), help="Publication month 1-12 (optional, or OPENALEX_MONTH)")
    parser.add_argument("--chunk-size", default=10000,  type=int, help="Records per chunk file")
    parser.add_argument("--output-dir", default=default_output_dir, help="Output directory (default: data/jsonl or OPENALEX_OUTPUT_DIR)")
    args = parser.parse_args()

    fetch_works(
        mailto=args.mailto,
        year=args.year,
        month=args.month,
        chunk_size=args.chunk_size,
        output_dir=args.output_dir,
    )
