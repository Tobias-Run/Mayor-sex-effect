"""Source-pinned first-coder Bückeburg assignment, separate from NRW outcomes."""
import csv,hashlib,json
from pathlib import Path
from nrw_2025_validation import original_visible_text

RAW=Path('data/raw/original-recovery-2026-10-11/presentation')
DOC=Path('docs/feasibility')

def evidence_supported(raw,filename,name,phrase,event_date):
    text=' '.join(original_visible_text(raw,filename).split())
    return all(value in text for value in (name,phrase,event_date))

def main():
    receipt=json.loads((RAW/'retrieval.json').read_text())
    rules={'spd-2021':('Sandra Schauer-Bolte','BÜRGERMEISTERKANDIDATIN','18.03.2021','female'),
           'cdu-2021':('Axel Wohlgemuth','CDU-Bürgermeisterkandidaten Axel Wohlgemuth','24. August 2021','male')}
    observations=[];sources=[]
    for pin in receipt['sources']:
        raw=(RAW/pin['file']).read_bytes()
        assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256']
        name,phrase,event_date,label=rules[pin['source_id']]
        assert evidence_supported(raw,pin['file'],name,phrase,event_date)
        observations.append({'name':name,'source_id':pin['source_id'],'presentation':label,'event_date':event_date,'locator':phrase})
        sources.append({**pin,'historical_event_date':event_date,'role':'candidate primary party source'})
    election=next(e for e in json.loads(Path('outputs/bandwidth-window-expansion-2026-10-11/selected-elections.json').read_text()) if e['ags']=='03257009')
    official={c['name']:c for c in election['candidates']}
    assert set(official)=={'Wohlgemuth, Axel','Schauer-Bolte, Sandra'}
    assert official['Wohlgemuth, Axel']['winner'] and not official['Schauer-Bolte, Sandra']['winner']
    linked=next(e for e in csv.DictReader((DOC/'recovered-original-linked-election-inventory.csv').open()) if e['ags']==election['ags'])
    count=int(linked['observed_supported_tender_statistics'])
    private={'election':election,'observations':observations,'independent_second_coding':False,'administrative_sex_observed':False}
    (RAW/'first-coder-assignment.json').write_text(json.dumps(private,indent=2)+'\n')
    result={'checked_on':'2026-10-11','cohort':election['cohort'],'ags':election['ags'],'municipality':election['municipality'],'decisive_date':election['decisive_date'],'margin_stratum':'over_5_to_10pp','absolute_margin_pp':election['absolute_margin_pp'],'first_coder_mixed_pair_supported':True,'female_presented_winner':False,'observed_supported_tender_statistics':count,'additional_provisional_mixed_count_elections':int(count>0),'previous_provisional_NRW_mixed_count_elections':4,'total_provisional_mixed_count_elections_across_separate_cohorts':4+int(count>0),'independent_second_coding_completed':False,'certified_main_study_elections':0,'cohorts_pooled':False,'limitations':['First-coder public presentation is not administrative sex.','Official Niedersachsen returns are headed provisional.','Late-term full-year 2025 outcomes are not pooled with NRW Q1 2026.','Calendar-mature follow-up does not establish complete result coverage.','Legal entry, uninterrupted exposure and result coverage remain open.','Candidate review targets one outcome-linked lead and cannot estimate frame-wide missingness or eliminate selection bias.']}
    (DOC/'original-recovery-assignment-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n')
    (DOC/'original-recovery-presentation-source-manifest.json').write_text(json.dumps({'sources':sources,'failed_requests':receipt['failed_requests'],'search_batches_per_finalist':2,'independent_second_coding_completed':False},indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
