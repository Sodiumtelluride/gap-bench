import json

with open("compare_query_types/data/medcpt_results_gold_standard_judge_entities (2).json", "r") as f:
    research_need_data = json.load(f)

with open("compare_query_types/data/medcpt_results_raw_quote.json", "r") as f:
    raw_quote_data = json.load(f)

with open("compare_query_types/data/medcpt_results_target.json", "r") as f:
    target_data = json.load(f)

judgments = {}
for i, query in enumerate(research_need_data[:40]):
    judgments[i] = {}
    judgments[i]["research_need"] = {}
    judgments[i]["research_need"]["query"] = query["query"]
    judgments[i]["research_need"]["ranked_articles"] = []
    relevant_set = []
    for article in query["combined_results"][:20]:
        judgments[i]["research_need"]["ranked_articles"].append(article["article_id"])
        if "human" in article["relevance"] and "dasha" in article["relevance"]["human"]:
            if article["relevance"]["human"]["dasha"]["label"] == "relevant":
                relevant_set.append(article["article_id"])
    judgments[i]["research_need"]["relevant_set"] = relevant_set
    

for i, query in enumerate(raw_quote_data[:40]):
    judgments[i]["raw_quote"] = {}
    judgments[i]["raw_quote"]["query"] = query["query_raw_quote"]
    judgments[i]["raw_quote"]["ranked_articles"] = []
    relevant_set = []
    for article in query["combined_results"][:20]:
        judgments[i]["raw_quote"]["ranked_articles"].append(article["article_id"])

for i, query in enumerate(target_data[:40]):
    judgments[i]["target"] = {}
    judgments[i]["target"]["query"] = query["query_target"]
    judgments[i]["target"]["ranked_articles"] = []
    relevant_set = []
    for article in query["combined_results"][:20]:
        judgments[i]["target"]["ranked_articles"].append(article["article_id"])


with open("research_need_judgments.json", "w") as f:
    json.dump(judgments, f, indent=2)
