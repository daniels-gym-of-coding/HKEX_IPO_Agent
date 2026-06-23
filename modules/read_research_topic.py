import os
import sys

def read_research_topic(file_path: str = "research_topic.txt") -> str:
    """Reads and validates the research topic prompt from the specified file."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not prompt:
        print(f"Error: {file_path} is empty.", file=sys.stderr)
        sys.exit(1)

    return prompt
