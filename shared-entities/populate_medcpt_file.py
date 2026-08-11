import json

# enter the medcpt file you want to be modified here 
YOUR_MEDCPT_FILE = ""
SHARED_ENTITIES_FILE = "shared-entities/medcpt_results_gold_standard_judge_shared_entities.json"

with open(YOUR_MEDCPT_FILE, "r") as f:
    medcpt_results = json.load(f)

with open(SHARED_ENTITIES_FILE, "r") as f:
    shared_entities = json.load(f)

out = []
for i, rec in enumerate(medcpt_results):
    if i<100:
        rec["entities"] = shared_entities[i]["entities"]
    rec["entities_knn"]= shared_entities[i]["entities_knn"]
    rec["entities_reranked"]= shared_entities[i]["entities_reranked"]
    for j, result in enumerate(rec["combined_results"]):
        result["exact_shared_entities"] = shared_entities[i]["combined_results"][j]["exact_shared_entities"]
        result["knn_shared_entities"] = shared_entities[i]["combined_results"][j]["knn_shared_entities"]
    out.append(rec)

# enter the name of your output file here
with open("results.json", "w") as f:
    json.dump(out, f, indent=2  )




