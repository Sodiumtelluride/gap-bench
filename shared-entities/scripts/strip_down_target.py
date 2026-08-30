import json

with open("shared-entities/data/medcpt_results_gold_standard_judge_with_shared_entities.json", "r") as f:
    medcpt_results = json.load(f)
    stripped_results = []
    for result in medcpt_results:
        new_result = {
            "target": result["target"],
            "raw_quote": result["raw_quote"],
            "source_article_id": result["source_article_id"],
        }
        stripped_results.append(new_result)

with open("shared-entities/data/stripped_medcpt_results.json", "w") as f:
    json.dump(stripped_results, f, indent=2)
