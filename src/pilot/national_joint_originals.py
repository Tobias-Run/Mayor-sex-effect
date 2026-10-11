"""NRW 2020 Q1 2025 original audit, with frozen historical evidence reuse."""
import argparse,csv,json,shutil,sys
from pathlib import Path
from unittest.mock import patch
import expanded_original_audit as audit
import bavaria_bounded_route as ted
from bandwidth_window_expansion import check_pin
from nrw_early_feasibility import labels_for,pair_status
from nrw_2025_reopening import name_key
from nrw_2025_validation import csv_write
from nrw_close_pair_screen import audit_reviews,original_events
from national_joint_recovery import recover

RAW=Path('data/raw/national-joint-expansion-2026-10-11')
OUT=Path('outputs/national-joint-expansion-2026-10-11')
DOC=Path('docs/feasibility')

def exports():
    result=audit.cached_exports()
    for slug in ('original-recovery-2026-10-11','bueckeburg-original-completion-2026-10-11'):
        root=Path('data/raw')/slug/'xml'
        result += [(root,p) for p in json.loads((root/'retrieval.json').read_text())['exports']]
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire-context',action='store_true');parser.add_argument('--acquire-originals',action='store_true');args=parser.parse_args()
    stage=OUT/'original-stage';stage.mkdir(parents=True,exist_ok=True)
    for src,target in [('national-joint-nrw-2020-election-inventory.csv','relaxed-acquisition-election-inventory.csv'),('national-joint-nrw-2020-q1-calls.csv','relaxed-acquisition-national-call-discovery.csv')]:shutil.copyfile(DOC/src,stage/target)
    argv=['expanded_original_audit']+(['--acquire-context'] if args.acquire_context else [])
    cache=recover(exports(),args.acquire_originals,RAW,OUT)
    with patch.object(audit,'RAW',RAW),patch.object(audit,'OUT',OUT/'original-audit'),patch.object(audit,'DOC',stage),patch.object(audit,'cached_exports',return_value=cache),patch.object(audit,'cohort_window',return_value=('2025-01-01','2025-03-31','Q1_2025_late_term_NRW_2020')),patch.object(ted,'MAX_PAGES',8),patch.object(sys,'argv',argv):audit.main()
    for p in stage.glob('expanded-original-*'):(DOC/p.name.replace('expanded-original-','national-joint-nrw-2020-original-',1)).write_bytes(p.read_bytes())
    # Candidate assignment is joined in a separately recorded historical reuse audit.
    for pin in json.loads((RAW/'candidate-reuse-pins.json').read_text())['inputs']:check_pin(pin,pin['artifact'])
    reviews={r['ags']:r for r in json.loads(Path('data/interim/nrw-close-pair-screen/reviews.json').read_text())['reviews']}
    sources={r['source_id']:r for r in csv.DictReader((DOC/'nrw-close-pair-source-manifest.csv').open())}
    historical=original_events(sources)
    validated=audit_reviews(historical,list(reviews.values()),sources)
    assert len(validated)==55
    elections=json.loads((OUT/'nrw-2020-selected-elections.json').read_text())
    linked={e['ags']:e for e in csv.DictReader((stage/'expanded-original-linked-election-inventory.csv').open())}
    assignment=[]
    for e in elections:
        review=reviews[e['ags']]
        assert {name_key(c['name']) for c in e['candidates']}=={name_key(c['candidate_name_source']) for c in review['candidates']}
        labels=labels_for(review);status=pair_status(labels)
        winner=next(c['name'] for c in e['candidates'] if c['winner'])
        female_winner=next((labels[i]=='female' for i,c in enumerate(review['candidates']) if name_key(c['candidate_name_source'])==name_key(winner)),False) if status=='mixed_public_presentation' else ''
        l=linked[e['ags']];count=int(l['observed_supported_tender_statistics'])
        assignment.append({'cohort':'NRW 2020','ags':e['ags'],'municipality':e['municipality'],'margin_stratum':e['margin_stratum'],'first_coder_pair_status':status,'female_presented_winner':female_winner,'observed_supported_tender_statistics':count,'provisional_mixed_count_election':status=='mixed_public_presentation' and count>0,'candidate_evidence_newly_collected':False,'independent_second_coding_completed':False,'office_exposure_verified':False,'main_study_eligibility_certified':False})
    csv_write(DOC/'national-joint-nrw-2020-assignment-inventory.csv',assignment)
    mixed=[r for r in assignment if r['provisional_mixed_count_election']]
    summary=json.loads((DOC/'national-joint-nrw-2020-original-audit-summary.json').read_text())
    summary.update({'cohort':'NRW 2020','call_window':'Q1 2025 late-term; separate from original historical report window','first_coder_mixed_pairs_retained':sum(r['first_coder_pair_status']=='mixed_public_presentation' for r in assignment),'mixed_elections_with_observed_supported_counts':len(mixed),'female_presented_wins_with_counts':sum(r['female_presented_winner'] for r in mixed),'female_presented_losses_with_counts':sum(not r['female_presented_winner'] for r in mixed),'candidate_evidence_source':'Frozen historical first-coder evidence; original source hashes revalidated','independent_second_coding_completed':False,'cohorts_pooled':False,'prior_provisional_inventory_in_other_cohorts':5,'warning':'Partial source-matched original audit. Candidate evidence is reused first-coder presentation, not independently recoded. Legal exposure, result completeness, selection and RDD precision remain unresolved. Acquisition counts must account for repeated municipalities.'})
    (DOC/'national-joint-nrw-2020-original-audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
