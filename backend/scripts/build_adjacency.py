"""
Builds a station-pair adjacency list from a Network Rail SCHEDULE JSON
extract, joined against CORPUS for TIPLOC -> CRS codes.

Usage:
    python build_adjacency.py <path_to_schedule.json> <path_to_corpus.json> <output.json>

Example:
    python build_adjacency.py ../../networkrail-data/schedule.json ../../corpus.json adjacency.json
"""

import sys
import json
from collections import defaultdict

# Rough passenger-category whitelist. CIF train categories starting with
# "O" (ordinary passenger) or "X" (express passenger) are passenger
# services. Everything else (freight prefixes, EE/ES for empty coaching
# stock, DD/DH/DQ for departmental, ZZ for light engine, etc.) is excluded.
# Not exhaustive, but good enough to keep freight/ECS noise out of the
# adjacency list.
PASSENGER_PREFIXES = ("O", "X")


def load_corpus_tiploc_to_crs(corpus_path):
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = {}
    for rec in data.get("TIPLOCDATA", []):
        tiploc = (rec.get("TIPLOC") or "").strip()
        crs = (rec.get("3ALPHA") or "").strip()
        if tiploc and crs:
            mapping[tiploc] = crs
    return mapping


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    schedule_path, corpus_path, output_path = sys.argv[1:4]

    print("Loading CORPUS for TIPLOC -> CRS fallback mapping...")
    tiploc_to_crs = load_corpus_tiploc_to_crs(corpus_path)
    print(f"  {len(tiploc_to_crs)} TIPLOC -> CRS mappings from CORPUS")

    pair_counts = defaultdict(int)
    missing_crs_tiplocs = set()

    schedules_seen = 0
    schedules_passenger = 0
    lines_processed = 0

    print("Streaming SCHEDULE extract...")
    with open(schedule_path, "r", encoding="utf-8") as f:
        for line in f:
            lines_processed += 1
            if lines_processed % 500000 == 0:
                print(f"  ...{lines_processed} lines processed, "
                      f"{schedules_seen} schedules seen, "
                      f"{len(pair_counts)} unique pairs so far")

            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            # SCHEDULE's own TiplocV1 records sometimes carry a crs_code;
            # prefer that over CORPUS when present.
            if "TiplocV1" in obj:
                rec = obj["TiplocV1"]
                tiploc = (rec.get("tiploc_code") or "").strip()
                crs = (rec.get("crs_code") or "").strip()
                if tiploc and crs:
                    tiploc_to_crs[tiploc] = crs
                continue

            if "JsonScheduleV1" not in obj:
                continue

            schedules_seen += 1
            sched = obj["JsonScheduleV1"]

            segment = sched.get("schedule_segment") or {}
            category = (segment.get("CIF_train_category") or "").strip()
            if not category.startswith(PASSENGER_PREFIXES):
                continue

            schedules_passenger += 1

            locations = segment.get("schedule_location") or []
            tiplocs = []
            for loc in locations:
                t = (loc.get("tiploc_code") or "").strip()
                if t:
                    tiplocs.append(t)

            for a, b in zip(tiplocs, tiplocs[1:]):
                crs_a = tiploc_to_crs.get(a)
                crs_b = tiploc_to_crs.get(b)
                if not crs_a:
                    missing_crs_tiplocs.add(a)
                if not crs_b:
                    missing_crs_tiplocs.add(b)
                if not crs_a or not crs_b or crs_a == crs_b:
                    continue
                pair = tuple(sorted((crs_a, crs_b)))
                pair_counts[pair] += 1

    print()
    print(f"Done. {lines_processed} lines, {schedules_seen} schedules seen, "
          f"{schedules_passenger} passenger schedules kept.")
    print(f"{len(pair_counts)} unique station pairs found.")
    print(f"{len(missing_crs_tiplocs)} distinct TIPLOCs had no CRS mapping "
          f"(freight-only or administrative locations, expected).")

    pairs_out = [
        {"crs_a": a, "crs_b": b, "count": count}
        for (a, b), count in sorted(pair_counts.items(), key=lambda x: -x[1])
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pairs_out, f, indent=2)

    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()