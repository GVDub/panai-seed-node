import os
import logging
import json
import argparse
from datetime import datetime, timedelta
from memory_api.memory_logger import logger


# Replace with actual embedding module import
# from your_embedding_module import embed_function
def embed_function(text): return [0.0] * 768  # placeholder for embedding

def load_memory_log(file_path):
    """
    Load memory log as either a JSON list or JSONL file.
    Returns a list of entry dicts.
    """
    with open(file_path, 'r') as f:
        content = f.read()
    content_stripped = content.strip()
    # If file is a JSON list, parse it directly
    if content_stripped.startswith('['):
        try:
            data = json.loads(content_stripped)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            # Fall back to line-by-line parsing
            pass
    # Fallback: parse as newline-delimited JSON
    entries = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as e:
            logger.warning(f"[PruneLogs] Skipping malformed JSON line: {e}")
    return entries

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
        ts_str = entry.get("timestamp") if isinstance(entry, dict) else None
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
            logger.info(f"Wrote batch {i//batch_size + 1} with {len(batch)} entries to {output_path}")
    return total_written

def main():
    logger.info("Starting log pruning process")
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
        logger.info(f"Loaded {len(entries)} entries.")

    entries_before = len(entries)
    entries = deduplicate_entries(entries)
    if args.verbose:
        logger.info(f"Deduplicated entries: removed {entries_before - len(entries)} entries, {len(entries)} remain.")

    entries_before = len(entries)
    entries = prune_old_entries(entries, days_threshold=args.days)
    if args.verbose:
        logger.info(f"Pruned old entries: removed {entries_before - len(entries)} entries, {len(entries)} remain.")

    if args.reembed:
        # from your_embedding_module import embed_function
        entries_before = len(entries)
        entries = reembed_non_vector_entries(entries, embed_function, verbose=args.verbose)
        if args.verbose:
            logger.info("Re-embedded entries without vectors.")

    entries_before = len(entries)
    entries, removed = remove_entries_without_vectors(entries)
    if args.verbose:
        logger.info(f"Removed {removed} entries without vectors, {len(entries)} remain.")

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
            logger.info(f"Processed batch {batch_idx + 1}/{batches} with {len(batch_entries)} entries.")

    logger.info(f"Log pruning completed. {total_entries} total entries written.")

def prune_synced_logs(input_path, output_path, days_threshold=30):
    try:
        entries = load_memory_log(input_path)
        logger.info(f"Loaded {len(entries)} entries.")
    except Exception as e:
        logger.error(f"Failed to load memory log: {e}")
        return

    try:
        entries = [e for e in entries if isinstance(e, dict)]
        entries = deduplicate_entries(entries)
        logger.info(f"{len(entries)} entries after deduplication.")

        entries = prune_old_entries(entries, days_threshold=days_threshold)
        logger.info(f"{len(entries)} entries after pruning old data.")

        entries, removed = remove_entries_without_vectors(entries)
        logger.info(f"{len(entries)} entries remain after removing {removed} entries without vectors.")

        total_written = write_cleaned_log(entries, output_path)
        logger.info(f"Cleaned log written to {output_path} with {total_written} entries.")
    except Exception as e:
        logger.error(f"Failed during pruning process: {e}")


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
                    logger.debug(f"Re-embedded entry: {entry.get('text')[:60]}...")
            except Exception as e:
                if verbose:
                    logger.debug(f"Failed to embed entry: {entry.get('text')[:60]}... Error: {e}")
        updated_entries.append(entry)
    if verbose:
        logger.info(f"Re-embedded {reembedded_count} entries without vectors.")
    return updated_entries

# Async stub for future compatibility
async def async_prune_synced_logs(input_path, output_path, days_threshold=30):
    """
    Async wrapper for prune_synced_logs to allow future non-blocking I/O.
    Currently calls the sync version directly.
    """
    prune_synced_logs(input_path, output_path, days_threshold)

if __name__ == "__main__":
    main()