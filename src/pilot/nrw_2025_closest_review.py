"""Bounded primary-evidence review of every NRW 2025 decisive pair within 2 pp.

Run from repository root. Requires ignored original sources and first-coder
annotations. Public artifacts contain event dispositions and source pins only.
No name inference, independent-review claim or causal estimator is implemented.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
from nrw_2025_reopening import parse_detail
from nrw_2025_validation import presentation_pairs, csv_write

DOC = Path('docs/feasibility')
OLD = Path('data/raw/nrw-2025-validation')
NEW = Path('data/raw/nrw-2025-closest-review-2026-10-11')


def assemble_review(events, pairs, annotations, coverage):
    """A completed search may remain unresolved; preserve every scoped election."""
    scoped = sorted((e for e in events if e['decisive_pair'] and e['absolute_margin_pp'] <= 2),
                    key=lambda e:e['absolute_margin_pp'])
    keys = {e['ags'] for e in scoped}
    grouped = {}
    for row in annotations:
        if row['ags'] not in keys:
            raise ValueError('Disposition outside fixed closest-pair scope')
        key = (row['ags'], row['official_finalist_role'])
        if key in grouped or row['official_finalist_role'] not in ('winner','loser'):
            raise ValueError('Repeated or invalid finalist disposition')
        if row['disposition'] not in ('accepted_first_coder','reviewed_unresolved'):
            raise ValueError('Finalist review is incomplete')
        grouped[key] = row
    supported = {r['ags']:r for r in pairs}
    if len(supported) != len(pairs) or set(supported)-keys:
        raise ValueError('Repeated or out-of-scope pair')
    result = []
    for event in scoped:
        ags = event['ags']
        if any((ags, role) not in grouped for role in ('winner','loser')):
            raise ValueError('Every finalist needs a completed review disposition')
        records = [grouped[(ags,role)] for role in ('winner','loser')]
        pair = supported.get(ags, {})
        result.append({'ags':ags,'municipality':event['municipality_source'].removeprefix('Krfr. Stadt ').removesuffix(', Stadt'),
                       'absolute_margin_pp':event['absolute_margin_pp'],
                       'pair_status':pair.get('pair_status','unresolved'),
                       'review_complete':True,
                       'winner_review_disposition':records[0]['disposition'],
                       'loser_review_disposition':records[1]['disposition'],
                       'evidence_tiers':';'.join(r['tier'] for r in records),
                       'winner_context_date':records[0]['context_date'],
                       'loser_context_date':records[1]['context_date'],
                       'winner_context':records[0]['context'],
                       'loser_context':records[1]['context'],
                       'source_ids':';'.join(sorted(set(r['source_id'] for r in records))),
                       'female_presented_winner':pair.get('female_presented_winner'),
                       'signed_presentation_margin_pp':pair.get('signed_presentation_margin_pp'),
                       'original_q1_procedures':int(coverage[ags]['verified_original_q1_procedures']),
                       'independent_second_coding':False,'administrative_gender_verified':False,
                       'main_study_eligibility_certified':False,
                       'unresolved_reason':'; '.join(r['reason'] for r in records if r['disposition']=='reviewed_unresolved')})
    return result


def main():
    events = json.loads(Path('outputs/nrw-election-register-2025/events.json').read_text())
    scoped = [e for e in events if e['decisive_pair'] and e['absolute_margin_pp'] <= 2]
    assert len(scoped) == 14
    # Reparse original state files; derived events are not accepted on trust.
    for event in scoped:
        pin = event['detail_source']
        raw = (Path('data/raw/nrw-2025')/(event['source_code']+'.txt')).read_bytes()
        assert len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256']
        assert parse_detail(raw.decode('utf-8-sig'),event) == event
    annotations, pairs, manifests = [], [], []
    for root in (OLD,NEW):
        sources = json.loads((root/'retrieval.json').read_text())
        batch = [r for r in json.loads((root/'first-coder-presentation.json').read_text()) if r['ags'] in {e['ags'] for e in scoped}]
        pairs.extend(presentation_pairs(scoped,batch,sources,root))
        annotations.extend(batch)
        used = {r['source_id'] for r in batch if r['disposition']=='accepted_first_coder'}
        # Every inspected original, including rejected and discovery pages, is pinned.
        ids = sorted(sources) if root == NEW else sorted(used)
        for key in ids:
            pin = sources[key]
            raw = (root/pin['file']).read_bytes()
            assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256']
            manifests.append({'source_id':key,'provider':urlparse(pin['url']).netloc,
                              'role':'accepted_presentation_source' if key in used else 'inspected_discovery_or_rejected_source',**pin})
    with (DOC/'nrw-2025-q1-call-municipalities.csv').open(newline='') as f:
        coverage = {r['ags']:r for r in csv.DictReader(f)}
    rows = assemble_review(scoped,pairs,annotations,coverage)
    csv_write(DOC/'nrw-2025-closest-pair-evidence-review.csv',rows)
    # This queue is reproducible by the call-roster script as well.
    csv_write(DOC/'nrw-2025-closest-pair-review-queue.csv',[
        {'ags':r['ags'],'municipality':r['municipality'],'absolute_margin_pp':r['absolute_margin_pp'],
         'presentation_status':r['pair_status'],'independent_second_coding':False,
         'original_q1_procedures':r['original_q1_procedures'],
         'priority_basis':'Exact absolute election margin only; retain all prediction labels and procurement coverage states'} for r in rows])
    csv_write(DOC/'nrw-2025-closest-review-source-manifest.csv',[
        {k:r.get(k,'') for k in ('source_id','provider','role','url','final_url','file','sha256','bytes','retrieved_at_utc','content_type')} for r in manifests])
    mixed = [r for r in rows if r['pair_status']=='mixed_public_presentation']
    unresolved = [r for r in rows if r['pair_status']=='unresolved']
    mixed_q1 = [r for r in mixed if r['original_q1_procedures']>0]
    summary = {'review_date_utc':'2026-10-11','scope':'All 14 official NRW 2025 decisive pairs within inclusive 2 pp',
               'new_pairs_reviewed':11,'new_finalist_dispositions':22,
               'new_accepted_finalist_observations':sum(r['disposition']=='accepted_first_coder' for r in annotations if r['ags'] not in {'05117000','05962032','05382040'}),
               'pair_status_counts':dict(Counter(r['pair_status'] for r in rows)),
               'confirmed_mixed_female_presented_wins':sum(r['female_presented_winner'] for r in mixed),
               'confirmed_mixed_female_presented_losses':sum(not r['female_presented_winner'] for r in mixed),
               'confirmed_mixed_with_original_q1_calls':len(mixed_q1),
               'original_q1_calls_in_confirmed_mixed_cases':sum(r['original_q1_procedures'] for r in mixed_q1),
               'unresolved_pair_count':len(unresolved),
               'accepted_winner_observations':sum(r['official_finalist_role']=='winner' and r['disposition']=='accepted_first_coder' for r in annotations),
               'accepted_loser_observations':sum(r['official_finalist_role']=='loser' and r['disposition']=='accepted_first_coder' for r in annotations),
               'unresolved_cases_with_original_q1_calls':sum(r['original_q1_procedures']>0 for r in unresolved),
               'maximum_additional_female_presented_wins_from_unresolved_pairs':sum(
                   any(a['ags']==r['ags'] and a['official_finalist_role']=='winner' and
                       (a['disposition']=='reviewed_unresolved' or a['public_presentation']=='female') for a in annotations)
                   for r in unresolved),
               'logical_maximum_mixed_pairs_if_every_unresolved_pair_is_mixed':len(mixed)+len(unresolved),
               'independently_second_coded_pairs':0,'administrative_gender_verified_pairs':0,
               'main_study_certified_elections':0,'causal_effects_estimated':False,
               'planning_decision':'Do not launch a two-percentage-point causal study; retain unresolved searches and proceed only with bounded cohort-level feasibility checks.',
               'failed_retrievals':json.loads((NEW/'failed-retrievals.json').read_text()),
               'source_snapshot_count':len(manifests),
               'inputs':[{'artifact':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in
                         [Path('outputs/nrw-election-register-2025/events.json'),OLD/'first-coder-presentation.json',NEW/'first-coder-presentation.json',NEW/'retrieval.json',DOC/'nrw-2025-q1-call-municipalities.csv']]}
    (DOC/'nrw-2025-closest-review-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
