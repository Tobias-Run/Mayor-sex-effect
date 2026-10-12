"""Separate bounded completion dispositions; keep all older worksheets frozen."""
import csv,json
from pathlib import Path
from bandwidth_window_expansion import check_pin
from nrw_close_pair_screen import audit_reviews,original_events
from nrw_2025_validation import csv_write

RAW=Path('data/raw/creative-causal-routes-2026-10-12/candidates')
DOC=Path('docs/feasibility')

def main():
    batch=json.loads((RAW/'batch-before-search.json').read_text())
    check_pin({'sha256':batch['protocol_sha256']},DOC/'creative-candidate-completion-protocol.md')
    for p in json.loads((RAW/'annotation-pins.json').read_text())['inputs']:check_pin(p,p['artifact'])
    earlier=Path('data/raw/national-joint-expansion-2026-10-11/candidates')
    sources={r['source_id']:r for r in csv.DictReader((DOC/'nrw-close-pair-source-manifest.csv').open())}
    for p in json.loads((earlier/'source-retrieval.json').read_text()):sources[p['source_id']]=p
    latest=json.loads((RAW/'source-retrieval.json').read_text())
    for p in latest:
        sources[p['source_id']]=p
        if p['status']=='acquired':check_pin(p,p['local_file'])
    events=original_events(sources)
    old={r['ags']:r for r in audit_reviews(events,json.loads((earlier/'new-reviews.json').read_text())['reviews'],sources)}
    worksheet=json.loads((RAW/'new-reviews.json').read_text())
    check_pin({'sha256':worksheet['codebook_sha256']},DOC/'candidate-exposure-codebook.md')
    new={r['ags']:r for r in audit_reviews(events,worksheet['reviews'],sources)}
    reasons={'05154036':'New official council source unavailable (502); reused nomination title is generic, not accepted for presentation.','05166008':'Dated campaign PDF unavailable (404); no new accepted historical evidence.','05166032':'Current board supplies named address but no 2020 historical link; no interpolation to 2020.','05566004':'Current named contact page supplies address but no 2020 historical presentation link.','05962032':'Reinspection of physical PDF p2 identifies a personal masculine relative pronoun in the named/signed 2020 candidate letter; both finalists now male-presented.','05382068':'Current personal history and 2020 result notice do not supply qualifying historical person-specific cues for both finalists.'}
    dispositions=[{'ags':b['ags'],'municipality':b['municipality'],'supported_candidates_before':old[b['ags']]['supported_candidates'],'supported_candidates_after':new[b['ags']]['supported_candidates'],'pair_status_before':old[b['ags']]['pair_status'],'pair_status_after':new[b['ags']]['pair_status'],'disposition':reasons[b['ags']],'independent_second_coding_completed':False,'main_study_eligibility_certified':False} for b in batch['selected']]
    csv_write(DOC/'creative-candidate-completion-dispositions.csv',dispositions)
    keys=('source_id','source_url','status','sha256','bytes','retrieved_at_utc','final_url','authorship','failure_reason')
    manifest=[{k:p.get(k,'') for k in keys} for p in latest]+[{k:sources['luedenscheid-weiland-2020'].get(k,'') for k in keys}]
    csv_write(DOC/'creative-candidate-source-manifest.csv',manifest)
    for filename in ('creative-2024-assignment-inventory.csv','creative-procedure-choice-assignment-opportunities.csv'):
        rows=list(csv.DictReader((DOC/filename).open()))
        for r in rows:
            if r['ags'] in new:
                r['first_coder_pair_status']=new[r['ags']]['pair_status'];r['female_presented_winner']=new[r['ags']]['female_presented_winner']
        csv_write(DOC/filename,rows)
    summary={'selected_pairs':6,'unresolved_candidate_search_queries':7,'new_original_requests':6,'new_original_sources_acquired':4,'new_original_sources_unavailable':2,'accepted_reused_originals_after_visual_text_reinspection':1,'additional_supported_candidate_observations':1,'new_same_presentation_pairs':1,'new_mixed_pairs':0,'additional_provisional_mixed_count_elections':0,'current_provisional_mixed_count_inventory':6,'independent_second_coding_completed':False,'certified_main_study_elections':0,'warning':'Source/gap/margin-based operational follow-up, not a representative selection audit. Current-only named addresses and generic titles remain insufficient; existing worksheets are unchanged.'}
    (DOC/'creative-candidate-completion-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
