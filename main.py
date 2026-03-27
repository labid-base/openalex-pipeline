import requests
import json
import calendar
import argparse
import os


def fetch_works(mailto: str, year: int, month: int | None = None, chunk_size: int = 10000, output_dir: str = "."):
    base_url = "https://api.openalex.org/works"
    cursor = "*"
    total = 0
    chunk_index = 1
    current_chunk = []

    filters = [f"publication_year:{year}", "has_raw_affiliation_strings:true"]

    if month is not None:
        last_day = calendar.monthrange(year, month)[1]
        date_from = f"{year}-{month:02d}-01"
        date_to   = f"{year}-{month:02d}-{last_day:02d}"
        filters.append(f"from_publication_date:{date_from}")
        filters.append(f"to_publication_date:{date_to}")
        label = f"{year}_{month:02d}"
    else:
        label = str(year)

    filter_str = ",".join(filters)
    os.makedirs(output_dir, exist_ok=True)

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
    parser = argparse.ArgumentParser(description="Fetch works from OpenAlex")
    parser.add_argument("--mailto",     required=True,  help="Polite pool email (e.g. emirhan@unige.ch)")
    parser.add_argument("--year",       required=True,  type=int, help="Publication year (e.g. 2025)")
    parser.add_argument("--month",      default=None,   type=int, help="Publication month 1-12 (optional)")
    parser.add_argument("--chunk-size", default=10000,  type=int, help="Records per chunk file")
    parser.add_argument("--output-dir", default=".",              help="Output directory")
    args = parser.parse_args()

    fetch_works(
        mailto=args.mailto,
        year=args.year,
        month=args.month,
        chunk_size=args.chunk_size,
        output_dir=args.output_dir,
    )
