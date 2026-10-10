"""Bounded availability screen for ALL official NRW 2025 pairs within 5 pp.

No gender-based selection. Indexed result publications are not original calls,
complete procurement populations, verified buyer jurisdiction or causal outcomes.
The existing capped TED helpers are reused with separate raw/output directories.
"""
import csv
import json
from collections import Counter
from pathlib import Path
import bavaria_bounded_route as ted


def select(events):
    return [dict(e, municipality=e['municipality_source'].removeprefix('Krfr. Stadt ').removesuffix(', Stadt'))
            for e in events if e['decisive_pair'] and e['absolute_margin_pp'] <= 5]


def main():
    events = json.loads(Path('outputs/nrw-election-register-2025/events.json').read_text())
    selected = select(events)
    ted.RAW = Path('data/raw/nrw-2025-procurement-screen-normalized')
    ted.START, ted.END = '20251101', '20260930'
    query = ted.query_for(selected)
    if not (ted.RAW / 'retrieval.json').exists():
        ted.acquire(query)
    notices, metadata = ted.snapshot(query)
    mapping = ted.aliases(selected)
    counts, reasons = Counter(), Counter()
    for notice in notices:
        ags, reason = ted.match_buyer(notice, mapping)
        reasons[reason] += 1
        if ags:
            counts[ags] += 1
    public = Path('docs/feasibility')
    (public / 'nrw-2025-ted-request-manifest.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False)+'\n')
    rows = [{'ags':e['ags'],'municipality':e['municipality'],'absolute_margin_pp':e['absolute_margin_pp'], 'decisive_date':e['decisive_date'], 'provisional_exact_buyer_result_notices':counts[e['ags']], 'gender_verified':False,'actual_term_verified':False,'original_call_window_verified':False,'complete_procurement_population_verified':False} for e in selected]
    with (public / 'nrw-2025-availability-matrix.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={'selected_elections':len(selected),'selection':'All official decisive two-candidate pairs within 5 pp; no gender prediction filter','publication_window':['2025-11-01','2026-09-30'],'indexed_notices':len(notices),'provisional_exact_buyer_matches':sum(counts.values()),'municipalities_with_provisional_matches':len(counts),'match_dispositions':dict(reasons),'certified_linked_elections':0,'warning':'Publication-date availability only. Zero exact matches is not evidence of no procurement. Competition dates, buyer jurisdiction, term boundaries and outcome completeness remain unverified.'}
    # A conditional planning inventory, never a certified treatment sample.
    leads = json.loads(Path('outputs/nrw-election-register-2025/prediction-leads.json').read_text())
    within = [e for e in leads if e['margin_pp'] <= 5]
    linked = [e for e in within if counts[e['ags']] > 0]
    wins = sum(e['female_label_winner'] for e in linked)
    summary['conditional_prediction_mixed_with_provisional_buyer_matches'] = {'pairs':len(linked),'female_label_wins':wins,'female_label_losses':len(linked)-wins,'not_verified_treatment_assignments':True}
    from nrw_early_feasibility import gaussian_t_mde
    summary['conditional_gaussian_planning_benchmarks'] = []
    for sample in (linked, within):
        treated = sum(e['female_label_winner'] for e in sample)
        control = len(sample)-treated
        if treated and control and len(sample)>2:
            summary['conditional_gaussian_planning_benchmarks'].append({'hypothetical_treated':treated,'hypothetical_control':control,'mde_sd':gaussian_t_mde(treated,control),'alpha':0.05,'power':0.8,'assumptions':'Independent elections, equal-variance Gaussian pooled t test; not RDD power or empirical outcome variance.'})
    (public / 'nrw-2025-procurement-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__ == '__main__':
    main()
