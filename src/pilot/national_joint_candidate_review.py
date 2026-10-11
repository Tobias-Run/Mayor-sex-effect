"""Revalidate separate new first-coder annotations and publish aggregates."""
import csv,json
from pathlib import Path
from bandwidth_window_expansion import check_pin
from nrw_close_pair_screen import audit_reviews,original_events
from nrw_2025_validation import csv_write

RAW=Path('data/raw/national-joint-expansion-2026-10-11/candidates')
DOC=Path('docs/feasibility')

def main():
    batch=json.loads((RAW/'batch-before-search.json').read_text())
    check_pin({'sha256':batch['protocol_sha256']},DOC/'national-joint-candidate-batch-protocol.md')
    for pin in json.loads((RAW/'accepted-source-pins.json').read_text())['inputs']:check_pin(pin,pin['artifact'])
    original=json.loads(Path('data/interim/nrw-close-pair-screen/reviews.json').read_text())
    worksheet=json.loads((RAW/'new-reviews.json').read_text())
    check_pin({'sha256':worksheet['codebook_sha256']},DOC/'candidate-exposure-codebook.md')
    sources={r['source_id']:r for r in csv.DictReader((DOC/'nrw-close-pair-source-manifest.csv').open())}
    new_sources=json.loads((RAW/'source-retrieval.json').read_text())
    for r in new_sources:sources[r['source_id']]=r
    events=original_events(sources)
    old=audit_reviews(events,original['reviews'],sources)
    new=audit_reviews(events,worksheet['reviews'],sources)
    old_by={r['ags']:r for r in old};new_by={r['ags']:r for r in new}
    selected={r['ags'] for r in batch['selected']}
    assert {r['ags'] for r in old if r!=new_by[r['ags']]}<=selected
    rows=list(csv.DictReader((DOC/'national-joint-nrw-2020-assignment-inventory.csv').open()))
    for r in rows:
        n=new_by[r['ags']];r['first_coder_pair_status']=n['pair_status'];r['female_presented_winner']=n['female_presented_winner']
        r['provisional_mixed_count_election']=n['pair_status']=='mixed_public_presentation' and int(r['observed_supported_tender_statistics'])>0
        r['candidate_evidence_newly_collected']=int(n['supported_candidates'])>int(old_by[r['ags']]['supported_candidates'])
    csv_write(DOC/'national-joint-nrw-2020-assignment-inventory.csv',rows)
    audit=[]
    for b in batch['selected']:
        o=old_by[b['ags']];n=new_by[b['ags']]
        audit.append({'ags':b['ags'],'municipality':b['municipality'],'batch_stratum':'linked_original_count' if int(b['observed_supported_tender_statistics']) else 'unlinked_hash_selected','supported_candidates_before':o['supported_candidates'],'supported_candidates_after':n['supported_candidates'],'pair_status_before':o['pair_status'],'pair_status_after':n['pair_status'],'female_presented_winner':n['female_presented_winner'],'new_primary_source_ids':';'.join(sorted(set(n['accepted_source_ids'].split(';'))-set(o['accepted_source_ids'].split(';')))),'independent_second_coding_completed':False,'main_study_eligibility_certified':False})
    csv_write(DOC/'national-joint-candidate-batch-dispositions.csv',audit)
    csv_write(DOC/'national-joint-candidate-source-manifest.csv',[{k:r.get(k,'') for k in ('source_id','source_url','status','sha256','bytes','retrieved_at_utc','final_url','authorship','failure_reason')} for r in new_sources])
    mixed=[r for r in rows if r['provisional_mixed_count_election']]
    summary=json.loads((DOC/'national-joint-nrw-2020-original-audit-summary.json').read_text())
    receipt=json.loads((DOC/'national-joint-original-recovery-export-manifest.json').read_text())
    summary.update({'new_original_xml_download_bytes':receipt['new_successful_bytes'],'previous_provisional_mixed_count_elections':5,'first_coder_mixed_pairs_before_followup':6,'first_coder_mixed_pairs_retained':sum(r['first_coder_pair_status']=='mixed_public_presentation' for r in rows),'mixed_elections_with_observed_supported_counts':len(mixed),'female_presented_wins_with_counts':sum(r['female_presented_winner']=='true' for r in mixed),'female_presented_losses_with_counts':sum(r['female_presented_winner']=='false' for r in mixed),'candidate_evidence_source':'Frozen evidence revalidated plus separately pinned bounded historical follow-up','provisional_mixed_count_elections_across_separate_cohorts':5+len(mixed)})
    (DOC/'national-joint-nrw-2020-original-audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
