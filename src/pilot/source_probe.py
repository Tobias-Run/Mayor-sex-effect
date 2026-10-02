"""Small source-access probe; not a research sample or treatment estimator.

Run from the repository root: python src/pilot/source_probe.py
Uses Python's standard library. Saves fetched responses under ignored outputs/.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import urllib.error
import urllib.request
from datetime import datetime, timezone

OUT = Path('outputs/source-probe')
OUT.mkdir(parents=True, exist_ok=True)
manifest = []


def fetch(url, filename, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    headers = {'User-Agent': 'Mayor-sex-effect research source probe'}
    if body is not None:
        headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
        manifest.append({'url': url, 'request': payload, 'status': response.status,
                         'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                         'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                         'file': filename})
    (OUT / filename).write_bytes(data)
    if not data:
        raise ValueError(f'Empty response from {url}; not a valid downloaded record')
    return data


def election_probe(code):
    url = ('https://www.wahlergebnisse.nrw/kommunalwahlen/2020/aktuell/'
           f'txtdateien/b{code}kw2000.txt')
    text = fetch(url, f'nrw-{code}.txt').decode('utf-8-sig')
    lines = text.splitlines()
    start = lines.index('davon entfielen auf:') + 1
    rows = list(csv.reader(io.StringIO('\n'.join(lines[start:])), delimiter=';'))
    candidates = [r for r in rows if len(r) >= 4 and r[1].isdigit()]
    valid = next(csv.reader([next(x for x in lines if x.startswith('Gültige Stimmen;'))], delimiter=';'))
    runoff = [(r[0], int(r[3])) for r in candidates if r[3].isdigit()]
    if len(runoff) != 2:
        raise ValueError(f'{code}: expected exactly two runoff candidates')
    if sum(v for _, v in runoff) != int(valid[3]):
        raise ValueError(f'{code}: runoff vote counts do not reconcile')
    if sum(int(r[1]) for r in candidates) != int(valid[1]):
        raise ValueError(f'{code}: first-round counts do not reconcile')
    return {'municipality_code': code, 'first_round_candidates': len(candidates),
            'runoff_valid_votes': int(valid[3]), 'counts_reconciled': True,
            'gender_verified': False, 'term_dates_verified': False}


summary = {'elections': [], 'ted': {}}
try:
    for code in ['154036', '154004', '158024']:
        summary['elections'].append(election_probe(code))
    query = ('buyer-country = DEU AND buyer-name ~ Kleve AND '
             'publication-date >= 20210101 AND publication-date <= 20241231')
    payload = {'query': query, 'fields': ['publication-number', 'publication-date',
               'buyer-name', 'notice-type'], 'page': 1, 'limit': 10, 'scope': 'ALL'}
    data = json.loads(fetch('https://api.ted.europa.eu/v3/notices/search', 'ted.json', payload))
    summary['ted'] = {'query': query, 'total_notice_count': data.get('totalNoticeCount'),
                      'returned_notice_count': len(data.get('notices', [])),
                      'timed_out': data.get('timedOut'),
                      'interpretation': 'Name-search notices, not municipal contract counts'}
    if data.get('timedOut'):
        raise ValueError('TED search timed out; count is not established')
finally:
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
