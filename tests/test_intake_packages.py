import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from library_custodian.discovery import discover
from test_change_detection import build_library, StubFetcher, DOC_URL


class DownloadFetcher(StubFetcher):
    def get(self, url):
        if url == DOC_URL:
            return b'%PDF-reviewed-later', {'content_type': 'application/pdf', 'final_url': url,
                                            'etag': self.etag, 'redirect_chain': []}
        return super().get(url)


class IntakePackageTests(unittest.TestCase):
    def test_changed_known_source_downloads_with_provenance_without_mutating_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            library, registry = build_library(root)
            manifest = library / 'documents.jsonl'
            before = manifest.read_bytes()
            with patch('library_custodian.discovery.Fetcher', DownloadFetcher):
                DownloadFetcher.etag = 'v1'
                discover(library, registry, root / 'state', root / 'quarantine', download=True)
                self.assertFalse(list((root / 'quarantine').rglob('*.intake.json')))
                DownloadFetcher.etag = 'v2'
                report = discover(library, registry, root / 'state', root / 'quarantine', download=True)
            self.assertEqual(report['counts']['downloaded_to_quarantine'], 1)
            path = next((root / 'quarantine').rglob('*.intake.json'))
            package = json.loads(path.read_text())
            self.assertEqual(package['approval_state'], 'quarantined_unreviewed')
            self.assertEqual(package['resolved_source_uri'], DOC_URL)
            self.assertEqual(package['redirect_chain'], [])
            self.assertEqual(package['source_sha256'], hashlib.sha256((path.parent / package['source_filename']).read_bytes()).hexdigest())
            self.assertEqual(before, manifest.read_bytes())

    def test_discovery_without_a_library_can_prepare_bootstrap_quarantine(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, registry = build_library(root)
            with patch('library_custodian.discovery.Fetcher', DownloadFetcher):
                report = discover(None, registry, root / 'state', root / 'quarantine', download=True)
            self.assertEqual(report['counts']['downloaded_to_quarantine'], 1)
            self.assertEqual(len(list((root / 'quarantine').rglob('*.intake.json'))), 1)


if __name__ == '__main__':
    unittest.main()
