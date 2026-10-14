"""Replay bounded exposure, independent-packet and conditional precision audits.

Run from repository root: PYTHONPATH=src/pilot python src/pilot/readiness_p4_p5.py
Requires pinned local originals; publishes municipal aggregates only. No RDD power.
"""
import csv, hashlib, itertools, json, zipfile
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from nrw_early_feasibility import design_support, gaussian_t_mde, gaussian_t_power, balanced_required_n

DOC=Path('docs/feasibility')
RAW=Path('data/raw/readiness-p4-p5-2026-10-15')
OUT=Path('outputs/readiness-p4-p5-2026-10-15')
CUTOFF='2026-09-30'

def read(path):
    return json.loads(Path(path).read_text())

def rows(path):
    with Path(path).open(newline='') as f:return list(csv.DictReader(f))

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path,data):
    Path(path).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def write_csv(path,data):
    with Path(path).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)

def verify_pins(pins):
    for p in pins:
        if sha(p['artifact'])!=p['sha256']:raise ValueError('Changed pinned input: '+p['artifact'])

def possible_sides(winner=None,loser=None):
    """Possible female-win sides of mixed pairs, preserving every known label."""
    if (winner,loser)==('same_presentation','same_presentation'):return set()
    if winner not in (None,'female','male') or loser not in (None,'female','male'):raise ValueError('Unknown label')
    return {w=='female' for w,l in itertools.product([winner] if winner else ['female','male'],[loser] if loser else ['female','male']) if w!=l}

def feasible_wins(options):
    counts={0}
    for sides in options:
        if not sides:raise ValueError('Same-presentation pair must be excluded before bounds')
        counts={n+int(s) for n in counts for s in sides}
    return counts

def packet_audit(link_keys):
    folder=Path('data/interim/current-cohort-independent-coding')
    forms=rows(folder/'blank-review-forms.csv');manifest=rows(folder/'neutral-source-manifest.csv')
    identity={'case_id','candidate_slot','official_identity','target_election_year','municipality_for_identity'}
    if len(forms)!=26 or len({r['case_id'] for r in forms})!=13:raise ValueError('Packet denominator changed')
    if any(len([r for r in forms if r['case_id']==case])!=2 for case in {r['case_id'] for r in forms}):raise ValueError('Missing candidate slot')
    if any(v for r in forms for k,v in r.items() if k not in identity):raise ValueError('Reviewer work present; do not overwrite or call blank')
    for r in manifest:
        p=folder/r['source_file']
        if sha(p)!=r['sha256'] or p.stat().st_size!=int(r['bytes']):raise ValueError('Packet source changed')
    key=read('data/interim/current-cohort-independent-coding-key/case-map.json')
    if not link_keys <= {r['ags']+':'+r['decisive_date'] for r in key}:raise ValueError('Six links not covered')
    bundle=Path(str(folder)+'.zip')
    if sha(bundle)!='b4b03d40c0e8ae149dad998258e2af9c0941394a7ac98d43e0d30f6abc688767':raise ValueError('Bundle changed')
    with zipfile.ZipFile(bundle) as z:
        for name in z.namelist():
            if name.startswith('/') or '..' in Path(name).parts or 'case-map' in name or 'coding-key' in name:raise ValueError('Unsafe/key-containing archive')
        for r in manifest:
            matches=[n for n in z.namelist() if n.endswith('/'+r['source_file']) or n==r['source_file']]
            if len(matches)!=1 or hashlib.sha256(z.read(matches[0])).hexdigest()!=r['sha256']:raise ValueError('Zip source mismatch')
    return {'pairs_prepared':13,'candidate_forms_prepared':26,'source_copies_verified':len(manifest),'source_bytes':sum(int(r['bytes']) for r in manifest),'bundle_sha256':sha(bundle),'bundle_bytes':bundle.stat().st_size,'current_links_covered':6,'reviewer_available':False,'pairs_assigned':0,'completed_independent_pairs':0,'candidate_agreement':None,'observed_disagreements':None,'resolved_disagreements':None,'status':'prepared_not_independently_reviewed','public_upload':False,'blinding_limit':'Forms omit first-coder labels, winner/margin and outcomes; original sources and public repository can reveal office/election facts. Prior exposure declaration required.'}

def role_labels(scoreboard):
    labels={}
    for r in scoreboard:
        if r['pair_status']=='mixed_public_presentation':
            labels[(r['cohort'],r['ags'])]=['female','male'] if r['female_presented_winner']=='true' else ['male','female']
        elif r['pair_status']=='same_public_presentation':
            # Only opposite-presentation feasibility matters; retain known exclusion.
            labels[(r['cohort'],r['ags'])]=['same_presentation','same_presentation']
    def put(cohort,ags,role,label):
        key=(cohort,ags);slot=0 if role=='winner' else 1
        if key in labels and labels[key][slot] is not None and labels[key][slot]!=label:
            # Same-presentation pairs can be female/female; they remain excluded.
            if labels[key][0]==labels[key][1]:return
            raise ValueError('Conflicting accepted first coding')
        labels.setdefault(key,[None,None])[slot]=label
    official={r['ags']:r for r in read('outputs/national-joint-expansion-2026-10-11/nrw-2020-selected-elections.json')}
    for r in read('data/raw/creative-causal-routes-2026-10-12/candidates/new-reviews.json')['reviews']:
        for c in r['candidates']:
            accepted={e['label'] for e in c['accepted_evidence']}
            if len(accepted)>1:raise ValueError('Conflicting candidate evidence')
            if accepted:
                match=[x for x in official[r['ags']]['candidates'] if x['name']==c['candidate_name_source']]
                if len(match)!=1:raise ValueError('Official candidate identity mismatch')
                put('NRW 2020',r['ags'],'winner' if match[0]['winner'] else 'loser',next(iter(accepted)))
    for file in ['data/raw/nrw-2025-validation/first-coder-presentation.json','data/raw/nrw-2025-closest-review-2026-10-11/first-coder-presentation.json']:
        for r in read(file):
            if r['disposition']=='accepted_first_coder':put('NRW 2025',r['ags'],r['official_finalist_role'],r['public_presentation'])
    for r in read('data/raw/cohort-expansion-2026-10-11/presentation/first-coder-annotations.json'):
        put('Brandenburg 2025' if r['ags'] in {'12069616','12065332'} else 'Brandenburg 2024',r['ags'],r['role'],r['presentation'])
    return labels

@lru_cache(None)
def benchmark(w,l,alpha=.025):
    if not w or not l or w+l<=2:return {'mde_sd':None,'power_025sd':None,'power_05sd':None,'power_1sd':None}
    return {'mde_sd':gaussian_t_mde(w,l,alpha),'power_025sd':gaussian_t_power(.25,w,l,alpha),'power_05sd':gaussian_t_power(.5,w,l,alpha),'power_1sd':gaussian_t_power(1,w,l,alpha)}

def conditional_bound(cases,labels):
    if len({r['ags'] for r in cases})!=len(cases):raise ValueError('Repeated municipality within cohort/route')
    options=[possible_sides(*labels.get((r['cohort'],r['ags']),[None,None])) for r in cases]
    usable=[s for s in options if s];n=len(usable);feasible=feasible_wins(usable)
    best=min(feasible,key=lambda w:(abs(2*w-n),w))
    return {'source_available_elections':len(cases),'known_same_presentation_excluded':len(cases)-n,'conditional_max_mixed_elections':n,'feasible_female_wins_min':min(feasible),'feasible_female_wins_max':max(feasible),'best_precision_female_wins':best,'best_precision_female_losses':n-best,**benchmark(best,n-best)}

def bounds(scoreboard,labels):
    routes=[('current_frozen_count_windows',[dict(r) for r in scoreboard if int(r['original_supported_tender_statistics'])>0])]
    inventory={(r['cohort'],r['ags']):r for r in rows(DOC/'creative-2024-election-inventory.csv')}
    calendar=[]
    for r in rows(DOC/'creative-2024-assignment-inventory.csv'):
        if int(r['observed_supported_tender_statistics'])>0:calendar.append(dict(inventory[(r['cohort'],r['ags'])],cohort=r['cohort']))
    routes.append(('separate_calendar_2024_counts',calendar))
    method=[]
    for r in rows(DOC/'creative-procedure-choice-assignment-opportunities.csv'):
        if r['has_method_metadata_pre_and_post']=='True':method.append(dict(inventory[('NRW 2020',r['ags'])],cohort='NRW 2020'))
    routes.append(('historical_2019_2021_method_METADATA_ONLY',method))
    result=[]
    for route,source in routes:
        for cohort in sorted({r['cohort'] for r in source}):
            for band in [2,5,10]:
                cases=[r for r in source if r['cohort']==cohort and float(r['absolute_margin_pp'])<=band]
                result.append({'route':route,'cohort':cohort,'nested_abs_gap_pp':band,**conditional_bound(cases,labels),'alpha':.025,'independently_certified_elections':0,'source_evidence_kind':'method_metadata_only_no_validated_paired_outcomes' if 'METADATA' in route else 'original_supported_count_statistics_not_complete_reporting','bound_condition':'All unresolved presentations resolve favorably holding accepted first coding fixed; all unverified validity/coverage gates assumed; current source inventory only','benchmark_kind':'independent_equal_variance_Gaussian_two_group_NOT_RDD','mde_sd_assuming_unvalidated_R2_075':None})
                if result[-1]['mde_sd'] is not None:result[-1]['mde_sd_assuming_unvalidated_R2_075']=result[-1]['mde_sd']*.5
    return result

def exposure_audit(links,annotations):
    procedures=rows(DOC/'recovered-original-procedure-audit.csv')+rows(DOC/'national-joint-nrw-2020-original-procedure-audit.csv')
    results=rows(DOC/'recovered-original-result-audit.csv')+rows(DOC/'national-joint-nrw-2020-original-result-audit.csv')
    ledger=[]
    for e in links:
        ps=[r for r in procedures if (r['cohort'],r['ags'])==(e['cohort'],e['ags'])]
        supported=[r for r in ps if r['original_issue_publication_inside_window']=='True' and r['sole_original_municipal_root_buyer_supported']=='True']
        if len({r['procedure_identifier'] for r in ps})!=len(ps):raise ValueError('Duplicated procedure')
        if len(supported)!=int(e['original_supported_procedures']):raise ValueError('Procedure denominator mismatch')
        rs=[r for r in results if (r['cohort'],r['ags'])==(e['cohort'],e['ags']) and r['observed_original_supported_statistic']=='True']
        if len(rs)!=int(e['original_supported_tender_statistics']):raise ValueError('Statistic count mismatch')
        dates=[r['root_publication_date'] for r in supported]
        year=int(e['decisive_date'][:4])+1;start=f'{year}-01-01';end=f'{year}-03-31'
        notes=[r for r in annotations if r['ags']==e['ags']]
        entries=[r['reported_entry_date'] for r in notes if r['reported_entry_date']]
        oath=[r['reported_oath_date'] for r in notes if r['reported_oath_date']]
        contracts=[r['contract_conclusion_date'] for r in rs if r['contract_conclusion_date']]
        ledger.append({'cohort':e['cohort'],'ags':e['ags'],'municipality':e['municipality'],'decisive_date':e['decisive_date'],'absolute_margin_pp':e['absolute_margin_pp'],'female_presented_winner':e['female_presented_winner'],'existing_window_start':e['observation_window_start'],'existing_window_end':e['observation_window_end'],'diagnostic_first_postelection_Q1_start':start,'diagnostic_first_postelection_Q1_end':end,'existing_window_matches_reference':e['observation_window_start']==start and e['observation_window_end']==end,'root_procedures_audited':len(ps),'original_supported_call_procedures':len(supported),'supported_tender_statistics':len(rs),'supported_procedures_without_supported_tender_statistic':len({r['procedure_identifier'] for r in supported}-{r['procedure_identifier'] for r in rs}),'earliest_root_publication':min(dates),'latest_root_publication':max(dates),'mature_nine_month_call_targets':sum(r['nine_month_target_mature_at_cutoff']=='True' for r in supported),'source_cutoff':CUTOFF,'earliest_observed_contract_date':min(contracts) if contracts else '', 'latest_observed_contract_date':max(contracts) if contracts else '', 'municipally_reported_entry_date':';'.join(entries),'reported_oath_date':';'.join(oath),'legal_entry_boundary_independently_adjudicated':False,'actual_procurement_decision_dates_verified':False,'continuous_original_winner_exposure_verified':False,'reporting_completeness_verified':False,'ITT_assignment_retained_through_turnover':True,'independent_review_completed':False,'main_study_eligibility_certified':False})
    return ledger

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    pins=read(RAW/'completed-input-pins.json')['inputs']+read(RAW/'replay-supplement-input-pins.json')['inputs'];verify_pins(pins)
    protocol=read(RAW/'before-audit.json');verify_pins(protocol['inputs'])
    retrievals=read(RAW/'source-retrieval.json');annotations=read(RAW/'office-review-annotations.json')
    if len(retrievals)>protocol['source_retrieval_cap'] or max(Counter(r['ags'] for r in retrievals).values())>2:raise ValueError('Source cap exceeded')
    sources=[]
    for r in retrievals:
        if r.get('artifact'):
            if sha(r['artifact'])!=r['sha256']:raise ValueError('New original changed')
            sources.append({'ags':r['ags'],'source_id':r['source_id'],'url':r['url'],'retrieved_utc':r['retrieved_utc'],'sha256':r['sha256'],'bytes':r['bytes'],'status':'original_retrieved'})
        else:sources.append({'ags':r['ags'],'source_id':r['source_id'],'url':r['url'],'retrieved_utc':r['retrieved_utc'],'sha256':'','bytes':0,'status':r['error']})
    for a in annotations:
        s=next(r for r in retrievals if r['source_id']==a['source_id'])
        text=Path(s['artifact']+'.txt').read_text()
        text=' '.join(text.split())
        if ' '.join(a['locator'].split()) not in text:raise ValueError('Source locator absent: '+a['source_id'])
        if a.get('identity_locator') and a['identity_locator'] not in text:raise ValueError('Source identity absent')
    cached=read('data/raw/nrw-2025-q1-eligibility-office/retrieval.json')
    for r in cached.values():
        if sha(Path('data/raw/nrw-2025-q1-eligibility-office')/r['file'])!=r['sha256']:raise ValueError('Cached office original changed')
    scoreboard=rows(DOC/'eligibility-scoreboard-events.csv');links=[r for r in scoreboard if r['provisional_mixed_count_link']=='True']
    if len(links)!=6:raise ValueError('Six-event inventory changed')
    packet=packet_audit({r['event_key'] for r in links})
    exposure=exposure_audit(links,annotations)
    old_observations=read('data/raw/nrw-2025-q1-eligibility-office/office-observations.json')
    for e in exposure:
        old=[r for r in old_observations if r['ags']==e['ags']]
        e['cached_point_role_observations']=len(old)
        e['cached_role_observation_dates']=';'.join(sorted({r['role_observation_date'] for r in old}))
    ceiling=bounds(scoreboard,role_labels(scoreboard))
    support=[]
    for cohort in sorted({r['cohort'] for r in links}):
        for band in [2,5,10]:
            cases=[r for r in links if r['cohort']==cohort and float(r['absolute_margin_pp'])<=band]
            w=sum(r['female_presented_winner']=='true' for r in cases);l=len(cases)-w
            margins=[float(r['absolute_margin_pp'])*(1 if r['female_presented_winner']=='true' else -1) for r in cases]
            support.append({'cohort':cohort,'nested_abs_gap_pp':band,'provisional_elections':len(cases),'female_wins':w,'female_losses':l,**design_support(margins),**benchmark(w,l),'RDD_power_estimable':False,'reason':'No certified common-window outcome sample; sparse assignment support; empirical outcome SD and predictive R2 unvalidated'})
    required=[{'effect_sd':effect,'alpha':alpha,'power':.8,'balanced_required_elections':balanced_required_n(effect,alpha),'balanced_required_assuming_unvalidated_R2_075':balanced_required_n(effect/.5,alpha),'benchmark_kind':'independent_equal_variance_Gaussian_NOT_RDD'} for alpha in [.025,.05] for effect in [.25,.5,1]]
    summary={'audit_date':'2026-10-15','source_cutoff':CUTOFF,'P4_status':'technical_audits_complete_independent_review_open','P5_status':'decision_complete_no_main_study_launch','decision':'End main-study causal claim under current audited protocols; retain feasibility/descriptive contribution. Reopening requires a source-pinned complete cohort with demonstrated joint yield and useful design-specific precision.','provisional_mixed_count_elections':6,'independently_certified_main_study_elections':0,'independent_packet':packet,'new_source_attempts':len(retrievals),'new_originals':len(sources)-sum(bool(r.get('error')) for r in retrievals),'supported_call_procedures':sum(r['original_supported_call_procedures'] for r in exposure),'supported_tender_statistics':sum(r['supported_tender_statistics'] for r in exposure),'compatible_first_postelection_Q1_cases':sum(r['existing_window_matches_reference'] for r in exposure),'all_cohort_pooling_permitted':False,'R_squared_validated':False,'RDD_power_simulated':False,'no_outreach':True,'private_records_uploaded':False,'pages_deployed':False}
    artifacts={'readiness-exposure-audit.csv':exposure,'readiness-source-manifest.csv':sources,'readiness-conditional-ceilings.csv':ceiling,'readiness-design-support.csv':support,'readiness-gaussian-benchmarks.csv':required}
    for name,data in artifacts.items():write_csv(DOC/name,data)
    write_json(DOC/'readiness-p4-p5-summary.json',summary)
    # Pin private inputs by content only. Raw paths are reproduction locators, not uploads.
    write_json(DOC/'readiness-p4-p5-input-manifest.json',{'audit_date':'2026-10-15','inputs':pins,'prospective_protocol_inputs':protocol['inputs'],'private_originals_not_uploaded':True})
    artifacts.update({'readiness-p4-p5-summary.json':None,'readiness-p4-p5-input-manifest.json':None})
    write_json(OUT/'verification.json',{'deterministic_public_artifacts':{str(DOC/name):sha(DOC/name) for name in artifacts},'independent_review_completed':False})
    print(json.dumps({'P4':summary['P4_status'],'P5':summary['P5_status'],'procedures':summary['supported_call_procedures'],'statistics':summary['supported_tender_statistics'],'ceilings_10pp':[r for r in ceiling if r['nested_abs_gap_pp']==10]},indent=2))

if __name__=='__main__':main()
