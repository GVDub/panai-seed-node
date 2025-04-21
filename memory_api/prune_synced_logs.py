import json
import os
import argparse
from datetime import datetime, timedelta

def load_memory_log(file_path):
    with open(file_path, 'r') as f:
        return [json.loads(line) for line in f if line.strip()]

def deduplicate_entries(entries):
    seen = set()
    deduped = []
    for entry in entries:
        key = (entry.get("text"), entry.get("session_id"))
        if key not in seen:
            seen.add(key)
            deduped.append(entry)
    return deduped

def prune_old_entries(entries, days_threshold=30):
    cutoff = datetime.utcnow() - timedelta(days=days_threshold)
    pruned = []
    for entry in entries:
        ts_str = entry.get("timestamp")
        try:
            ts = datetime.fromisoformat(ts_str.rstrip('Z'))
            if ts > cutoff:
                pruned.append(entry)
        except Exception:
            # Keep malformed timestamp entries for manual inspection
            pruned.append(entry)
    return pruned

def write_cleaned_log(entries, output_path):
    with open(output_path, 'w') as f:
        for entry in entries:
            json.dump(entry, f)
            f.write('\n')

def main():
    parser = argparse.ArgumentParser(description="Prune and deduplicate memory logs.")
    parser.add_argument("input", help="Path to input memory log file")
    parser.add_argument("output", help="Path to output cleaned log file")
    parser.add_argument("--days", type=int, default=30, help="Age in days to retain entries (default: 30)")
    args = parser.parse_args()

    entries = load_memory_log(args.input)
    print(f"Loaded {len(entries)} entries.")

    entries = deduplicate_entries(entries)
    print(f"{len(entries)} entries after deduplication.")

    entries = prune_old_entries(entries, days_threshold=args.days)
    print(f"{len(entries)} entries after pruning old data.")

    write_cleaned_log(entries, args.output)
    print(f"Cleaned log written to {args.output}")

def prune_synced_logs(input_path, output_path, days_threshold=30):
    entries = load_memory_log(input_path)
    print(f"Loaded {len(entries)} entries.")

    entries = deduplicate_entries(entries)
    print(f"{len(entries)} entries after deduplication.")

    entries = prune_old_entries(entries, days_threshold=days_threshold)
    print(f"{len(entries)} entries after pruning old data.")

    write_cleaned_log(entries, output_path)
    print(f"Cleaned log written to {output_path}")

if __name__ == "__main__":
    main()