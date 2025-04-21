import json
import os
import argparse
from datetime import datetime, timedelta

# from your_embedding_module import embed_function

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

def remove_entries_without_vectors(entries):
    filtered = [entry for entry in entries if entry.get("vector") is not None]
    removed = len(entries) - len(filtered)
    print(f"Removed {removed} entries without vectors.")
    return filtered

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
    parser.add_argument("--reembed", action="store_true", help="Re-embed entries without vectors")
    args = parser.parse_args()

    entries = load_memory_log(args.input)
    print(f"Loaded {len(entries)} entries.")

    entries = deduplicate_entries(entries)
    print(f"{len(entries)} entries after deduplication.")

    entries = prune_old_entries(entries, days_threshold=args.days)
    print(f"{len(entries)} entries after pruning old data.")

    if args.reembed:
        from your_embedding_module import embed_function
        entries = reembed_non_vector_entries(entries, embed_function)

    entries = remove_entries_without_vectors(entries)

    write_cleaned_log(entries, args.output)
    print(f"Cleaned log written to {args.output}")

def prune_synced_logs(input_path, output_path, days_threshold=30):
    entries = load_memory_log(input_path)
    print(f"Loaded {len(entries)} entries.")

    entries = deduplicate_entries(entries)
    print(f"{len(entries)} entries after deduplication.")

    entries = prune_old_entries(entries, days_threshold=days_threshold)
    print(f"{len(entries)} entries after pruning old data.")

    entries = remove_entries_without_vectors(entries)

    write_cleaned_log(entries, output_path)
    print(f"Cleaned log written to {output_path}")


# Function to re-embed entries without vectors
def reembed_non_vector_entries(entries, embed_function):
    updated_entries = []
    reembedded_count = 0
    for entry in entries:
        if entry.get("vector") is None and entry.get("text"):
            try:
                embedded_vector = embed_function(entry["text"])
                entry["vector"] = embedded_vector
                reembedded_count += 1
            except Exception as e:
                print(f"Failed to embed entry: {entry.get('text')[:60]}... Error: {e}")
        updated_entries.append(entry)
    print(f"Re-embedded {reembedded_count} entries without vectors.")
    return updated_entries

if __name__ == "__main__":
    main()