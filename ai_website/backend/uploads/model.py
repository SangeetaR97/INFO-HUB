#!/usr/bin/env python3
"""
model.py
Python component for Prompt Suggestion System — uses prompts from prompts.py (no JSON).

Usage:
    python model.py "your query here" [top_k]

Outputs a JSON object to stdout:
{"query": "...", "suggestions": [{"prompt": "...", "score": ...}, ...]}
"""

import sys
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Import prompts from prompts.py
from prompts import prompts

EMBED_FILE = "prompts_embeddings.npy"
MODEL_NAME = "all-mpnet-base-v2"  # change if you prefer smaller/larger model

def build_embeddings(prompts_list, model):
    return model.encode(prompts_list, convert_to_numpy=True, show_progress_bar=True)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No query provided"}))
        sys.exit(1)

    query = sys.argv[1]
    try:
        top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    except:
        top_k = 5

    # Load model
    model = SentenceTransformer(MODEL_NAME)

    # Load or build embeddings for prompts (cached to file)
    embeddings = None
    if os.path.exists(EMBED_FILE):
        try:
            embeddings = np.load(EMBED_FILE)
        except Exception:
            embeddings = None

    if embeddings is None:
        embeddings = build_embeddings(prompts, model)
        np.save(EMBED_FILE, embeddings)

    # Embed query
    query_emb = model.encode([query], convert_to_numpy=True)[0]

    # Cosine similarity
    sims = cosine_similarity([query_emb], embeddings)[0]
    top_idx = np.argsort(sims)[-top_k:][::-1]

    results = []
    for i in top_idx:
        results.append({
            "prompt": prompts[i],
            "score": float(sims[i])
        })

    # Print JSON to stdout
    print(json.dumps({"query": query, "suggestions": results}, ensure_ascii=False))

if __name__ == "__main__":
    main()

