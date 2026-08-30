from Bio import Entrez  # pip install biopython
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "citations" / "data"

CORPUS = DATA / "ignor-corpus-2022-2026-sections (1).jsonl"
OUT = DATA / "ignor-corpus-2022-2026-sections-with-references.jsonl"
EMAIL = "gelfandnat@gmail.com"



# Function to fetch the articles this paper cites
def fetch_citing_articles_and_count(pmid, email):
    Entrez.email = email  # Set your email for NCBI API usage
    try:
        handle = Entrez.elink(dbfrom="pubmed", id=pmid, linkname="pubmed_pubmed_refs")
        records = Entrez.read(handle)
        handle.close()

        # Extract PMIDs of the articles that the given PMID cites
        if not records[0]["LinkSetDb"]:
            print(f"No citing articles found for PMID {pmid}")
            return []

        ref_pmids = [link["Id"] for link in records[0]["LinkSetDb"][0]["Link"]]
        
        return ref_pmids
    except Exception as e:
        print(f"Error fetching references articles for PMID {pmid}: {e}")
        return []

pmid_to_ref_map = {}
with open(CORPUS, "r") as f:
    unique_pmids = set()
    for line in f:
        record = json.loads(line)
        unique_pmids.add(record["article_id"])
    for pmid in unique_pmids:
        ref_pmids = fetch_citing_articles_and_count(pmid, EMAIL)
        pmid_to_ref_map[pmid] = ref_pmids


with open(CORPUS, "r") as f:
    corpus = [json.loads(line) for line in f]
    new_corpus = []
    for record in corpus:
        new_record = record.copy()
        new_record["references"] = pmid_to_ref_map.get(record["article_id"], [])
        new_corpus.append(new_record)

with open(OUT, "w") as f:
    for record in new_corpus:
        f.write(json.dumps(record) + "\n")