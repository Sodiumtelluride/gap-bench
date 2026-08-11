"""Tag each candidate article with the entities it shares with its query.

Reads the judged results and the NER'd corpus, matches entities on their
canonical ontology ID (mondo:/hp:/pr:/...), and writes a `shared_entities`
list onto every candidate plus a `query_entities` list onto every record.
"""

import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
MEDCPT_RESULTS = DATA / "medcpt_results_gold_standard_judge_entities.json"
CORPUS = DATA / "corpus-2022-2026-bel-indented.json"
OUT = DATA / "medcpt_results_gold_standard_judge_shared_entities.json"

CANDIDATE_FIELD = "combined_results"
TOP_K = 5  # how many KNN neighbours per entity to consider a match against

def split_entity(entity):
    """'mondo:0005027||epilepsy (seizure disorder)' -> {'id': ..., 'name': ...}."""
    head, _, tail = entity.partition("||")
    return {"id": head, "name": tail or head}


def knn_canonical_ids(reranked):
    """Split on single pipes, but not double pipes."""
    if not reranked:
        return []
    return [
        value.strip().lower()
        for value in re.split(r"(?<!\|)\|(?!\|)", reranked)
        if value.strip()
    ][:TOP_K]

def knn_entity_lists(rec):
    """[(surface, {top-K knn canonical IDs})] per entity, order preserved.

    Kept per-entity rather than flattened so a query entity is only ever
    compared against a single article entity's own neighbour set.
    """
    surfaces = rec.get("entities_reranked", []) or []
    knn = rec.get("entities_knn", []) or []
    out = []
    for i, surface in enumerate(surfaces):
        out.append((surface, knn_canonical_ids(knn[i]) if i < len(knn) else []))
    return out

def main():
    results = json.loads(MEDCPT_RESULTS.read_text())
    corpus = json.loads(CORPUS.read_text())

    article_knn = {str(a["article_id"]): knn_entity_lists(a) for a in corpus}
    article_entities = {
        str(a["article_id"]): set(a.get("entities_reranked") or []) for a in corpus
    }

    tagged = missing = 0
    for rec in results:
        query_knn = knn_entity_lists(rec)
        query_entities = rec.get("entities_reranked") or []
        for cand in rec.get(CANDIDATE_FIELD) or []:
            aid = str(cand["article_id"])
            cand["exact_shared_entities"] = []
            cand["knn_shared_entities"] = []

            if aid not in article_entities:
                missing += 1
                continue

            abstract_entities = article_entities[aid]
            skipped_indexes = set()
            for i, entity in enumerate(query_entities):
                if entity == "None of the above":
                    continue
                if entity in abstract_entities:
                    skipped_indexes.add(i)
                    cand["exact_shared_entities"].append(split_entity(entity))

            for i, (q_entity, q_ids) in enumerate(query_knn):
                if i in skipped_indexes or not q_ids or q_entity == "None of the above":
                    continue
                for _, a_ids in article_knn.get(aid, ()):
                    if set(q_ids) & set(a_ids):
                        cand["knn_shared_entities"].append(split_entity(q_entity))
                        break

            tagged += 1

    OUT.write_text(json.dumps(results, indent=2))
    print(f"tagged {tagged} candidates, {missing} not found in corpus -> {OUT.name}")


if __name__ == "__main__":
    main()
