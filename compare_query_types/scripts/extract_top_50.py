import json

with open("compare_query_types/data/medcpt_results_gold_standard_judge_entities (2).json", "r") as f:
    data = json.load(f)
    top_50 = data[:50]

with open("top_50_quotes_and_targets.json", "w") as f:
    new = []
    for rec in top_50:
        new.append({
            "raw_quote": rec["raw_quote"],
            "target": rec["target"]
        })
    json.dump(new, f, indent=2)