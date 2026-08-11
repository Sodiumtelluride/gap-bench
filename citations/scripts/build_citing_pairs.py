"""Find (query source article, retrieved candidate) pairs where the candidate
cites the article the query was derived from.

Inputs:  medcpt_results_gold_standard_judge.json
         ignor-corpus-2022-2026-sections-with-references.jsonl
Output:  citing_pairs.json
"""

import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "citations" / "data"

CORPUS = DATA / "ignor-corpus-2022-2026-sections-with-references.jsonl"
RESULTS = REPO / "medcpt_results_gold_standard_judge.json"
OUT = DATA / "citing_pairs.json"
FIELDS = ["combined_results", "results", "bm25_results"]

# --- corpus: article_id -> title / pub_date / reference set -------------------
refs, titles, pub_dates = {}, {}, {}
with open(CORPUS) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        aid = rec.get("article_id")
        if aid is None:
            continue
        aid = str(aid)
        if aid in refs:
            continue
        refs[aid] = {str(x) for x in (rec.get("references") or [])}
        titles[aid] = rec.get("title") or ""
        pub_dates[aid] = rec.get("pub_date") or ""

# --- walk the results, collect citing pairs -----------------------------------
with open(RESULTS) as f:
    records = json.load(f)

pairs = defaultdict(lambda: {"fields": set(), "occurrences": []})

for qi, rec in enumerate(records):
    src = rec.get("source_article_id")
    if not src:
        continue
    src = str(src)
    for field in FIELDS:
        for rank, cand in enumerate(rec.get(field) or [], start=1):
            cid = str(cand.get("article_id"))
            if cid not in refs or src not in refs[cid]:
                continue
            entry = pairs[(src, cid)]
            entry["fields"].add(field)
            entry["occurrences"].append({
                "query_index": qi,
                "query": rec.get("query", ""),
                "target": rec.get("target", ""),
                "field": field,
                "rank": rank,
                "llm_judgment": (cand.get("relevance") or {}).get("judgment"),
            })

out_pairs = []
for (src, cid), entry in sorted(pairs.items()):
    occ = sorted(entry["occurrences"], key=lambda o: (o["field"], o["rank"]))
    judgments = [o["llm_judgment"] for o in occ if o["llm_judgment"]]
    out_pairs.append({
        "source_article_id": src,
        "source_title": titles.get(src, ""),
        "source_pub_date": pub_dates.get(src, ""),
        "citing_article_id": cid,
        "citing_title": titles.get(cid, ""),
        "citing_pub_date": pub_dates.get(cid, ""),
        "fields": sorted(entry["fields"]),
        "n_query_occurrences": len(occ),
        "llm_judgment_counts": {
            "yes": judgments.count("yes"),
            "no": judgments.count("no"),
            "unclear": judgments.count("unclear"),
            "unjudged": len(occ) - len(judgments),
        },
        "occurrences": occ,
    })

payload = {
    "description": (
        "Pairs where a retrieved candidate article cites the source article "
        "the query was derived from (candidate.references contains "
        "source_article_id)."
    ),
    "results_file": RESULTS.name,
    "corpus_file": CORPUS.name,
    "n_pairs": len(out_pairs),
    "n_source_articles": len({p["source_article_id"] for p in out_pairs}),
    "n_query_records_total": len(records),
    "pairs": out_pairs,
}

with open(OUT, "w") as f:
    json.dump(payload, f, indent=2)

print(f"wrote {OUT}: {payload['n_pairs']} pairs, "
      f"{payload['n_source_articles']} source articles")
