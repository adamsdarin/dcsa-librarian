from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from library_custodian.runner import write_reports, run_scheduled_job, EXIT_SOURCE_ERROR
from library_custodian.status import scan_status


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.schedule = self.root / 'schedule.json'
        self.registry = self.root / 'registry.json'
        self.schedule.write_text(json.dumps(dict(timezone='UTC', jobs=[dict(id='monthly', action='discover',
            local_times=['09:00'], days_of_month='1', sources=[])])))
        self.registry.write_text(json.dumps(dict(sources=[dict(id='one', enabled=True), dict(id='two', enabled=True)])))
        self.summary = dict(job_id='monthly', ran_at='2026-09-01T09:01:00+00:00', library_root=str(self.root),
            sources_scanned=['one', 'two'], sources_errored=[], manifest_checked=True,
            findings=dict(changed=[], new_urls=[], candidates=[]),
            registry_sha256=hashlib.sha256(self.registry.read_bytes()).hexdigest())

    def status(self, now='2026-09-15T12:00:00+00:00'):
        return scan_status(self.schedule, self.registry, self.root/'state', self.root, datetime.fromisoformat(now))['jobs'][0]

    def test_missing_record_is_unknown_and_current_complete_record_passes(self):
        self.assertEqual(self.status()['status'], 'unknown')
        write_reports(self.root/'state', self.summary, 0)
        self.assertEqual(self.status()['status'], 'current')
        self.assertEqual(self.status('2026-10-01T10:00:00+00:00')['status'], 'overdue')

    def test_partial_registry_change_and_wrong_library_do_not_clear(self):
        self.summary['sources_scanned'] = ['one']
        write_reports(self.root/'state', self.summary, 0)
        self.assertEqual(self.status()['status'], 'incomplete')
        self.summary['sources_scanned'] = ['one', 'two']
        self.summary['registry_sha256'] = 'outdated'
        write_reports(self.root/'state', self.summary, 0)
        self.assertEqual(self.status()['status'], 'needs_review')
        self.summary['library_root'] = str(self.root/'other')
        write_reports(self.root/'state', self.summary, 0)
        self.assertEqual(self.status()['status'], 'unknown')

    def test_failed_or_skipped_job_not_counted_as_a_fresh_scan(self):
        write_reports(self.root/'state', self.summary, 1)
        self.assertEqual(self.status()['status'], 'failed')
        self.summary['skipped'] = 'period_already_satisfied'
        write_reports(self.root/'state', self.summary, 0)
        self.assertEqual(self.status()['status'], 'needs_review')

    def test_future_or_naive_timestamps_rejected(self):
        self.summary['ran_at'] = '2027-01-01T12:00:00+00:00'
        write_reports(self.root/'state', self.summary, 0)
        self.assertEqual(self.status()['status'], 'unknown')
        with self.assertRaises(ValueError):
            scan_status(self.schedule, self.registry, self.root/'state', self.root, datetime(2026,9,15))

    def test_empty_or_unverified_source_cannot_end_as_success(self):
        for defect in ({'documents_seen': 0}, {'verification_errors': ['failed check']}, {'unverified_documents': ['source']}):
            source = dict(source_id='one', status='ok', pages_scanned=1, documents_seen=1)
            source.update(defect)
            report = dict(run_id='synthetic', manifest_checked=True, counts={}, sources=[source])
            with patch('library_custodian.runner.discover', return_value=report):
                summary, code = run_scheduled_job('monthly', self.schedule, self.root, self.registry,
                    self.root/'state', self.root/'quarantine', now=datetime(2026,9,1,10,tzinfo=timezone.utc))
            self.assertEqual(code, EXIT_SOURCE_ERROR)
            self.assertEqual(summary['sources_errored'], ['one'])


if __name__ == '__main__': unittest.main()
