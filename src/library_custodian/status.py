"""Read-only acquisition freshness; no network or invented successful scans."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from .schedule import expand_days, load_schedule, period_satisfied, period_key


def last_due(job, now):
    allowed = set(range(1, 32)) if job.days_of_month == '*' else {int(x) for x in expand_days(job.days_of_month).split(',')}
    for back in range(63):
        day = (now - timedelta(days=back)).date()
        if day.day not in allowed:
            continue
        candidates = [datetime.combine(day, datetime.strptime(value, '%H:%M').time(), now.tzinfo) for value in job.local_times]
        due = [value for value in candidates if value <= now]
        if due:
            return max(due)
    raise ValueError('No scheduled due time found')


def scan_status(schedule_path, registry_path, state_dir, library_root, now=None):
    schedule = load_schedule(schedule_path)
    zone = timezone.utc if schedule.timezone_name == 'UTC' else ZoneInfo(schedule.timezone_name)
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('Status check time requires a timezone')
    now = now.astimezone(zone)
    registry = json.loads(registry_path.read_text(encoding='utf-8-sig'))
    enabled = {s['id'] for s in registry['sources'] if s.get('enabled', True)}
    registry_hash = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    rows = []
    for job in schedule.jobs:
        due = last_due(job, now)
        row = {'job_id': job.id, 'action': job.action, 'due_at': due.isoformat(), 'status': 'unknown'}
        try:
            record = json.loads((state_dir / 'reports' / f'{job.id}-latest.json').read_text(encoding='utf-8-sig'))
            ran = datetime.fromisoformat(record['ran_at'])
            if ran.tzinfo is None or record.get('job_id') != job.id:
                raise ValueError('Invalid run identity/time')
            row['ran_at'] = ran.isoformat()
            if record.get('library_root') is None or Path(record['library_root']).resolve() != library_root.resolve():
                row.update(status='unknown', reason='Run did not check this library')
            elif ran > now + timedelta(minutes=5):
                row.update(status='unknown', reason='Run timestamp is in the future')
            elif record.get('skipped'):
                # A skip is not a new source check. Keep it visible until the
                # original scan and period evidence are verified by the owner.
                confirmed = period_satisfied(state_dir, job, period_key(job, due), library_root, registry_path)
                row.update(status='current' if confirmed else 'needs_review',
                           reason='Reviewed issue-period evidence verified' if confirmed else 'Skipped poll requires original period evidence')
            elif record.get('exit_code') not in (0, 3):
                row.update(status='failed', reason='Last job did not finish successfully')
            elif ran < due:
                row.update(status='overdue', reason='No completed run at or after the latest due time')
            elif job.action == 'doctor':
                row['status'] = 'current' if record.get('library_ready') is True else 'failed'
            else:
                expected = (set(job.sources) if job.sources else enabled)
                seen = set(record.get('sources_scanned', []))
                if record.get('registry_sha256') != registry_hash:
                    row.update(status='needs_review', reason='Source registry changed or run lacks registry binding')
                elif not expected or seen != expected or record.get('sources_errored') or record.get('manifest_checked') is not True:
                    row.update(status='incomplete', reason='Source or manifest coverage is incomplete')
                else:
                    row.update(status='current', source_count=len(seen),
                               findings_pending=bool(any(record.get('findings', {}).values())))
        except (OSError, ValueError, KeyError, TypeError):
            row.update(status='unknown', reason='No valid structured run record')
        rows.append(row)
    return {'status': 'current' if all(row['status'] == 'current' for row in rows) else 'attention_required', 'jobs': rows}
