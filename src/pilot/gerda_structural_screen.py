"""Conservative candidate-pair screen of the pinned GERDA CSV.

Run from repo root: python src/pilot/gerda_structural_screen.py
Outputs are local and ignored. This is a feasibility screen, not sample approval.
Only complete two-person decisive rounds are considered; broad first-round
multi-candidate eligibility and each state's institutions still require review.
"""
import csv
import json
import hashlib
from collections import defaultdict, Counter
from pathlib import Path
from datetime import date
from decimal import Decimal

START = date(2020, 1, 1)
CUTOFF = date(2026, 10, 3)
ROOT = Path('data/raw/gerda')
OUT = Path('outputs/gerda-screen'); OUT.mkdir(parents=True, exist_ok=True)
rows = list(csv.DictReader((ROOT / 'mayoral_candidates.csv').open(encoding='utf-8-sig')))
metadata = json.loads((ROOT / 'retrieval.json').read_text())
assert hashlib.sha256((ROOT / 'mayoral_candidates.csv').read_bytes()).hexdigest() == metadata['sha256'], 'Source checksum changed'
groups = defaultdict(list)
for row in rows:
    groups[(row['state'], row['ags'], row['election_date'], row['election_type'])].append(row)


def integer(text):
    if text in ('', 'NA'): return None
    value = Decimal(text)
    if value != value.to_integral_value(): raise ValueError(f'Non-integer votes: {text}')
    return int(value)


def one_value(group, field):
    values = {r[field] for r in group}
    if len(values) != 1: raise ValueError(f'Conflicting {field}: {values}')
    return next(iter(values))


def screen(key, group):
    state, ags, first_date, kind = key
    if kind not in ('Bürgermeisterwahl', 'Oberbürgermeisterwahl'):
        return None, 'municipal_association_office'
    if any('Landrat' in r['office_type'] for r in group):
        return None, 'county_office_label'
    if any(r[f] == 'TRUE' for r in group for f in
           ('flag_superseded', 'flag_shared_ags', 'flag_decisive_round_missing')):
        return None, 'source_quality_flag'
    try:
        has_sw = one_value(group, 'has_stichwahl')
        if has_sw == 'TRUE':
            when = one_value(group, 'election_date_sw')
            if not when: return None, 'missing_runoff_date'
            pair = [r for r in group if integer(r['candidate_votes_sw']) is not None]
            vote_field, rank_field, share_field = 'candidate_votes_sw', 'candidate_rank_sw', 'candidate_voteshare_sw'
            declared_field = 'n_candidates_sw'
            round_label = 'runoff'
        elif has_sw == 'FALSE':
            when = first_date
            pair = group
            vote_field, rank_field, share_field = 'candidate_votes_hw', 'candidate_rank_hw', 'candidate_voteshare_hw'
            declared_field = 'n_candidates_hw'
            round_label = 'first'
        else:
            return None, 'unknown_round_structure'
        if not START <= date.fromisoformat(when) <= CUTOFF:
            return None, 'outside_screen_window'
        if len(pair) != 2: return None, 'not_complete_two_candidate_round'
        if any(integer(r[declared_field]) != 2 for r in pair):
            return None, 'candidate_count_not_two'
        if sum(r['is_winner'] == 'TRUE' for r in group) != 1:
            return None, 'winner_flag_not_unique'
        if sorted(integer(r[rank_field]) or 0 for r in pair) != [1, 2]:
            return None, 'invalid_final_rank'
        votes = [integer(r[vote_field]) for r in pair]
        if any(v is None or v < 0 for v in votes) or sum(votes) == 0:
            return None, 'missing_or_invalid_votes'
        winner = next(r for r in group if r['is_winner'] == 'TRUE')
        if winner not in pair or integer(winner[rank_field]) != 1:
            return None, 'winner_rank_disagrees'
        if votes[0] == votes[1]: return None, 'tie_needs_rule'
        # GERDA's valid_votes is first-round total; never use it as runoff total.
        if round_label == 'first' and any(integer(r['valid_votes']) != sum(votes) for r in pair):
            return None, 'first_round_votes_do_not_reconcile'
        for r, v in zip(pair, votes):
            if not r[share_field]: return None, 'missing_final_share'
            if abs(float(r[share_field]) - v / sum(votes)) > 0.0001:
                return None, 'final_share_disagrees'
        genders = [r['candidate_gender'] for r in pair]
        if set(genders) == {'m', 'w'}:
            status = 'mixed_labels_both_raw' if all(r['candidate_gender_source'] == 'raw' for r in pair) else 'mixed_labels_prediction_involved'
        elif all(g in ('m', 'w') for g in genders): status = 'same_gender_labels'
        else: status = 'gender_unresolved'
        return {'state': state, 'ags': ags, 'first_round_date': first_date,
                'decisive_date': when, 'round': round_label, 'status': status,
                'absolute_margin_pp': abs(votes[0]-votes[1])/sum(votes)*100,
                'gender_sources': [r['candidate_gender_source'] for r in pair],
                'actual_terms_verified': False}, None
    except (ValueError, TypeError, StopIteration) as error:
        return None, f'parse_or_schema_error: {error}'

records, exclusions = [], Counter()
for key, group in groups.items():
    record, reason = screen(key, group)
    if record: records.append(record)
    else: exclusions[reason] += 1
summaries = []
for state in sorted({r['state'] for r in rows}):
    subset = [r for r in records if r['state'] == state]
    item = {'state': state, 'structural_pairs': len(subset),
            'gender_status': dict(Counter(r['status'] for r in subset))}
    for status in ('mixed_labels_both_raw', 'mixed_labels_prediction_involved', 'gender_unresolved'):
        eligible = [r for r in subset if r['status'] == status]
        item[status + '_within_pp'] = {str(h): sum(r['absolute_margin_pp'] <= h for r in eligible) for h in (1, 2, 5, 10)}
    summaries.append(item)
result = {'source': metadata, 'screen_start': str(START), 'screen_cutoff': str(CUTOFF),
          'candidate_rows': len(rows), 'grouped_events': len(groups),
          'exclusion_counts': dict(exclusions), 'states': summaries}
result['focus_windows'] = {}
for state in ('09', '05'):
    for end_year in (2020, 2024):
        subset = [r for r in records if r['state'] == state and int(r['decisive_date'][:4]) <= end_year]
        result['focus_windows'][state + '_2020_' + str(end_year)] = {
            'structural_pairs': len(subset), 'status': dict(Counter(r['status'] for r in subset)),
            'prediction_involved_mixed_within_pp': {str(h): sum(r['status'] == 'mixed_labels_prediction_involved' and r['absolute_margin_pp'] <= h for r in subset) for h in (1, 2, 5, 10)},
            'unresolved_gender_within_pp': {str(h): sum(r['status'] == 'gender_unresolved' and r['absolute_margin_pp'] <= h for r in subset) for h in (1, 2, 5, 10)}}
(OUT / 'summary.json').write_text(json.dumps(result, indent=2))
(OUT / 'events.json').write_text(json.dumps(records, indent=2))
print(json.dumps(result, indent=2))
