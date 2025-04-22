import json
import argparse
from datetime import datetime, timedelta


# Replace with actual embedding module import
# from your_embedding_module import embed_function
def embed_function(text): return [0.0] * 768  # placeholder for embedding

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
    return filtered, removed

def write_cleaned_log(entries, output_path, batch_size=1000, verbose=False):
    mode = 'w'
    total_written = 0
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i+batch_size]
        with open(output_path, mode) as f:
            for entry in batch:
                json.dump(entry, f)
                f.write('\n')
        total_written += len(batch)
        mode = 'a'
        if verbose:
            print(f"Wrote batch {i//batch_size + 1} with {len(batch)} entries to {output_path}")
    return total_written

def main():
    parser = argparse.ArgumentParser(description="Prune and deduplicate memory logs.")
    parser.add_argument("input", help="Path to input memory log file")
    parser.add_argument("output", help="Path to output cleaned log file")
    parser.add_argument("--days", type=int, default=30, help="Age in days to retain entries (default: 30)")
    parser.add_argument("--reembed", action="store_true", help="Re-embed entries without vectors")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for processing entries (default: 1000)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    entries = load_memory_log(args.input)
    if args.verbose:
        print(f"Loaded {len(entries)} entries.")

    entries_before = len(entries)
    entries = deduplicate_entries(entries)
    if args.verbose:
        print(f"Deduplicated entries: removed {entries_before - len(entries)} entries, {len(entries)} remain.")

    entries_before = len(entries)
    entries = prune_old_entries(entries, days_threshold=args.days)
    if args.verbose:
        print(f"Pruned old entries: removed {entries_before - len(entries)} entries, {len(entries)} remain.")

    if args.reembed:
        # from your_embedding_module import embed_function
        entries_before = len(entries)
        entries = reembed_non_vector_entries(entries, embed_function, verbose=args.verbose)
        if args.verbose:
            print("Re-embedded entries without vectors.")

    entries_before = len(entries)
    entries, removed = remove_entries_without_vectors(entries)
    if args.verbose:
        print(f"Removed {removed} entries without vectors, {len(entries)} remain.")

    total_entries = len(entries)
    batches = (total_entries + args.batch_size - 1) // args.batch_size

    for batch_idx in range(batches):
        start = batch_idx * args.batch_size
        end = min(start + args.batch_size, total_entries)
        batch_entries = entries[start:end]
        write_mode = 'w' if batch_idx == 0 else 'a'
        with open(args.output, write_mode) as f:
            for entry in batch_entries:
                json.dump(entry, f)
                f.write('\n')
        if args.verbose:
            print(f"Processed batch {batch_idx + 1}/{batches} with {len(batch_entries)} entries.")

    print(f"Processed {batches} batches. Total entries written: {total_entries}")

def prune_synced_logs(input_path, output_path, days_threshold=30):
    try:
        entries = load_memory_log(input_path)
        print(f"Loaded {len(entries)} entries.")
    except Exception as e:
        print(f"[ERROR] Failed to load memory log: {e}")
        return

    try:
        entries = deduplicate_entries(entries)
        print(f"{len(entries)} entries after deduplication.")

        entries = prune_old_entries(entries, days_threshold=days_threshold)
        print(f"{len(entries)} entries after pruning old data.")

        entries, removed = remove_entries_without_vectors(entries)
        print(f"{len(entries)} entries remain after removing {removed} entries without vectors.")

        total_written = write_cleaned_log(entries, output_path)
        print(f"Cleaned log written to {output_path} with {total_written} entries.")
    except Exception as e:
        print(f"[ERROR] Failed during pruning process: {e}")


# Function to re-embed entries without vectors
def reembed_non_vector_entries(entries, embed_function, verbose=False):
    updated_entries = []
    reembedded_count = 0
    for entry in entries:
        if entry.get("vector") is None and entry.get("text"):
            try:
                embedded_vector = embed_function(entry["text"])
                entry["vector"] = embedded_vector
                reembedded_count += 1
                if verbose:
                    print(f"Re-embedded entry: {entry.get('text')[:60]}...")
            except Exception as e:
                if verbose:
                    print(f"Failed to embed entry: {entry.get('text')[:60]}... Error: {e}")
        updated_entries.append(entry)
    if verbose:
        print(f"Re-embedded {reembedded_count} entries without vectors.")
    return updated_entries

if __name__ == "__main__":
    main()