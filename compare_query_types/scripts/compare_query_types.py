import json
from math import log2
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
JUDGMENTS = DATA / "research_need_judgments.json"

QUERY_TYPES = ["research_need", "raw_quote", "target"]
K = 20


def ndcg_at_k(ranked_ids, relevant_set, k=10):
    gains = [1 if doc in relevant_set else 0 for doc in ranked_ids[:k]]
    dcg = sum(g / log2(i + 2) for i, g in enumerate(gains))
    n_ideal = min(len(relevant_set), k)
    idcg = sum(1 / log2(i + 2) for i in range(n_ideal))
    return dcg / idcg if idcg > 0 else 0.0

def condense(ranked_ids, judged_set):
    return [d for d in ranked_ids if d in judged_set]




with open(JUDGMENTS, "r") as f:
    judgments = json.load(f)

for idx, judgment in judgments.items():
    # The research-need annotations are the ground truth for all three query
    # types, since only those were judged by hand.
    relevant_set = set(judgment["research_need"]["relevant_set"])
    for query_type in QUERY_TYPES:
        ranked_ids = judgment[query_type]["ranked_articles"]
        judgment[query_type][f"ndcg_at_{K}"] = ndcg_at_k(ranked_ids, relevant_set, k=K)

with open(JUDGMENTS, "w") as f:
    json.dump(judgments, f, indent=2)

for query_type in QUERY_TYPES:
    scores = [judgments[idx][query_type][f"ndcg_at_{K}"] for idx in judgments]
    mean_ndcg = sum(scores) / len(scores) if scores else 0.0
    print(f"Mean NDCG@{K} for {query_type}: {mean_ndcg:.4f}")