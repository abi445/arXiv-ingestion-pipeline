'''
parseer/normaliseer een ruwe tekst

Per record:
- ID van de paper
- Titel
- Abstract (summary in dit geval)
- Timestamps (published, evt updates)
- Auteurs
- Categorieën
- PDF link

'''

import feedparser
import json
from pathlib import Path



STATE_PATH = "data/state.json"

def load_state(): #load state van de papers die opgeslagen zijn
    with open(STATE_PATH) as f:
        content = f.read().strip()
        if not content:
            return set()
        return set(json.loads(content))


def save_state(seen): #voeg de nieuwe papers toe aan de oude state
    with open(STATE_PATH, "w") as f:
        json.dump(list(seen),f)

def load_metadata(path):
    with open(path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return metadata

def save_jsonl(paper, output_path):
    output_path = Path(output_path)

    with output_path.open("a", encoding="utf-8") as f:
         f.write(json.dumps(paper, ensure_ascii=False) + "\n")

def parse(xml_pad, meta_pad):

    feed = feedparser.parse(xml_pad)

    metadata = load_metadata(meta_pad)


    for entry in feed.entries:
        
        

        pdf_link = None
        for link in entry.links:
            if link.type == "application/pdf":
                pdf_link = link.href
                break

        data_json = {
            "paper_id": entry.get("id", "").split("/")[-1],
            "title": entry.get("title"),
            "abstract": entry.get("summary", "").replace("\n", " ").strip(),
            "published": entry.get("published"),
            "updated": entry.get("updated"),
            "authors": [a.get("name") for a in entry.get("authors", [])],
            "categories": [t.get("term") for t in entry.get("tags", [])],
            "pdf_link": pdf_link,
            "metadata": metadata
        }
        
        yield data_json



if __name__ == "__main__":
    path = "data/raw/2026-02-12/run_20260212T040931Z/response.xml"
    metapath = "data/raw/2026-02-12/run_20260212T040931Z/metadata.json"
    outpath = "data/processed/papers.jsonl"

    seen_ids = load_state()

    for paper in parse(path, metapath):
        if paper["paper_id"] in seen_ids:
            continue

        save_jsonl(paper, outpath)

        seen_ids.add(paper["paper_id"])

    save_state(seen_ids)