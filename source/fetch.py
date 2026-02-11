'''
1 taak, haal de papers op van arXiv op basis van een query en de raw response teruggeven

Om te testen: 1 call die 25 papers ophaalt.


verzoek van arXiv API:
“Thank you to arXiv for use of its open access interoperability.”

'''

import urllib, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone
import json

baseurl = 'http://export.arxiv.org/api/query?'
params = {
    "search_query": 'ti:"random forest"',
    "start": 0,
    "max_results": 1        
}
url = baseurl + urllib.parse.urlencode(params)


data = urllib.request.urlopen(url)
http_status = data.status
xml_tekst = (data.read().decode('utf-8'))


def save_raw_response(xml_tekst, baseurl, params, url, http_status):
    '''
    Dit slaat de run op in een mapje met daarin een JSON file voor de meta data en een XML file voor de tekst
    
    de meta data die ik wil opslaan:
    - fetched_tijd (utc)
    - base_url (ook wel endpoint)
    - parameters
    - volledige_url
    - http_status
    '''

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    run_id = now.strftime("%Y%m%dT%H%M%SZ")

    run_dir = Path("data") / "raw" / date_str / f"run_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    xml_path = run_dir / "response.xml"
    xml_path.write_text(xml_tekst, encoding="utf-8")

    metadata = {
        "fetched_at_utc": run_id,
        "endpoint": baseurl,
        "params": params,
        "request_url": url,
        "http_status": http_status,
    }

    meta_path = run_dir / "metadata.json"
    meta_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Raw run opgeslagen in: {run_dir}")


if __name__ == "__main__":
    save_raw_response(xml_tekst=xml_tekst, baseurl=baseurl, params=params, url=url, http_status=http_status)

    

