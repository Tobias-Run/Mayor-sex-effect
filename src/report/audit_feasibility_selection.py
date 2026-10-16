"""Descriptive selection audit of fixed public ledgers; no effects or new coding."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/feasibility'
STAGES = ['frame', 'both_presentations', 'mixed_first_coder', 'mixed_with_original_call',
          'mixed_with_count_statistic', 'mixed_with_reference_window', 'certified_main_study']


def rows(path):
    with Path(path).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def validate(events):
    keys = [(r['cohort'], r['ags'], r['decisive_date']) for r in events]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate election event')
    for r in events:
        both = r['winner_presentation_gate'] == r['loser_presentation_gate'] == 'pass'
        if both != (r['pair_status'] in {'mixed_public_presentation', 'same_public_presentation'}):
            raise ValueError('Pair status conflicts with presentation gates')
        if r['provisional_mixed_count_link'] not in {'True', 'False'}:
            raise ValueError('Unknown linkage flag')
        observed = int(r['original_supported_tender_statistics']) > 0
        call = int(r['original_supported_procedures']) > 0
        if int(r['original_supported_tender_statistics']) < 0 or int(r['original_supported_procedures']) < 0:
            raise ValueError('Negative source evidence count')
        if observed and not call:
            raise ValueError('Count statistic lacks supported call')
        expected = r['pair_status'] == 'mixed_public_presentation' and observed
        if (r['provisional_mixed_count_link'] == 'True') != expected:
            raise ValueError('Link must require mixed pair and observed count')


def stages(event, exposure):
    both = event['winner_presentation_gate'] == event['loser_presentation_gate'] == 'pass'
    mixed = both and event['pair_status'] == 'mixed_public_presentation'
    call = mixed and int(event['original_supported_procedures']) > 0
    count = call and int(event['original_supported_tender_statistics']) > 0
    key = (event['cohort'], event['ags'], event['decisive_date'])
    aligned = count and exposure.get(key, {}).get('existing_window_matches_reference') == 'True'
    certified = aligned and event['main_study_eligibility_certified'] == 'True'
    return [True, both, mixed, call, count, aligned, certified]


def selection_tables(events, exposure_rows):
    validate(events)
    exposure = {(r['cohort'], r['ags'], r['decisive_date']): r for r in exposure_rows}
    if len(exposure) != len(exposure_rows):
        raise ValueError('Duplicate exposure event')
    expected = {(r['cohort'], r['ags'], r['decisive_date']) for r in events if r['provisional_mixed_count_link'] == 'True'}
    if set(exposure) != expected:
        raise ValueError('Exposure ledger must cover exactly the provisional links')
    cohorts = sorted({r['cohort'] for r in events})
    flow, roles, availability = [], [], []
    for cohort in ['ALL_BOOKKEEPING_NOT_POOLED_ANALYSIS'] + cohorts:
        sample = events if cohort.startswith('ALL_') else [r for r in events if r['cohort'] == cohort]
        for band in [2, 5, 10]:
            rs = [r for r in sample if float(r['absolute_margin_pp']) <= band]
            n = len(rs)
            counts = [sum(stages(r, exposure)[i] for r in rs) for i in range(len(STAGES))]
            for i, (name, kept) in enumerate(zip(STAGES, counts)):
                previous = counts[i - 1] if i else n
                flow.append({'cohort': cohort, 'nested_abs_gap_pp': band, 'stage': name,
                             'events_retained': kept, 'previous_stage_events': previous,
                             'events_not_progressing': previous - kept,
                             'fraction_of_band_frame': kept / n if n else None,
                             'independent_probability_sample': False})
            winner = sum(r['winner_presentation_gate'] == 'pass' for r in rs)
            loser = sum(r['loser_presentation_gate'] == 'pass' for r in rs)
            both = counts[1]
            roles.append({'cohort': cohort, 'nested_abs_gap_pp': band, 'events': n,
                          'winner_supported': winner, 'loser_supported': loser, 'both_supported': both,
                          'winner_only': winner - both, 'loser_only': loser - both,
                          'neither_supported': n - winner - loser + both,
                          'winner_support_fraction': winner / n if n else None,
                          'loser_support_fraction': loser / n if n else None,
                          'winner_minus_loser_pp': 100 * (winner - loser) / n if n else None})
        for source_field in ['metadata_call_notice_versions', 'original_supported_procedures', 'original_supported_tender_statistics']:
            for available in [False, True]:
                rs = [r for r in sample if (int(r[source_field]) > 0) == available]
                both = sum(r['winner_presentation_gate'] == r['loser_presentation_gate'] == 'pass' for r in rs)
                availability.append({'cohort': cohort, 'source_evidence_field': source_field,
                                     'has_source_evidence': available, 'events': len(rs),
                                     'both_presentations_supported': both,
                                     'both_support_fraction': both / len(rs) if rs else None,
                                     'zero_records_imply_zero_procurement': False})
    return flow, roles, availability


def write_csv(path, data):
    with Path(path).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)


def main():
    manifest = json.loads((DOC / 'internal-review-selection-inputs-2026-10-16.json').read_text())
    for pin in manifest['inputs']:
        data = (ROOT / pin['artifact']).read_bytes()
        if len(data) != pin['bytes'] or hashlib.sha256(data).hexdigest() != pin['sha256']:
            raise ValueError('Changed review input: ' + pin['artifact'])
    events = rows(DOC / 'eligibility-scoreboard-events.csv')
    exposure = rows(DOC / 'readiness-exposure-audit.csv')
    flow, roles, availability = selection_tables(events, exposure)
    for suffix, records in [('flow', flow), ('roles', roles), ('source-association', availability)]:
        write_csv(DOC / ('selection-audit-2026-10-16-' + suffix + '.csv'), records)
    all_roles = next(r for r in roles if r['cohort'].startswith('ALL_') and r['nested_abs_gap_pp'] == 10)
    counter = Counter(r['ags'] for r in events)
    summary = {'date': '2026-10-16', 'events': len(events), 'municipalities': len(counter),
               'repeated_municipalities': sum(n > 1 for n in counter.values()),
               'aggregate_roles': all_roles,
               'all_frame_stage_counts': {r['stage']: r['events_retained'] for r in flow if r['cohort'].startswith('ALL_') and r['nested_abs_gap_pp'] == 10},
               'cohort_pooling_adopted': False, 'selection_correction_estimated': False,
               'incumbency_or_population_selection_tested': False,
               'outcomes_or_treatment_effects_estimated': False, 'independent_review_completed': False,
               'scope': 'Fixed acquired bookkeeping events; not a probability sample or population attrition estimate'}
    (DOC / 'selection-audit-2026-10-16-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
