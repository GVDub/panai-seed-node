import argparse
import json
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from datetime import datetime

def export_memories(output_file, host='localhost', port=6333, collection_name='memory'):
    client = QdrantClient(host=host, port=port)
    scroll_filter = {}

    total_exported = 0
    offset = None
    with open(output_file, 'w') as f:
        while True:
            result, next_page = client.scroll(
                collection_name=collection_name,
                scroll_filter=scroll_filter,
                offset=offset,
                with_payload=True,
                with_vectors=True,
                limit=100
            )
            if not result:
                break
            for point in result:
                memory_entry = {
                    'id': point.id,
                    'payload': point.payload,
                    'vector': point.vector,
                }
                json.dump(memory_entry, f)
                f.write('\n')
                total_exported += 1
            offset = next_page

    print(f"Exported {total_exported} memory entries to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Export memory entries from Qdrant to JSONL.")
    parser.add_argument("output", help="Output file path (e.g., memory_log.json)")
    parser.add_argument("--host", default="localhost", help="Qdrant host (default: localhost)")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant port (default: 6333)")
    parser.add_argument("--collection", default="panai_memory", help="Collection name (default: panai_memory)")
    args = parser.parse_args()

    export_memories(args.output, args.host, args.port, args.collection)

if __name__ == "__main__":
    main()
