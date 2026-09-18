import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from library_custodian.schedule import Job, confirm_period, period_satisfied, record_period_satisfied


class PeriodReviewTests(unittest.TestCase):
    def test_match_and_legacy_marker_do_not_suppress_polling_but_review_does(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); state=root/'state'; library=root/'library'
            registry=root/'registry.json'; registry.write_text('{}')
            job=Job('voi','', 'discover', ('09:00',), '28-31,1-3', (), 'month', 'voi', '')
            record_period_satisfied(state,job,'2026-09',{'satisfied_by':['https://www.dcsa.mil/voi-2016.pdf']})
            self.assertFalse(period_satisfied(state,job,'2026-09',library,registry))
            artifact=root/'issue.txt'; artifact.write_text('Synthetic September issue review evidence')
            receipt=root/'review.json'
            data=dict(source_uri='https://www.dcsa.mil/voi.pdf',source_artifact='issue.txt',
                source_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(), reviewed_by='test',
                reviewed_utc='2026-09-30T12:00:00Z',issue_locator='Synthetic issue heading',review_basis='Synthetic full-source review',
                issue_period_verified=True,source_period='2026-09')
            receipt.write_text(json.dumps(data))
            confirm_period(state,job,'2026-09',receipt,registry,library)
            self.assertTrue(period_satisfied(state,job,'2026-09',library,registry))
            self.assertFalse(period_satisfied(state,job,'2026-09',root/'other',registry))
            self.assertFalse(period_satisfied(state,job,'2026-10',library,registry))
            retained=next((state/'period-evidence').glob('*.bin')); retained.write_text('changed')
            self.assertFalse(period_satisfied(state,job,'2026-09',library,registry))
            data['source_period']='2026-08'; receipt.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'period'):
                confirm_period(state,job,'2026-09',receipt,registry,library)
