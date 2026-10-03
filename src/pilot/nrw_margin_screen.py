"""Screen exact-vote margins after nrw_runoffs.py; no gender inference.
Run: python src/pilot/nrw_margin_screen.py
"""
import csv
import json
from pathlib import Path

base = Path('outputs/nrw-runoff-audit')
audit = json.loads((base / 'audit.json').read_text())
if any(not r['valid'] for r in audit):
    raise ValueError('Resolve failed source audits before margin screening')
results = []
for record in audit:
    lines = (base / f"{record['code']}.txt").read_text(encoding='utf-8-sig').splitlines()
    start = lines.index('davon entfielen auf:') + 1
    rows = [r for r in csv.reader(lines[start:], delimiter=';') if len(r) > 3 and r[3].isdigit()]
    assert len(rows) == 2
    votes = [int(r[3]) for r in rows]
    total = sum(votes)
    assert total == record['runoff_valid_votes']
    results.append({'municipality_source_code': record['code'], 'source_url': record['url'],
                    'absolute_margin_pp': abs(votes[0]-votes[1])/total*100,
                    'valid_votes': total, 'mixed_gender_status': 'unverified'})
results.sort(key=lambda r: r['absolute_margin_pp'])
summary = {'validated_runoff_events': len(results),
           'inclusive_absolute_margin_counts': {str(h): sum(r['absolute_margin_pp'] <= h for r in results) for h in [1, 2, 5, 10]},
           'scope': 'All gender combinations, NRW district-municipality runoffs in 2020; not an RDD sample'}
(base / 'margin-screen.json').write_text(json.dumps({'summary': summary, 'events': results}, indent=2))
print(json.dumps(summary, indent=2))
