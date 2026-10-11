"""National structural inventory and separate Niedersachsen 2021 metadata audit.

Run from repository root: python src/pilot/national_scale_expansion.py
No public finalist names or predictions; no certified sample or pooled effects.
"""
import csv, hashlib, json, re, subprocess
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from cohort_expansion import SOURCE, SOURCE_SHA
from cohort_expansion_national import notice_key, national_day, municipal_match
from federal_procurement import csv_rows, verified_archive
from nrw_2025_validation import csv_write
import bavaria_bounded_route as ted

DOC = Path('docs/feasibility')
RAW = Path('data/raw/national-scale-expansion-2026-10-11')
OUT = Path('outputs/national-scale-expansion-2026-10-11')

def integer(value):
    if value in ('', 'NA', None):
        return None
    n = Decimal(value)
    if not n.is_finite() or n != n.to_integral_value():
        raise ValueError('Non-integer source value')
    return int(n)


def screen(group):
    """Reconcile complete decisive rounds; no gender/name selection."""
    def one(field):
        values = {r[field] for r in group}
        if len(values) != 1:
            raise ValueError('Conflicting ' + field)
        return next(iter(values))
    if one('election_type') not in ('Bürgermeisterwahl', 'Oberbürgermeisterwahl'):
        return None, 'association_office'
    if any('Landrat' in r['office_type'] for r in group):
        return None, 'county_office'
    if any(r[f] == 'TRUE' for r in group for f in
           ('flag_superseded', 'flag_shared_ags', 'flag_decisive_round_missing')):
        return None, 'source_quality_flag'
    sw = one('has_stichwahl')
    if sw not in ('TRUE', 'FALSE'):
        return None, 'unknown_round'
    suffix = 'sw' if sw == 'TRUE' else 'hw'
    when = one('election_date_sw') if suffix == 'sw' else one('election_date')
    if not when or not '2018-01-01' <= when <= '2025-12-31':
        return None, 'outside_2018_2025'
    pair = [r for r in group if integer(r['candidate_votes_sw']) is not None] if suffix == 'sw' else group
    if len(pair) != 2 or any(integer(r['n_candidates_' + suffix]) != 2 for r in pair):
        return None, 'not_complete_two_candidate_round'
    votes = [integer(r['candidate_votes_' + suffix]) for r in pair]
    if any(v is None or v < 0 for v in votes) or sum(votes) <= 0 or votes[0] == votes[1]:
        return None, 'invalid_or_tied_votes'
    if suffix == 'hw' and any(integer(r['valid_votes']) != sum(votes) for r in pair):
        return None, 'valid_votes_do_not_reconcile'
    winners = [r for r in group if r['is_winner'] == 'TRUE']
    if len(winners) != 1 or winners[0] not in pair:
        return None, 'winner_not_unique_in_pair'
    if sorted(integer(r['candidate_rank_' + suffix]) or 0 for r in pair) != [1, 2]:
        return None, 'invalid_ranks'
    if integer(winners[0]['candidate_rank_' + suffix]) != 1 or integer(winners[0]['candidate_votes_' + suffix]) != max(votes):
        return None, 'winner_votes_disagree'
    for r, v in zip(pair, votes):
        share = r['candidate_voteshare_' + suffix]
        if not share or abs(float(share) - v / sum(votes)) > .0001:
            return None, 'share_disagrees'
    return {'state': one('state'), 'ags': one('ags'), 'municipality': one('ags_name'),
            'first_date': one('election_date'), 'decisive_date': when,
            'round': 'runoff' if suffix == 'sw' else 'first', 'valid_votes': sum(votes),
            'absolute_margin_pp': float(Decimal(100) * abs(votes[0] - votes[1]) / sum(votes)),
            'both_names_available': all(r['candidate_name'] for r in pair),
            'candidates': [{'name': r['candidate_name'], 'votes': v,
                            'winner': r['is_winner'] == 'TRUE'} for r, v in zip(pair, votes)]}, None



def load_frame():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('GERDA source changed')
    groups = defaultdict(list)
    for row in csv.DictReader(SOURCE.open(newline='', encoding='utf8')):
        groups[(row['state'], row['ags'], row['election_date'], row['election_type'])].append(row)
    records, reasons = [], Counter()
    for group in groups.values():
        try:
            record, reason = screen(group)
        except (ValueError, TypeError, ArithmeticError) as error:
            record, reason = None, 'schema_error:' + str(error)
        if record:
            records.append(record)
        else:
            reasons[reason] += 1
    close = sorted([r for r in records if r['absolute_margin_pp'] <= 5], key=lambda r: (r['state'], r['decisive_date'], r['ags']))
    selected = [r for r in close if r['state'] == '03' and r['decisive_date'][:4] == '2021']
    if len(selected) != 18 or len({r['ags'] for r in selected}) != 18:
        raise ValueError('Prespecified Niedersachsen cohort changed')
    return records, close, selected, reasons


def validate_page(event, pages):
    matches = [(i + 1, p) for i, p in enumerate(pages) if re.search(r'Schlüssel:\s*' + event['ags'][2:] + r'\b', p)]
    if len(matches) != 1:
        raise ValueError('Official municipality page missing or ambiguous')
    page_no, page = matches[0]
    if 'Bürgermeister/Bürgermeisterin' not in page or 'kann als gewählt gelten:' not in page:
        raise ValueError('Unexpected office or nondecisive official page')
    total = re.search(r'D\s+Gültige Stimmen\s+(\d+)\b', page)
    if not total or int(total[1]) != event['valid_votes']:
        raise ValueError('Official valid total disagrees')
    found = []
    lines = page.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r'^\s*([12])\s{2,}(.+?)(?:\s{2,}\S.*|\s*)$', line)
        if not m:
            continue
        votes = next((v for text in lines[i + 1:i + 4] if (v := re.match(r'^\s*(\d+)\s+(\d+\.\d+)\s*$', text))), None)
        if not votes:
            raise ValueError('Official candidate vote row missing')
        found.append({'name': m[2].strip(), 'votes': int(votes[1])})
    key = lambda name: ''.join(name.casefold().split())
    expected = {(key(c['name']), c['votes']) for c in event['candidates']}
    if len(found) != 2 or {(key(c['name']), c['votes']) for c in found} != expected:
        raise ValueError('Official candidate identities or votes disagree: ' + event['ags'])
    winner = max(found, key=lambda c: c['votes'])['name']
    # The declaration lists given name before family name; strip academic titles
    # only for this explicit declaration-to-table identity comparison.
    declaration = page.split('kann als gewählt gelten:', 1)[1].splitlines()[1].strip()
    family, given = winner.split(',', 1)
    plain = lambda value: key(re.sub(r'\b(?:Prof\.|Dr\.)', '', value))
    if not plain(given + family) in plain(declaration):
        raise ValueError('Official declared winner disagrees')
    return page_no


def niedersachsen_aliases(events):
    normalized = [dict(e, municipality=re.sub(r', Stadt$', '', e['municipality'])) for e in events]
    return ted.aliases(normalized)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    protocol = json.loads((RAW / 'protocol-before-discovery.json').read_text())
    if hashlib.sha256(Path(protocol['artifact']).read_bytes()).hexdigest() != protocol['sha256']:
        raise ValueError('Pinned protocol changed')
    records, close, selected, reasons = load_frame()
    counts = Counter(r['ags'] for r in close)
    public = [{k: r[k] for k in ('state', 'ags', 'municipality', 'first_date', 'decisive_date', 'round', 'valid_votes', 'absolute_margin_pp', 'both_names_available')} | {'elections_for_municipality_in_screen': counts[r['ags']], 'state_return_numbers_verified_in_this_phase': r in selected, 'presentation_review_complete': False, 'main_study_eligibility_certified': False} for r in close]
    csv_write(DOC / 'national-close-election-inventory.csv', public)
    matrix = []
    for state, year in sorted({(r['state'], r['decisive_date'][:4]) for r in records}):
        rs = [r for r in records if r['state'] == state and r['decisive_date'][:4] == year]
        cs = [r for r in rs if r['absolute_margin_pp'] <= 5]
        matrix.append({'state': state, 'election_year': year, 'structural_pairs': len(rs), 'pairs_within_5pp': len(cs), 'both_names_available_within_5pp': sum(r['both_names_available'] for r in cs), 'distinct_municipalities_within_5pp': len({r['ags'] for r in cs}), 'certified_main_study_elections': 0})
    csv_write(DOC / 'national-state-year-expansion-matrix.csv', matrix)
    official = json.loads((RAW / 'official-retrieval.json').read_text())['sources']
    pages = {}
    for pin in official:
        source = Path(pin['artifact'])
        if hashlib.sha256(source.read_bytes()).hexdigest() != pin['sha256']:
            raise ValueError('Official PDF changed')
        pages[pin['round']] = subprocess.run(['pdftotext', '-layout', str(source), '-'], check=True, capture_output=True, text=True).stdout.split('\f')
    verification = []
    for event in selected:
        page = validate_page(event, pages[event['round']])
        pin = next(p for p in official if p['round'] == event['round'])
        verification.append({'ags': event['ags'], 'municipality': event['municipality'], 'decisive_date': event['decisive_date'], 'round': event['round'], 'absolute_margin_pp': event['absolute_margin_pp'], 'identities_votes_total_declared_winner_agree': True, 'source_page': page, 'url': pin['url'], 'sha256': pin['sha256'], 'source_status': 'state_transmitted_provisional_return_not_legal_certification'})
    csv_write(DOC / 'niedersachsen-2021-official-verification.csv', verification)
    (OUT / 'selected-elections.json').write_text(json.dumps(selected, indent=2, ensure_ascii=False) + '\n')
    export_root = Path('data/raw/cohort-expansion-2026-10-11/national-csv')
    pins = [p for p in json.loads((export_root / 'retrieval.json').read_text())['exports'] if p['period'].startswith('2025-')]
    if {p['period'] for p in pins} != {'2025-01', '2025-02', '2025-03'}:
        raise ValueError('Incomplete Q1 metadata coverage')
    addendum = json.loads((RAW / 'alias-addendum-before-replay.json').read_text())
    if hashlib.sha256(Path(addendum['artifact']).read_bytes()).hexdigest() != addendum['sha256']:
        raise ValueError('Pinned alias correction changed')
    aliases = niedersachsen_aliases(selected)
    calls, by_ags, seen = [], defaultdict(list), set()
    types, dispositions = Counter(), Counter()
    for pin in pins:
        with verified_archive(export_root, pin) as archive:
            buyers = defaultdict(list)
            for row in csv_rows(archive, 'organisation.csv'):
                if row['organisationRole'] == 'buyer':
                    buyers[notice_key(row)].append(row)
            for row in csv_rows(archive, 'notice.csv'):
                key = notice_key(row)
                if key in seen:
                    raise ValueError('Duplicate monthly notice/version')
                seen.add(key)
                ags, reason = municipal_match(buyers.get(key, []), aliases)
                dispositions[reason] += 1
                if not ags:
                    continue
                day = national_day(row['publicationDate'])
                if not '2025-01-01' <= day <= '2025-03-31':
                    raise ValueError('Outside fixed late-term quarter')
                types[row['noticeType']] += 1
                if row['noticeType'] != 'cn-standard':
                    continue
                unit = {'ags': ags, 'national_notice_identifier': key[0], 'version': key[1], 'national_publication_day_berlin': day, 'procedure_identifier_source': row['procedureIdentifier'], 'buyer_name_source': buyers[key][0]['organisationName'], 'source_export_file': pin['file'], 'source_export_sha256': pin['sha256'], 'metadata_only': True, 'original_call_verified': False}
                calls.append(unit); by_ags[ags].append(unit)
    # A CSV with a header remains reproducible when there are no matched calls.
    if calls:
        csv_write(DOC / 'niedersachsen-2021-national-call-discovery.csv', calls)
    else:
        (DOC / 'niedersachsen-2021-national-call-discovery.csv').write_text('ags,national_notice_identifier,metadata_only\n')
    inventory = []
    for event in selected:
        cs = by_ags[event['ags']]
        inventory.append({'ags': event['ags'], 'municipality': event['municipality'], 'decisive_date': event['decisive_date'], 'absolute_margin_pp': event['absolute_margin_pp'], 'official_result_numbers_verified': True, 'observation_window': '2025Q1_late_term_separate_cohort', 'national_call_notices': len(cs), 'calls_with_procedure_identifier': sum(bool(c['procedure_identifier_source']) for c in cs), 'distinct_nonmissing_procedure_identifiers': len({c['procedure_identifier_source'] for c in cs if c['procedure_identifier_source']}), 'primary_presentation_review': 'not_started', 'supported_tender_count_outcomes': 0, 'independent_second_coding': False, 'main_study_eligibility_certified': False})
    csv_write(DOC / 'niedersachsen-2021-linked-acquisition-inventory.csv', inventory)
    prior = list(csv.DictReader((DOC / 'expanded-election-acquisition-frame.csv').open()))
    combined = [dict(r, observation_window='following_year_Q1') for r in prior]
    for r in inventory:
        combined.append({'cohort': 'Niedersachsen 2021', 'ags': r['ags'], 'municipality': r['municipality'], 'pair_status': 'unreviewed_in_this_cohort_batch', 'female_presented_winner': '', 'original_q1_called_procedures': 0, 'candidate_tender_statistics': 0, 'known_mixed_with_supported_count_inventory': False, 'independent_second_coding': False, 'main_study_eligibility_certified': False, 'observation_window': r['observation_window']})
    csv_write(DOC / 'broader-election-acquisition-frame.csv', combined)
    summary = {'checked_on': '2026-10-11', 'source_sha256': SOURCE_SHA, 'protocol_sha256': protocol['sha256'], 'alias_addendum_sha256': addendum['sha256'], 'national_screen_start': '2018-01-01', 'national_screen_end': '2025-12-31', 'national_structural_pairs': len(records), 'national_close_elections': len(close), 'national_close_distinct_municipalities': len(counts), 'national_close_elections_both_names_available': sum(r['both_names_available'] for r in close), 'national_repeated_municipalities': sum(n > 1 for n in counts.values()), 'new_cohort_elections': len(selected), 'new_cohort_official_numbers_verified': len(verification), 'prior_acquisition_frame_elections': len(prior), 'combined_acquisition_frame_elections': len(prior) + len(selected), 'combined_acquisition_distinct_municipalities': len({r['ags'] for r in prior} | {r['ags'] for r in selected}), 'national_notice_rows_inspected': len(seen), 'matched_notice_type_counts': dict(types), 'national_call_notices': len(calls), 'elections_with_national_calls': sum(bool(v) for v in by_ags.values()), 'call_notices_without_procedure_identifiers': sum(not c['procedure_identifier_source'] for c in calls), 'distinct_nonmissing_procedure_identifiers': len({c['procedure_identifier_source'] for c in calls if c['procedure_identifier_source']}), 'reused_csv_bytes': sum(p['bytes'] for p in pins), 'additional_procurement_download_bytes': 0, 'official_pdf_bytes': sum(p['bytes'] for p in official), 'new_supported_mixed_count_elections': 0, 'prior_supported_mixed_count_elections': 4, 'certified_main_study_elections': 0, 'pooled_effects_estimated': False, 'pages_deployed': False, 'source_exclusion_counts': dict(reasons), 'municipal_match_dispositions': dict(dispositions), 'warning': 'Structural leads and metadata, not a census or certified causal sample. Late-term 2025Q1 stays separate; election assignment and turnover remain unverified.'}
    (DOC / 'national-scale-expansion-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (DOC / 'niedersachsen-2021-source-manifest.json').write_text(json.dumps({'official_sources': official, 'reused_national_exports': pins}, indent=2) + '\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('source_exclusion_counts', 'municipal_match_dispositions')}, indent=2))


if __name__ == '__main__':
    main()
