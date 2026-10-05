"""Bounded Bavaria register/TED availability audit; no new candidate labels.

Run at the repository root. --download acquires one capped TED query for the
31 named 2020 elections within 10 pp. Buyer text matches are provisional;
result publication dates never stand in for original competition dates.
Uses the optional analysis/requirements-feasibility.txt numerical environment.
"""
import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from bavaria_historical_register import NS, excel_date, read_sheet
from bavaria_ted_linkage import tender_count
from nrw_early_feasibility import gaussian_t_mde, verify_baseline

RAW = Path('data/raw/bavaria-bounded-route')
OUT = Path('outputs/bavaria-bounded-route')
DOC = Path('docs/feasibility')
URL = 'https://api.ted.europa.eu/v3/notices/search'
START, END = '20231101', '20260930'
MAX_PAGES, LIMIT = 6, 250
REGISTER_ROOT = RAW / 'direct-source-checks'
GERDA_CHECK_COMMIT = '176259ea551b12a56dcd0c15b168e0e6e608f59a'
REGISTER_SOURCES = [
    ('current-officeholders.xlsx',
     'https://www.statistik.bayern.de/mam/wahlen/kommunalwahlen/bgm/wahlergebnisse_mandatsr%C3%A4ger.xlsx',
     'ee4801b905b4dcd87f85cc1e7854d43e4ef243f67b2aa6fd2e01e3285270af07'),
    ('gerda-current-candidates.csv',
     f'https://media.githubusercontent.com/media/awiedem/german_election_data/{GERDA_CHECK_COMMIT}/data/mayoral_elections/final/mayoral_candidates.csv',
     '7ab9425dc9b4b1625eadcd5ff001689cec72e32d5f278a5740a29c7b1e9212b1'),
    ('gerda-current-readme.md',
     f'https://raw.githubusercontent.com/awiedem/german_election_data/{GERDA_CHECK_COMMIT}/data/mayoral_elections/final/README.md',
     'c2551c716eb1c7c08a6a9df8d899f35bfdb8759fc61f00e7f732e4d218224c4c'),
]
FIELDS = ['publication-number', 'publication-date', 'buyer-name', 'buyer-city',
          'buyer-legal-type', 'buyer-identifier', 'procedure-type',
          'procedure-identifier', 'notice-type', 'previous-notice-id-proc',
          'contract-conclusion-date', 'result-lot-identifier', 'identifier-lot',
          'received-submissions-type-code', 'received-submissions-type-val',
          'BT-759-LotResult', 'BT-142-LotResult']
PINS = {
    'outputs/bavaria-named-reports/recovered-screen-events.json':
        'da79491faaa958bae781d14a5d374ddfd3636bcd50a4345c9bee5c09efc0fbc9',
    'outputs/bavaria-register/screen-source-comparison.json':
        'af2f86a79ba740e00913fda0056719019c5804f5f4a1a7389ef62685d99eae3a',
    'outputs/bavaria-candidate-register/candidates.json':
        '6c95538382821c60aff9ca5bb3c0310c069e7e71f92987debf323a85da5b4f90',
    'outputs/bavaria-register/rounds.json':
        'f11574b7caaca876991dc8c1249333205d8602998b47fc8ca4adfddb5169c549',
}


def load_inputs():
    data = {}
    for path, expected in PINS.items():
        raw = Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Input changed: ' + path)
        data[path] = json.loads(raw)
    return list(data.values())


def semantic_digest(rows):
    canonical = '\n'.join(sorted(json.dumps(r, sort_keys=True) for r in rows))
    return hashlib.sha256(canonical.encode()).hexdigest()


def register_check(download=False):
    REGISTER_ROOT.mkdir(parents=True, exist_ok=True)
    for name, url, expected in REGISTER_SOURCES:
        path = REGISTER_ROOT / name
        if not path.exists() and download:
            with urlopen(url, timeout=45) as response:
                raw = response.read()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError('Register download differs from pinned version: ' + name)
            path.write_bytes(raw)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Register source changed: ' + name)
    old_path = Path('data/raw/gerda/mayoral_candidates.csv')
    if hashlib.sha256(old_path.read_bytes()).hexdigest() != '5cf7c8f7695cf17d3001ffe49ba5bb5a8f2800be8426754c1db3143b200fba0e':
        raise ValueError('Baseline GERDA candidate file changed')
    with old_path.open(newline='') as handle:
        old = [r for r in csv.DictReader(handle) if r['state'] == '09']
    with (REGISTER_ROOT / 'gerda-current-candidates.csv').open(newline='') as handle:
        new = [r for r in csv.DictReader(handle) if r['state'] == '09']
    historical = [r for r in new if '2020' <= r['election_year'] <= '2024']
    with ZipFile(REGISTER_ROOT / 'current-officeholders.xlsx') as archive:
        strings = [''.join(e.itertext()) for e in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        rows = read_sheet(archive, 'xl/worksheets/sheet1.xml', strings)
    if rows[1][1].get('I') != 'Amtsinhaber/in' or rows[1][1].get('J') != 'Geschlecht':
        raise ValueError('Current officeholder schema differs')
    municipal = [r for _,r in rows[2:] if r.get('C') in ('kreisfreie Stadt', 'kreisangehörige Gemeinde')
                 and r.get('A', '').isdigit()]
    if len({r['A'] for r in municipal}) != len(municipal):
        raise ValueError('Current registry contains multiple municipal officeholder rows')
    return dict(gerda_baseline_commit='030c1fb865ec4e6ef94d5dee2039edde081a0f5d',
                gerda_checked_commit=GERDA_CHECK_COMMIT,
                current_bavaria_rows=len(new), bavaria_rows_semantically_unchanged=semantic_digest(old)==semantic_digest(new),
                bavaria_semantic_sha256=semantic_digest(new), historical_2020_2024_rows=len(historical),
                historical_rows_with_names=sum(bool(r['candidate_name']) for r in historical),
                historical_rows_with_gender=sum(bool(r['candidate_gender']) for r in historical),
                gender_label_year_counts=dict(Counter(r['election_year'] for r in new if r['candidate_gender'])),
                current_officeholder_source_date=rows[0][1]['A'], current_municipal_officeholders=len(municipal),
                officeholder_election_years=dict(Counter(excel_date(r.get('F'))[:4] if r.get('F') else 'unknown'
                                                         for r in municipal)),
                historical_gender_transfers=0, losing_candidate_rows_in_current_officeholder_file=0)


def margin(event):
    rows = event['candidate_identity']['candidates']
    valid = event['candidate_identity']['valid_votes']
    if len(rows) != 2 or valid <= 0 or sum(r['votes'] for r in rows) != valid:
        raise ValueError('Named pair vote vector does not reconcile')
    return Decimal(100) * abs(rows[0]['votes'] - rows[1]['votes']) / valid


def city_name(event):
    return re.sub(r', (?:St|M|GKSt)$', '', event['municipality'])


def city_variants(event):
    name = city_name(event)
    variants = {name}
    # Declared query variants, not confirmed buyer identities or fuzzy matching.
    explicit = {
        'Mühldorf a.Inn': ['Mühldorf am Inn', 'Mühldorf a. Inn'],
        'Grafing b.München': ['Grafing bei München', 'Grafing b. München'],
        'Moosburg a.d.Isar': ['Moosburg an der Isar', 'Moosburg a.d. Isar'],
        'Lauf a.d.Pegnitz': ['Lauf an der Pegnitz', 'Lauf a.d. Pegnitz'],
        'Prien a.Chiemsee': ['Prien am Chiemsee', 'Prien a. Chiemsee'],
        'Weißenburg i.Bay.': ['Weißenburg in Bayern', 'Weißenburg i. Bay.'],
    }
    variants.update(explicit.get(name, []))
    return sorted(variants)


def query_for(events):
    cities = sorted({v for e in events for v in city_variants(e)})
    conditions = ' OR '.join('buyer-city = ' + json.dumps(c, ensure_ascii=False)
                             for c in cities)
    return (f'buyer-country = DEU AND ({conditions}) AND buyer-legal-type = la '
            f'AND notice-type = can-standard '
            f'AND publication-date >= {START} AND publication-date <= {END}')


def acquire(query):
    if (RAW / 'retrieval.json').exists():
        raise FileExistsError('Retain the existing snapshot; do not overwrite it')
    RAW.mkdir(parents=True, exist_ok=True)
    pages, ids, total = [], set(), None
    for page in range(1, MAX_PAGES + 1):
        payload = dict(query=query, fields=FIELDS, page=page, limit=LIMIT, scope='ALL')
        request = Request(URL, json.dumps(payload).encode(),
                          headers={'Content-Type': 'application/json'})
        with urlopen(request, timeout=40) as response:
            raw = response.read()
        result = json.loads(raw)
        if result.get('timedOut'):
            raise ValueError('TED query timed out; no complete snapshot')
        if total is None:
            total = result['totalNoticeCount']
            if total > MAX_PAGES * LIMIT:
                raise ValueError('Query exceeds the declared acquisition cap')
        if total != result['totalNoticeCount']:
            raise ValueError('Changing notice count during pagination')
        path = RAW / f'page-{page}.json'
        path.write_bytes(raw)
        pages.append(dict(file=path.name, sha256=hashlib.sha256(raw).hexdigest(),
                          bytes=len(raw), request=payload))
        for notice in result['notices']:
            number = notice['publication-number']
            if number in ids:
                raise ValueError('Duplicate notice across pages')
            ids.add(number)
        print(f'Acquired page {page}: {len(ids)}/{total} result notices', flush=True)
        if len(ids) == total:
            break
        if not result['notices']:
            raise ValueError('Incomplete pagination')
    if len(ids) != total:
        raise ValueError('Incomplete capped acquisition')
    metadata = dict(url=URL, query=query, fields=FIELDS, total_notice_count=total,
                    retrieved_at_utc=datetime.now(timezone.utc).isoformat(), pages=pages,
                    publication_window=[START, END], acquisition_cap=MAX_PAGES * LIMIT)
    (RAW / 'retrieval.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False)+'\n')


def snapshot(query):
    metadata = json.loads((RAW / 'retrieval.json').read_text())
    if metadata['query'] != query or metadata['fields'] != FIELDS:
        raise ValueError('Snapshot request changed')
    notices = []
    for page in metadata['pages']:
        raw = (RAW / page['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != page['sha256'] or len(raw) != page['bytes']:
            raise ValueError('Snapshot bytes changed')
        response = json.loads(raw)
        if response.get('timedOut') or response['totalNoticeCount'] != metadata['total_notice_count']:
            raise ValueError('Snapshot query incomplete')
        notices.extend(response['notices'])
    if len(notices) != metadata['total_notice_count'] or len({n['publication-number'] for n in notices}) != len(notices):
        raise ValueError('Missing or duplicate snapshot notices')
    return notices, metadata


def normal_text(value):
    return ' '.join(unicodedata.normalize('NFC', value).casefold().split())


def aliases(events):
    mapping = defaultdict(set)
    for event in events:
        for variant in city_variants(event):
            for prefix in ('Stadt ', 'Gemeinde ', 'Markt ', 'Kreisstadt '):
                mapping[normal_text(prefix + variant)].add(event['ags'])
    return mapping


def match_buyer(notice, mapping):
    # Multilingual labels are translations, not separate buyers. A joint or
    # ambiguous German buyer list cannot be assigned to one municipality.
    names = set(notice.get('buyer-name', {}).get('deu', []))
    if len(names) != 1:
        return None, 'missing_or_multiple_german_buyer_names'
    matches = mapping.get(normal_text(next(iter(names))), set())
    if len(matches) != 1:
        return None, 'unmatched_or_ambiguous_municipal_name'
    if notice.get('buyer-legal-type') != ['la']:
        return None, 'legal_type_not_single_local_authority'
    return next(iter(matches)), 'provisional_exact_municipal_name_and_local_authority'


def options(candidates):
    if len(candidates) != 2 or sum(c['winner'] for c in candidates) != 1:
        raise ValueError('Invalid candidate pair')
    winner = next(c for c in candidates if c['winner'])
    loser = next(c for c in candidates if not c['winner'])
    if any(c['official_title_presentation'] not in ('female', 'male', 'missing') for c in candidates):
        raise ValueError('Conflicting or unsupported presentation must remain unresolved')
    values = []
    for female_wins, labels in [(1, ('female', 'male')), (0, ('male', 'female'))]:
        if all(c['official_title_presentation'] in ('missing', label)
               for c, label in zip((winner, loser), labels)):
            values.append(female_wins)
    return values


def csv_write(path, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def run(download=False):
    baseline = verify_baseline()
    source_check = register_check(download)
    named, statewide, candidates, rounds = load_inputs()
    round_index = {r['source_row']: r for r in rounds}
    def source_margin(event):
        source = round_index[event['source_row']]
        if source['ags'] != event['ags'] or source['election_date'] != event['decisive_date']:
            raise ValueError('Structural pair source identity differs')
        return margin({'candidate_identity': {'candidates': source['candidate_slots'],
                                              'valid_votes': source['valid_votes']}})
    selected = sorted([e for e in named if margin(e) <= 10], key=lambda e: e['ags'])
    if len({e['ags'] for e in selected}) != len(selected):
        raise ValueError('Multiple selected elections in one municipality')
    query = query_for(selected)
    if download:
        acquire(query)
    notices, metadata = snapshot(query)
    grouped_candidates, grouped_notices = defaultdict(list), defaultdict(list)
    for candidate in candidates:
        grouped_candidates[candidate['ags']].append(candidate)
    mapping, exclusions = aliases(selected), Counter()
    local_records = []
    for notice in notices:
        ags, disposition = match_buyer(notice, mapping)
        if ags:
            grouped_notices[ags].append(notice)
            local_records.append(dict(ags=ags, buyer_match=disposition, source_fields=notice))
        else:
            exclusions[disposition] += 1
    matrix = []
    for event in selected:
        pair = grouped_candidates[event['ags']]
        possibilities = options(pair)
        if not possibilities:
            raise ValueError('Known same-presentation pair requires explicit exclusion review')
        labels = {c['official_title_presentation'] for c in pair}
        confirmed = labels == {'female', 'male'}
        subset = grouped_notices[event['ags']]
        counts = [tender_count(n) for n in subset]
        matrix.append(dict(ags=event['ags'], municipality=event['municipality'],
                           election_date=event['decisive_date'], absolute_margin_pp=str(margin(event)),
                           pair_status='mixed_official_titles' if confirmed else 'unresolved',
                           female_presented_winner=str(bool(possibilities[0])).lower() if confirmed else '',
                           provisional_municipal_result_notices=len(subset),
                           indexed_single_lot_total_tender_counts=sum(n is not None for n in counts),
                           indexed_single_lot_single_tender_counts=sum(n == 1 for n in counts),
                           publication_2024_notices=sum(n['publication-date'][:4] == '2024' for n in subset),
                           original_competition_window='not_verified', reporting_coverage='not_audited',
                           buyer_identity='provisional_text_and_type_match', independent_coding='not_completed',
                           main_sample_eligibility='pending', zero_count_meaning='query absence, not zero procurement'))
    bands, precision = [], []
    with (DOC / 'nrw-early-linkage-matrix.csv').open(newline='') as handle:
        nrw = list(csv.DictReader(handle))
    for cutoff in (1, 2, 5, 10):
        cohort = [e for e in selected if margin(e) <= cutoff]
        matched = [e for e in cohort if grouped_notices[e['ags']]]
        confirmed = [r for r in matrix if Decimal(r['absolute_margin_pp']) <= cutoff and r['pair_status'] == 'mixed_official_titles']
        general = [e for e in statewide if e['first_round_date'] == '2020-03-15' and source_margin(e) <= cutoff]
        bands.append(dict(cutoff_pp=cutoff, statewide_general_2020_structural_pairs=len(general),
                          named_general_2020_pairs=len(cohort), pairs_with_provisional_result_notices=len(matched),
                          confirmed_mixed_title_pairs=len(confirmed),
                          confirmed_female_wins=sum(r['female_presented_winner'] == 'true' for r in confirmed),
                          confirmed_female_losses=sum(r['female_presented_winner'] == 'false' for r in confirmed),
                          certified_main_study_elections=0))
        for scope, events in [('all_named', cohort), ('provisional_result_presence', matched)]:
            # Conditional maximal sample: every still-unknown pair is mixed;
            # known one-sided titles constrain which candidate could be female.
            opts = [options(grouped_candidates[e['ags']]) for e in events]
            nrw_rows = [r for r in nrw if Decimal(r['absolute_margin_pp']) <= cutoff and r['pair_status'] != 'same_public_presentation']
            n = len(opts) + len(nrw_rows)
            low = sum(min(o) for o in opts) + sum(r['female_presented_winner'] == 'true' for r in nrw_rows)
            high = sum(max(o) for o in opts) + sum(r['female_presented_winner'] != 'false' for r in nrw_rows)
            balanced = min(range(low, high+1), key=lambda k: abs(k-(n-k)))
            for alpha in (.05, .025):
                precision.append(dict(cutoff_pp=cutoff, bavaria_scope=scope,
                                      bavaria_conditional_max=len(opts), nrw_conditional_max=len(nrw_rows),
                                      pooled_conditional_max=n, feasible_min_female_wins=low,
                                      feasible_max_female_wins=high, best_balance_female_wins=balanced,
                                      best_balance_female_losses=n-balanced, alpha=alpha,
                                      gaussian_pooled_t_mde_sd=gaussian_t_mde(balanced,n-balanced,alpha)
                                      if balanced and n-balanced else '', target_power=.8,
                                      status='upper_bound_not_sample_or_rdd_power'))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'provisional-notices.json').write_text(json.dumps(local_records, indent=2, ensure_ascii=False)+'\n')
    csv_write(DOC / 'bavaria-bounded-linkage-matrix.csv', matrix)
    csv_write(DOC / 'bavaria-bounded-band-summary.csv', bands)
    csv_write(DOC / 'bavaria-nrw-conditional-precision.csv', precision)
    pins = [dict(artifact=p, sha256=h) for p,h in PINS.items()]
    for path in [DOC / 'nrw-early-linkage-matrix.csv', RAW / 'retrieval.json']:
        pins.append(dict(artifact=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    pins.append(dict(artifact='data/raw/gerda/mayoral_candidates.csv',
                     sha256='5cf7c8f7695cf17d3001ffe49ba5bb5a8f2800be8426754c1db3143b200fba0e'))
    for name, _, expected in REGISTER_SOURCES:
        pins.append(dict(artifact=str(REGISTER_ROOT / name), sha256=expected))
    csv_write(DOC / 'bavaria-bounded-input-hashes.csv', pins)
    summary = dict(generated_at_utc=datetime.now(timezone.utc).isoformat(),
                   election_inputs=list(PINS), named_pairs=len(named), queried_pairs=len(selected),
                   general_2020_structural_pairs=sum(e['first_round_date'] == '2020-03-15' for e in statewide),
                   calendar_2020_structural_pairs=sum(e['first_round_date'].startswith('2020') for e in statewide),
                   query_notice_count=len(notices), provisional_municipal_notices=len(local_records),
                   municipalities_with_provisional_results=sum(bool(grouped_notices[e['ags']]) for e in selected),
                   indexed_single_lot_total_tender_counts=sum(tender_count(r['source_fields']) is not None for r in local_records),
                   municipalities_with_indexed_total_tender_counts=sum(any(tender_count(n) is not None for n in grouped_notices[e['ags']])
                                                                      for e in selected),
                   exclusions=dict(exclusions), bands=bands, query_metadata=metadata,
                   main_study_elections_certified=0, new_candidate_labels=0,
                   independent_coding_completed=False, original_competition_dates_verified=False,
                   causal_effects_estimated=False, frozen_baseline_hashes_verified=baseline,
                   register_source_check=source_check)
    (DOC / 'bavaria-bounded-checkpoint.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n')
    if verify_baseline() != baseline:
        raise ValueError('Baseline verification changed')
    load_inputs()
    print(json.dumps({k:v for k,v in summary.items() if k not in ('query_metadata','bands')},indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true')
    run(parser.parse_args().download)
