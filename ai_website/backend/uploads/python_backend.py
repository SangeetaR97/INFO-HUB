#!/usr/bin/env python3
"""
python_backend.py
Prints suggestions one by one, still using JSON output from model.py
"""

import subprocess
import sys
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 python_backend.py \"your query here\" [top_k]")
        sys.exit(1)

    # Combine args into query
    raw_args = sys.argv[1:]
    query = " ".join(raw_args)

    # Optional top_k
    top_k = None
    if raw_args[-1].isdigit():
        top_k = int(raw_args[-1])
        query = " ".join(raw_args[:-1])

    # Call model.py as subprocess
    cmd = [sys.executable, "model.py", query]
    if top_k:
        cmd.append(str(top_k))

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except Exception as e:
        print(f"ERROR: failed to run model.py: {e}")
        sys.exit(1)

    if proc.stdout:
        # Parse JSON output
        try:
            data = json.loads(proc.stdout)
            suggestions = data.get("suggestions", [])
            # Print suggestions line by line
           # print("--- Suggestions ---")
            for idx, item in enumerate(suggestions, 1):
                print(f"{idx}. {item['prompt']} (score: {item['score']:.3f})")
           # print("--- End ---\n")
        except json.JSONDecodeError:
            print("ERROR: model.py did not return valid JSON")
            print(proc.stdout)
    else:
        print("No output from model.py")

if __name__ == "__main__":
    main()
