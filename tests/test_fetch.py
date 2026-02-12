import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from source.fetch import save_raw_response, fetch


'''
Deze tests zijn gegenereerd door CHATGPT


python -m unittest discover -s tests

'''

class TestSaveRawResponse(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_files_and_returns_run_dir(self):
        xml = "<feed><entry>hi</entry></feed>"
        baseurl = "http://export.arxiv.org/api/query"
        params = {"search_query": 'ti:"random forest"', "start": 0, "max_results": 1}
        url = baseurl + "?dummy=1"
        status = 200
        response_bytes = len(xml.encode("utf-8"))

        run_dir = save_raw_response(
            xml_tekst=xml,
            baseurl=baseurl,
            params=params,
            url=url,
            http_status=status,
            response_bytes=response_bytes,
            root_dir=self.root
        )

        self.assertTrue(run_dir.exists())
        self.assertTrue(run_dir.is_dir())
        self.assertTrue((run_dir / "response.xml").exists())
        self.assertTrue((run_dir / "metadata.json").exists())

    def test_xml_is_saved_exactly(self):
        xml = "<feed>ABC</feed>"

        run_dir = save_raw_response(
            xml_tekst=xml,
            baseurl="http://export.arxiv.org/api/query",
            params={"search_query": "cat:cs.LG", "start": 0, "max_results": 5},
            url="http://export.arxiv.org/api/query?x=1",
            http_status=200,
            response_bytes=len(xml.encode("utf-8")),
            root_dir=self.root
        )

        saved = (run_dir / "response.xml").read_text(encoding="utf-8")
        self.assertEqual(saved, xml)

    def test_metadata_schema_and_values(self):
        xml = "<feed/>"
        baseurl = "http://export.arxiv.org/api/query"
        params = {"search_query": "cat:cs.LG", "start": 0, "max_results": 5}
        url = baseurl + "?search_query=cat:cs.LG"
        status = 200
        response_bytes = len(xml.encode("utf-8"))

        run_dir = save_raw_response(
            xml_tekst=xml,
            baseurl=baseurl,
            params=params,
            url=url,
            http_status=status,
            response_bytes=response_bytes,
            root_dir=self.root
        )

        meta = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))

        # schema keys
        required = ["fetched_at_utc", "endpoint", "params", "request_url", "http_status", "response_bytes"]
        for k in required:
            self.assertIn(k, meta)

        # exact values
        self.assertEqual(meta["endpoint"], baseurl)
        self.assertEqual(meta["params"], params)
        self.assertEqual(meta["request_url"], url)
        self.assertEqual(meta["http_status"], status)
        self.assertEqual(meta["response_bytes"], response_bytes)

        # timestamp sanity (niet exact testen)
        self.assertTrue(meta["fetched_at_utc"].endswith("Z"))
        self.assertTrue(meta["fetched_at_utc"].startswith("20"))

    def test_run_dir_structure_under_root(self):
        """
        Check dat hij opslaat onder:
        <root_dir>/raw/YYYY-MM-DD/run_YYYYMMDDTHHMMSSZ/
        """
        xml = "<feed/>"
        baseurl = "http://export.arxiv.org/api/query"
        params = {"search_query": "cat:cs.LG", "start": 0, "max_results": 1}
        url = baseurl + "?search_query=cat:cs.LG"
        status = 200
        response_bytes = len(xml.encode("utf-8"))

        run_dir = save_raw_response(
            xml_tekst=xml,
            baseurl=baseurl,
            params=params,
            url=url,
            http_status=status,
            response_bytes=response_bytes,
            root_dir=self.root
        )

        # run_dir begint met root/raw/
        self.assertEqual(run_dir.parents[2], self.root)      # .../<root>/raw/<date>/run_x
        self.assertEqual(run_dir.parents[1].name, "raw")     # .../<root>/raw/...

        # foldernaam begint met run_
        self.assertTrue(run_dir.name.startswith("run_"))


class TestFetch(unittest.TestCase):
    @patch("source.fetch.urllib.request.urlopen")
    def test_fetch_makes_one_request_and_decodes(self, mock_urlopen):
        class FakeResponse:
            status = 200
            def read(self):
                return b"<feed>ok</feed>"

        mock_urlopen.return_value = FakeResponse()

        baseurl = "http://export.arxiv.org/api/query"
        params = {"search_query": 'ti:"random forest"', "start": 0, "max_results": 1}

        url, status, response_bytes, xml_text = fetch(baseurl, params)

        self.assertEqual(status, 200)
        self.assertEqual(response_bytes, len(b"<feed>ok</feed>"))
        self.assertEqual(xml_text, "<feed>ok</feed>")

        # URL bevat baseurl + '?' en ge-encodeerde params (geen spaties/quotes raw)
        self.assertTrue(url.startswith(baseurl + "?"))
        self.assertIn("search_query=", url)
        self.assertIn("start=0", url)
        self.assertIn("max_results=1", url)

        mock_urlopen.assert_called_once_with(url)


if __name__ == "__main__":
    unittest.main()
