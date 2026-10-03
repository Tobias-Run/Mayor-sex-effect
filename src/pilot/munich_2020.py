"""Retrieve and reconcile Munich's official 2020 mayoral results.
Run from repo root: python src/pilot/munich_2020.py
Standard library only; candidate data are written to ignored outputs.
"""
from html_tables import Tables
from pathlib import Path
import urllib.request
import json
import hashlib

out = Path('outputs/munich-2020'); out.mkdir(parents=True, exist_ok=True)
summary = []
for date in ['20200315', '20200329']:
    url = f'https://www.wahlen-muenchen.de/ergebnisse/{date}oberbuergermeisterwahl/index.html'
    with urllib.request.urlopen(url, timeout=30) as response: raw = response.read()
    (out / f'{date}.html').write_bytes(raw)
    parser = Tables(); parser.feed(raw.decode('utf-8'))
    table = next(t for t in parser.tables if t and t[0][:3] == ['Wahlvorschlag', 'Bewerbende', 'Stimmen'])
    count = lambda s: int(s.replace('.', ''))
    candidates = [{'nomination': r[0], 'candidate': r[1], 'votes': count(r[2])} for r in table[1:] if r[1]]
    valid = count(next(r[2] for r in table if r[0] == 'Gültige Stimmen'))
    assert sum(c['votes'] for c in candidates) == valid, 'Votes fail reconciliation'
    (out / f'{date}-candidates.json').write_text(json.dumps(candidates, ensure_ascii=False, indent=2))
    summary.append({'election_date': date, 'url': url, 'sha256': hashlib.sha256(raw).hexdigest(),
                    'candidates': len(candidates), 'valid_votes': valid, 'reconciled': True,
                    'gender_verified': False, 'actual_term_dates_verified': False})
(out / 'summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
