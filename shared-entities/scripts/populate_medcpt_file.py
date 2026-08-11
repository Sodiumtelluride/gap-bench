import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "shared-entities" / "data"

# Enter the medcpt file you want to be modified here. A bare filename is read
# from shared-entities/data/; an absolute path is used as-is.
YOUR_MEDCPT_FILE = DATA / "medcpt_results_gold_standard_judge_with_shared_entities.json" 
SHARED_ENTITIES_FILE = DATA / "medcpt_results_gold_standard_judge_shared_entities.json"

with open(YOUR_MEDCPT_FILE, "r") as f:
    medcpt_results = json.load(f)

with open(SHARED_ENTITIES_FILE, "r") as f:
    shared_entities = json.load(f)

out = []
for i, rec in enumerate(medcpt_results):
    if i<100:
        rec["entities"] = shared_entities[i]["entities"]
        rec["identified_query_entities"] = shared_entities[i]["identified_query_entities"]
        rec["unidentified_query_entities"] = shared_entities[i]["unidentified_query_entities"]
    rec["entities_knn"]= shared_entities[i]["entities_knn"]
    rec["entities_reranked"]= shared_entities[i]["entities_reranked"]
    for j, result in enumerate(rec["combined_results"]):
        result["exact_shared_entities"] = shared_entities[i]["combined_results"][j]["exact_shared_entities"]
        result["knn_shared_entities"] = shared_entities[i]["combined_results"][j]["knn_shared_entities"]
    out.append(rec)

# enter the name of your output file here
with open(DATA / "results.json", "w") as f:
    json.dump(out, f, indent=2  )




