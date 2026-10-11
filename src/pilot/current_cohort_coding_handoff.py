"""Prepare private multi-cohort independent forms; never complete second coding."""
import csv,hashlib,json,shutil
from pathlib import Path
from collections import Counter
from nrw_2025_validation import csv_write
from bandwidth_window_expansion import check_pin
from nrw_2025_reopening import name_key

ROOT=Path('data/interim/current-cohort-independent-coding')
KEY=Path('data/interim/current-cohort-independent-coding-key')
RAW=Path('data/raw/national-joint-expansion-2026-10-11/candidates')

def blank_form(case,slot,name,year,municipality):
    return {'case_id':case,'candidate_slot':slot,'official_identity':name,'target_election_year':year,'municipality_for_identity':municipality,'independent_presentation':'','administrative_measure_if_explicit':'','source_file':'','exact_locator':'','identity_status':'','primary_authorship':'','historical_target_link':'','event_date':'','uncertainty_reason':'','reviewer_identity':'','review_date':'','prior_exposure_disclosed':''}

def neutral_id(value):return hashlib.sha256(value.encode()).hexdigest()[:16]

def review_has_work(form):
    identity={'case_id','candidate_slot','official_identity','target_election_year','municipality_for_identity'}
    return any(value for field,value in form.items() if field not in identity)

def main():
    ROOT.mkdir(parents=True,exist_ok=True);KEY.mkdir(parents=True,exist_ok=True)
    existing=ROOT/'blank-review-forms.csv'
    if existing.exists() and any(review_has_work(r) for r in csv.DictReader(existing.open())):
        raise FileExistsError('Preserve reviewer work; do not regenerate over populated forms')
    old_sources={r['source_id']:r for r in csv.DictReader(open('docs/feasibility/nrw-close-pair-source-manifest.csv'))}
    for p in json.loads((RAW/'source-retrieval.json').read_text()):old_sources[p['source_id']]=p
    new_reviews={r['ags']:r for r in json.loads((RAW/'new-reviews.json').read_text())['reviews']}
    older={e['ags']:e for e in json.loads(Path('outputs/national-joint-expansion-2026-10-11/nrw-2020-selected-elections.json').read_text())}
    active={e['ags']:e for e in json.loads(Path('outputs/bandwidth-window-expansion-2026-10-11/selected-elections.json').read_text())}
    cases=[]
    for selected in json.loads((RAW/'batch-before-search.json').read_text())['selected']:
        e=older[selected['ags']];review=new_reviews[e['ags']]
        pins=[(old_sources[sid],Path(old_sources[sid]['local_file'])) for sid in review['reviewed_source_ids'] if not sid.startswith('nrw-result-') and old_sources[sid]['status']=='acquired']
        cases.append((e,[c['candidate_name_source'] for c in review['candidates']],pins))
    annotations=json.loads(Path('data/raw/nrw-2025-validation/first-coder-presentation.json').read_text())
    source2025=json.loads(Path('data/raw/nrw-2025-validation/retrieval.json').read_text())
    for ags in ('05382040','05954020','05962032','05978024'):
        e=active[ags];pins=[]
        for a in annotations:
            if a['ags']==ags:
                p=source2025[a['source_id']];pins.append((dict(p,source_url=p['url']),Path('data/raw/nrw-2025-validation')/p['file']))
        cases.append((e,[c['name'] for c in e['candidates']],pins))
    e=active['03257009'];pins=[]
    for p in json.loads(Path('data/raw/original-recovery-2026-10-11/presentation/retrieval.json').read_text())['sources']:
        pins.append((dict(p,source_url=p['url']),Path('data/raw/original-recovery-2026-10-11/presentation')/p['file']))
    cases.append((e,[c['name'] for c in e['candidates']],pins))
    forms=[];key=[];manifest=[];copied={};total=0
    for e,names,pins in sorted(cases,key=lambda c:neutral_id(c[0]['ags']+c[0]['decisive_date'])):
        case=neutral_id(e['ags']+':'+e['decisive_date']+':current-coding')
        directory=ROOT/case;directory.mkdir(exist_ok=True)
        for i,name in enumerate(sorted(names,key=lambda n:neutral_id(case+n)),1):forms.append(blank_form(case,str(i),name,e['decisive_date'][:4],e['municipality']))
        key.append({'case_id':case,'ags':e['ags'],'cohort':e['cohort'],'decisive_date':e['decisive_date'],'first_coder_key_location':'Separate existing pinned annotations; not in packet','reviewer_forms_completed':False})
        for pin,path in pins:
            pin=dict(pin,bytes=int(pin['bytes']))
            raw=check_pin(pin,path);digest=hashlib.sha256(raw).hexdigest();filename='source-'+digest[:16]+path.suffix.lower()
            target=directory/filename
            if str(target) in copied:continue
            total+=len(raw)
            if total>512*1024**2:raise ValueError('Independent packet copy budget exceeded')
            target.write_bytes(raw);copied[str(target)]=digest
            manifest.append({'case_id':case,'source_file':case+'/'+filename,'source_url':pin.get('source_url',pin.get('url','')),'sha256':digest,'bytes':len(raw),'text_encoding':pin.get('text_encoding','utf-8')})
    assert len(cases)==13 and len(forms)==26 and len({f['case_id'] for f in forms})==13
    assert all(not f['independent_presentation'] and not f['reviewer_identity'] for f in forms)
    csv_write(ROOT/'blank-review-forms.csv',forms);csv_write(ROOT/'neutral-source-manifest.csv',manifest)
    (KEY/'case-map.json').write_text(json.dumps(key,indent=2)+'\n')
    shutil.copyfile('docs/feasibility/current-cohort-independent-coding-protocol.md',ROOT/'README.md')
    summary={'prepared_pairs':13,'prepared_candidate_forms':26,'cohorts':['NRW 2020','NRW 2025','Niedersachsen 2021'],'current_provisional_mixed_count_cases_covered':6,'other_exclusion_or_unresolved_pairs_in_packet':7,'source_copies':len(manifest),'copied_original_bytes':total,'second_coding_completed':False,'independent_reviewer_assigned':False,'key_in_packet':False,'votes_margins_winner_labels_outcomes_in_forms':False,'blinding_limit':'Original sources and public study summaries can reveal election/office facts; require prior-exposure disclosure.','packet_sent':False,'packet_uploaded':False}
    Path('docs/feasibility/current-cohort-independent-coding-readiness.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
