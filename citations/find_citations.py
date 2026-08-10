import pandas as pd
from Bio import Entrez
import json 
# Function to fetch citing articles and count the citations
def fetch_citing_articles_and_count(pmid, email):
    Entrez.email = email  # Set your email for NCBI API usage
    try:
        # Fetch the articles citing the input PMID
        handle = Entrez.elink(dbfrom="pubmed", id=pmid, linkname="pubmed_pubmed_refs")
        records = Entrez.read(handle)
        handle.close()

        # Extract PMIDs of the citing articles
        if not records[0]["LinkSetDb"]:
            print(f"No citing articles found for PMID {pmid}")
            return []

        ref_pmids = [link["Id"] for link in records[0]["LinkSetDb"][0]["Link"]]
        
        return ref_pmids
    except Exception as e:
        print(f"Error fetching references articles for PMID {pmid}: {e}")
        return []

pmid_to_ref_map = {}
with open("/Users/Nathan/Documents/GitHub/gap-bench/ignor-corpus-2022-2026-sections (1).jsonl", "r") as f:
    unique_pmids = set()
    for line in f:
        record = json.loads(line)
        unique_pmids.add(record["article_id"])
    for pmid in unique_pmids:
        ref_pmids = fetch_citing_articles_and_count(pmid, "gelfandnat@gmail.com")
        pmid_to_ref_map[pmid] = ref_pmids


with open("/Users/Nathan/Documents/GitHub/gap-bench/ignor-corpus-2022-2026-sections (1).jsonl", "r") as f:
    corpus = [json.loads(line) for line in f]
    new_corpus = []
    for record in corpus:
        new_record = record.copy()
        new_record["references"] = pmid_to_ref_map.get(record["article_id"], [])
        new_corpus.append(new_record)

with open("/Users/Nathan/Documents/GitHub/gap-bench/ignor-corpus-2022-2026-sections-with-references.jsonl", "w") as f:
    for record in new_corpus:
        f.write(json.dumps(record) + "\n")