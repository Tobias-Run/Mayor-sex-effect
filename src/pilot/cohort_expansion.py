"""Bounded Brandenburg expansion; retain all labels and unmatched elections.

No candidate names or annotations are written to public ledgers. Acquisition
and replay use a pinned protocol, official results, and complete capped TED
queries. This creates an acquisition frame, never a certified analysis sample.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.request import urlopen

import bavaria_bounded_route as ted
from html_tables import Tables
from nrw_2025_validation import csv_write, original_visible_text
from nrw_2025_reopening import name_key

ROOT = Path('data/raw/cohort-expansion-2026-10-11')
OUT = Path('outputs/cohort-expansion-2026-10-11')
DOC = Path('docs/feasibility')
SOURCE = Path('data/raw/bavaria-bounded-route/direct-source-checks/gerda-current-candidates.csv')
SOURCE_SHA = '7ab9425dc9b4b1625eadcd5ff001689cec72e32d5f278a5740a29c7b1e9212b1'
FIELDS = ['publication-number', 'publication-date', 'notice-identifier',
          'notice-version', 'procedure-identifier', 'notice-type', 'buyer-name',
          'buyer-city', 'buyer-legal-type', 'procedure-type',
          'previous-notice-id-proc', 'change-notice-version-identifier',
          'internal-identifier-proc', 'title-proc', 'contract-conclusion-date']


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
    if not when or not '2023-01-01' <= when <= '2025-12-31':
        return None, 'outside_2023_2025'
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


def frame():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('GERDA source changed')
    groups = defaultdict(list)
    with SOURCE.open(newline='') as f:
        for row in csv.DictReader(f):
            groups[(row['state'], row['ags'], row['election_date'], row['election_type'])].append(row)
    records, excluded = [], Counter()
    for group in groups.values():
        try:
            result, reason = screen(group)
        except (ValueError, TypeError, ArithmeticError) as error:
            result, reason = None, 'schema_or_parse_error:' + str(error)
        if result:
            records.append(result)
        else:
            excluded[reason] += 1
    selected = sorted([r for r in records if r['state'] == '12' and r['decisive_date'][:4] in ('2024', '2025') and r['absolute_margin_pp'] <= 5], key=lambda r: (r['decisive_date'], r['ags']))
    if len(selected) != 10 or len({r['ags'] for r in selected}) != 10:
        raise ValueError('Fixed ten-election frame changed')
    return records, selected, excluded


def official_url(event):
    ags = event['ags']
    if not re.fullmatch(r'12\d{6}', ags):
        raise ValueError('Unexpected Brandenburg AGS')
    code = ags[:5] + '0' + ags[5:] + ags[5:]
    day = ''.join(reversed(event['decisive_date'].split('-')))
    kind = 's' if event['round'] == 'runoff' else 'h'
    # Source-linked exception: the older Stahnsdorf page uses the 8-digit AGS.
    if ags == '12069604' and event['decisive_date'] == '2024-03-17':
        code = ags
    return 'https://wahlen.brandenburg.de/wahlen/de/kommunalwahlen/ergebnisse/buergermeisterwahlen/ergebnisse/~' + kind + '_' + day + '_' + code


def german_count(value):
    if not re.fullmatch(r'(?:\d+|\d{1,3}(?:\.\d{3})+)', value):
        raise ValueError('Invalid German vote count')
    return int(value.replace('.', ''))


def candidate_identity_key(value):
    # Explicit academic titles do not alter a person's full name. No initials,
    # shortened names, surname-only joins, or approximate spelling matches.
    return name_key(re.sub(r'\bDr\.\s*', '', value))


def validate_official(raw, event):
    text = raw.decode('utf-8')
    tables = Tables(); tables.feed(text)
    flat = [row for table in tables.tables for row in table]
    dates = [r[1] for r in flat if len(r) == 2 and r[0] == 'Wahltag']
    kinds = [r[1] for r in flat if len(r) == 2 and r[0] == 'Wahlart']
    cities = [r[1] for r in flat if len(r) == 2 and r[0] in ('Stadt', 'Gemeinde', 'amtsfr. Gemeinde')]
    expect_day = '.'.join(reversed(event['decisive_date'].split('-')))
    if dates != [expect_day] or kinds != ['Stichwahl' if event['round'] == 'runoff' else 'Hauptwahl'] or cities != [event['municipality']]:
        raise ValueError('Official date/round/municipality differs')
    valid = [german_count(r[1]) for r in flat if len(r) >= 2 and r[0] == 'Gültige Stimmen']
    candidates = [r for r in flat if len(r) == 5 and r[0].isdigit()]
    observed = {candidate_identity_key(r[1]): german_count(r[3]) for r in candidates}
    expected = {candidate_identity_key(c['name']): c['votes'] for c in event['candidates']}
    if len(candidates) != 2 or len(observed) != 2 or observed != expected or valid != [event['valid_votes']] or sum(observed.values()) != valid[0]:
        raise ValueError('Official full identities/vote vector/denominator differs')
    visible = original_visible_text(raw, 'official.html')
    winner = next(c['name'] for c in event['candidates'] if c['winner'])
    # Winner text must occur after the committee declaration, not just in a table.
    if 'Der Wahlausschuss stellte fest' not in visible:
        raise ValueError('No official committee declaration')
    declaration = visible.split('Der Wahlausschuss stellte fest', 1)[1]
    if candidate_identity_key(winner) not in candidate_identity_key(declaration) or 'gewählt worden ist' not in declaration:
        raise ValueError('Declared winner does not corroborate votes')
    return True


def official_sources(selected, download=False):
    path = ROOT / 'official-source-retrieval.json'
    pins = json.loads(path.read_text()) if path.exists() else {}
    statuses = {}
    for e in selected:
        key = e['ags'] + '-' + e['decisive_date'][:4]
        source_key = key + '-linked' if e['ags'] == '12069604' else key
        try:
            if source_key not in pins and download:
                url = official_url(e)
                with urlopen(url, timeout=40) as response:
                    raw = response.read(5 * 1024 * 1024 + 1)
                    if len(raw) > 5 * 1024 * 1024 or response.status != 200 or b'<html' not in raw.lower():
                        raise ValueError('Invalid bounded official response')
                    name = 'bb-' + source_key + '.html'
                    pins[source_key] = {'url': url, 'final_url': response.url, 'file': name,
                                 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                                 'retrieved_at_utc': datetime.now(timezone.utc).isoformat()}
                (ROOT / name).write_bytes(raw)
                path.write_text(json.dumps(pins, indent=2) + '\n')
            if source_key not in pins:
                raise ValueError('Official source not acquired')
            pin = pins[source_key]; raw = (ROOT / pin['file']).read_bytes()
            if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
                raise ValueError('Official source changed')
            validate_official(raw, e)
            (ROOT / ('bb-' + key + '.txt')).write_text(original_visible_text(raw, pin['file']))
            statuses[key] = {'official_pair_verified': True, 'official_source_status': 'exact_identity_votes_day_winner_verified', 'official_source_id': source_key}
        except Exception as error:
            statuses[key] = {'official_pair_verified': False, 'official_source_status': str(error), 'official_source_id': key if key in pins else ''}
        print(key, statuses[key]['official_source_status'], flush=True)
    return statuses, pins


def calls_query(events, year):
    cities = sorted({e['municipality'] for e in events})
    clauses = ' OR '.join('buyer-city = ' + json.dumps(c, ensure_ascii=False) for c in cities)
    return ('buyer-country = DEU AND (' + clauses + ') AND buyer-legal-type = la '
            'AND notice-type = cn-standard AND publication-date >= ' + str(year + 1) + '0101 '
            'AND publication-date <= ' + str(year + 1) + '0331')


def retained_query(query, path, download):
    ted.RAW = path; ted.FIELDS = FIELDS
    ted.MAX_PAGES = 6; ted.LIMIT = 250
    if not (path / 'retrieval.json').exists():
        if not download:
            return None, None
        ted.acquire(query)
    return ted.snapshot(query)


def main(download=False):
    ROOT.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    protocol_pin = json.loads((ROOT / 'protocol-before-acquisition.json').read_text())
    if hashlib.sha256(Path(protocol_pin['artifact']).read_bytes()).hexdigest() != protocol_pin['sha256']:
        raise ValueError('Pre-acquisition protocol changed')
    records, selected, excluded = frame()
    statuses, sources = official_sources(selected, download)
    cohorts = []
    for (state, year) in sorted({(r['state'], r['decisive_date'][:4]) for r in records}):
        rs = [r for r in records if (r['state'], r['decisive_date'][:4]) == (state, year)]
        cohorts.append({'state': state, 'decisive_year': year, 'screened_pairs': len(rs),
                        'pairs_with_two_names': sum(r['both_names_available'] for r in rs),
                        'pairs_within_5pp': sum(r['absolute_margin_pp'] <= 5 for r in rs),
                        'pairs_within_5pp_with_two_names': sum(r['absolute_margin_pp'] <= 5 and r['both_names_available'] for r in rs),
                        'official_census_completeness_verified': False})
    csv_write(DOC / 'cohort-expansion-source-availability.csv', cohorts)
    ledger, metadata, raw_calls, raw_context = [], {}, [], []
    for year in (2024, 2025):
        events = [e for e in selected if e['decisive_date'][:4] == str(year)]
        calls, call_pin = retained_query(calls_query(events, year), ROOT / ('calls-' + str(year)), download)
        mapping = ted.aliases(events)
        # Explicit source-observed municipal designation; no fuzzy stripping.
        if year == 2025:
            mapping[ted.normal_text('Stadt Velten - Die Bürgermeisterin')].add('12065332')
        matched = [dict(n, ags=ted.match_buyer(n, mapping)[0]) for n in calls or [] if ted.match_buyer(n, mapping)[0]]
        guids = sorted({n['procedure-identifier'] for n in matched})
        context, context_pin = [], None
        if guids:
            query = '(' + ' OR '.join('procedure-identifier = ' + json.dumps(g) for g in guids) + ') AND publication-date <= ' + str(year + 1) + '0930'
            context, context_pin = retained_query(query, ROOT / ('context-' + str(year)), download)
            if context is not None and any(n['procedure-identifier'] not in guids for n in context):
                raise ValueError('Unexpected procedure context')
        metadata[str(year)] = {'calls': call_pin, 'context': context_pin}
        raw_calls.extend(dict(n, election_year=year) for n in matched)
        raw_context.extend(dict(n, election_year=year) for n in context or [])
        for e in events:
            own = [n for n in matched if n['ags'] == e['ags']]
            ids = {n['procedure-identifier'] for n in own}
            own_context = [n for n in context or [] if n['procedure-identifier'] in ids]
            ledger.append({'ags': e['ags'], 'municipality': e['municipality'], 'election_year': year,
                           'decisive_date': e['decisive_date'], 'absolute_margin_pp': e['absolute_margin_pp'],
                           **statuses[e['ags'] + '-' + str(year)],
                           'call_issue_and_publication_window': str(year + 1) + '-01-01/' + str(year + 1) + '-03-31',
                           'indexed_result_cutoff': str(year + 1) + '-09-30',
                           'call_query_complete': calls is not None, 'indexed_exact_buyer_call_notices': len(own),
                           'provisional_call_procedures': len(ids),
                           'indexed_standard_result_notices': sum(n['notice-type'] == 'can-standard' for n in own_context),
                           'call_roots_verified': False, 'pair_presentation_status': 'not_reviewed',
                           'independent_second_coding': False, 'main_study_eligibility_certified': False})
    csv_write(DOC / 'brandenburg-expansion-election-inventory.csv', ledger)
    csv_write(DOC / 'brandenburg-expansion-official-source-manifest.csv', [{'source_id': key, **value} for key, value in sources.items()])
    (DOC / 'brandenburg-expansion-ted-request-manifests.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n')
    (OUT / 'selected-elections.json').write_text(json.dumps(selected, indent=2, ensure_ascii=False) + '\n')
    (OUT / 'matched-calls.json').write_text(json.dumps(raw_calls, indent=2, ensure_ascii=False) + '\n')
    (OUT / 'procedure-context.json').write_text(json.dumps(raw_context, indent=2, ensure_ascii=False) + '\n')
    summary = {'checked_on': '2026-10-11', 'selected_elections': len(ledger),
               'selection': 'All screened Brandenburg 2024/2025 decisive pairs within 5pp; no name, label, winner or procurement filter',
               'original_official_pairs_verified': sum(r['official_pair_verified'] for r in ledger),
               'indexed_exact_buyer_calls': len(raw_calls),
               'provisional_procedures': len({n['procedure-identifier'] for n in raw_calls}),
               'elections_with_provisional_calls': sum(bool(r['provisional_call_procedures']) for r in ledger),
               'elections_without_exact_call_match': sum(not r['provisional_call_procedures'] for r in ledger),
               'context_notice_types': dict(Counter(n['notice-type'] for n in raw_context)),
               'independent_second_coding_completed': False, 'certified_main_study_elections': 0,
               'pooled_with_nrw': False, 'causal_effect_estimated': False,
               'gerda_candidate_source_sha256': SOURCE_SHA, 'protocol_sha256': protocol_pin['sha256'],
               'structural_screen_exclusions_all_source_years': dict(excluded)}
    (DOC / 'brandenburg-expansion-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--download', action='store_true')
    main(parser.parse_args().download)
