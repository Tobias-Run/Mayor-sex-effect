"""Audit two further official Bavarian 2020 runoff archives.
Run: python src/pilot/additional_bavaria.py
No gender inference, term assignment or RDD eligibility determination.
"""
from pathlib import Path
import urllib.request
import json
import hashlib
from html_tables import Tables

SOURCES = {
    'augsburg': 'https://www.augsburg.de/fileadmin/user_upload/verwaltungswegweiser/buergeramt/wahlen/kommunalwahlen/2020/ob-stichwahl/index.html',
    'nuremberg': 'https://www.nuernberg.de/datenwahlen/ko2020/prod/wahl-2020-03-29/09564000/html5/Buergermeisterwahl_Bayern_15_Gemeinde_Stadt_Nuernberg.html',
}
out = Path('outputs/additional-bavaria'); out.mkdir(parents=True, exist_ok=True)
summary = []
number = lambda text: int(text.replace('.', ''))
for city, url in SOURCES.items():
    with urllib.request.urlopen(url, timeout=30) as response: raw = response.read()
    (out / f'{city}.html').write_bytes(raw)
    parser = Tables(); parser.feed(raw.decode('utf-8'))
    if city == 'augsburg':
        table = next(t for t in parser.tables if t and t[0][:2] == ['Kandidaten', 'Anzahl'])
        candidates = [{'label': r[0], 'votes': number(r[1])} for r in table[1:3]]
        valid = number(next(r[1] for r in table if r[0] == 'Gültige Stimmen'))
    else:
        table = next(t for t in parser.tables if t and 'Anzahl' in t[0])
        candidates = [{'label': r[1], 'votes': number(r[2])} for r in table[1:] if len(r) == 4]
        valid = number(next(r[1] for t in parser.tables for r in t if r and r[0] == 'gültige Stimmen'))
    assert len(candidates) == 2
    assert sum(c['votes'] for c in candidates) == valid
    (out / f'{city}-candidates.json').write_text(json.dumps(candidates, ensure_ascii=False, indent=2))
    summary.append({'city': city, 'election_date': '2020-03-29', 'url': url,
                    'valid_votes': valid, 'reconciled': True,
                    'absolute_margin_pp': abs(candidates[0]['votes']-candidates[1]['votes']) / valid * 100,
                    'gender_verified': False, 'term_dates_verified': False,
                    'sha256': hashlib.sha256(raw).hexdigest()})
(out / 'summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
