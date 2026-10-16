"""Public-input-only synthesis; preserves the frozen v0.1 report. No downloads."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'manuscript/feasibility-2026-10-16'


def verify(root, manifest):
    seen = set()
    for entry in manifest['inputs']:
        name = entry['artifact']
        path = (root / name).resolve()
        if name in seen or not path.is_relative_to(root.resolve()):
            raise ValueError('Duplicate or unsafe input: ' + name)
        seen.add(name)
        data = path.read_bytes()
        if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError('Changed public evidence: ' + name)


def reconcile(events, exposure, summary):
    keys = [(r['cohort'], r['ags'], r['decisive_date']) for r in exposure]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate exposure event')
    if len(exposure) != summary['provisional_mixed_count_elections']:
        raise ValueError('Provisional election denominator mismatch')
    for field, total in [('original_supported_call_procedures', 'supported_call_procedures'),
                         ('supported_tender_statistics', 'supported_tender_statistics')]:
        if sum(int(r[field]) for r in exposure) != summary[total]:
            raise ValueError('Procedure/statistic denominator mismatch')
    if any(r['main_study_eligibility_certified'] != 'False' for r in exposure):
        raise ValueError('Review decision requires reconsideration')
    if sum(r['existing_window_matches_reference'] == 'True' for r in exposure) != summary['compatible_first_postelection_Q1_cases']:
        raise ValueError('Window alignment mismatch')
    if len({r['event_key'] for r in events}) != len(events):
        raise ValueError('Duplicate scoreboard event')
    return {'events': len(events), 'municipalities': len({r['ags'] for r in events}),
            'provisional_elections': len(exposure), 'certified_elections': summary['independently_certified_main_study_elections'],
            'procedures': summary['supported_call_procedures'], 'statistics': summary['supported_tender_statistics']}


def table(headers, rows):
    if any('|' in str(c) or '\n' in str(c) for row in [headers] + rows for c in row):
        raise ValueError('Unsafe table cell')
    return '\n'.join('| ' + ' | '.join(map(str, row)) + ' |' for row in [headers, ['---'] * len(headers)] + rows)


def build(root=ROOT, destination=DEST):
    manifest = json.loads((destination / 'inputs.json').read_text())
    verify(root, manifest)
    base = root / 'docs/feasibility'
    def rows(name):
        with (base / name).open(newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    summary = json.loads((base / 'readiness-p4-p5-summary.json').read_text())
    exposure = rows('readiness-exposure-audit.csv')
    facts = reconcile(rows('eligibility-scoreboard-events.csv'), exposure, summary)
    linked = [[r['municipality'], r['cohort'], f"{float(r['absolute_margin_pp']):.2f}",
               r['original_supported_call_procedures'], r['supported_tender_statistics']] for r in exposure]
    labels = {'current_frozen_count_windows': 'Current count', 'separate_calendar_2024_counts': '2024 count',
              'historical_2019_2021_method_METADATA_ONLY': 'Method metadata only'}
    ceilings = [[labels[r['route']] + ': ' + r['cohort'], r['source_available_elections'],
                 r['conditional_max_mixed_elections'],
                 r['best_precision_female_wins'] + '/' + r['best_precision_female_losses'],
                 f"{float(r['mde_sd']):.2f}" if r['mde_sd'] else 'NA']
                for r in rows('readiness-conditional-ceilings.csv') if r['nested_abs_gap_pp'] == '10']
    benchmarks = [[r['effect_sd'], r['balanced_required_elections'], r['balanced_required_assuming_unvalidated_R2_075']]
                  for r in rows('readiness-gaussian-benchmarks.csv') if r['alpha'] == '0.025']
    values = {**facts,
              'linked_table': table(['Municipality', 'Election cohort', 'Gap (pp)', 'Calls', 'Statistics'], linked),
              'ceiling_table': table(['Route and cohort', 'Source N', 'Max mixed N', 'Best W/L', 'MDE (SD)'], ceilings),
              'precision_table': table(['Effect (SD)', 'Balanced N', 'N if assumed R-squared = .75'], benchmarks)}
    text = (destination / 'manuscript.template.md').read_text()
    text = re.sub(r'\{\{([a-z_]+)\}\}', lambda m: str(values[m[1]]), text)
    if '{{' in text:
        raise ValueError('Unresolved manuscript field')
    (destination / 'manuscript.md').write_text(text)
    (destination / 'facts.json').write_text(json.dumps(facts, indent=2) + '\n')
    return facts


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
