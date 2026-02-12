'''
“Thank you to arXiv for use of its open access interoperability.”


'''

from fetch import fetch, save_raw_response
from parse import parse, load_state, save_state, save_jsonl
from pathlib import Path



baseurl = 'http://export.arxiv.org/api/query'
params = {
    "search_query": 'ti:"robot"',
    "start": 0,
    "max_results": 25        
}
    
url, http_status, response_bytes, xml_tekst = fetch(baseurl=baseurl, params=params)

run_dir = save_raw_response(xml_tekst=xml_tekst, baseurl=baseurl, params=params, url=url, http_status=http_status, response_bytes=response_bytes)

path = run_dir / "response.xml"
metapath = run_dir / "metadata.json"
outpath = Path("data/processed/papers.jsonl")

seen_ids = load_state()

for paper in parse(path, metapath):
    if paper["paper_id"] in seen_ids:
        continue

    save_jsonl(paper, outpath)

    seen_ids.add(paper["paper_id"])

save_state(seen_ids)