"""Bounded P3 measurement calibration; no rates, effects or eligibility promotion.

Run at the repository root. Replays pinned compiled-source fields and original
TED representations; process-level records and original source copies stay local.
"""
import csv,gzip,hashlib,json,re
from collections import Counter,defaultdict
from datetime import date
from pathlib import Path
from nrw_2025_validation import original_visible_text,csv_write
from bavaria_bounded_route import normal_text

RAW=Path('data/raw/procedure-choice-calibration-2026-10-14')
OUT=Path('outputs/procedure-choice-calibration-2026-10-14')
DOC=Path('docs/feasibility')
SALT='|procedure-calibration-2026-10-14'
METHODS={'Open procedure':'pt_open','Restricted procedure':'pt_restricted','Competitive procedure with negotiation':'pt_competitive_negotiation','Award of a contract without prior publication of a call for competition in the Official Journal of the European Union':'pt_award_contract_without_call'}

def pin_read(pin):
    raw=Path(pin['artifact']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin['sha256']:raise ValueError('Changed pinned source: '+pin['artifact'])
    return raw

def select_cases(frame):
    if len(frame)!=55 or len({r['ags'] for r in frame})!=55:raise ValueError('Complete 55-election frame required')
    conditions=[('mixed_pre_post',lambda r:r['mixed_pair_with_pre_post_method_metadata']=='True',5),('same_presentation_control',lambda r:r['first_coder_pair_status']=='same_public_presentation',2),('unresolved_pre_post_control',lambda r:r['first_coder_pair_status']=='unresolved' and r['has_method_metadata_pre_and_post']=='True',2),('no_pre_post_method_match_control',lambda r:r['has_method_metadata_pre_and_post']!='True',1)]
    selected=[]
    for label,predicate,n in conditions:
        pool=sorted([r for r in frame if predicate(r) and r['ags'] not in {x['ags'] for x in selected}],key=lambda r:hashlib.sha256((r['ags']+SALT).encode()).hexdigest())
        if len(pool)<n:raise ValueError('Pinned stratum insufficient; explicit amendment required')
        selected.extend(dict(r,stratum=label,selection_hash=hashlib.sha256((r['ags']+SALT).encode()).hexdigest()) for r in pool[:n])
    return selected

def unique_documents(documents):
    result={}
    for d in documents:
        key=(d.get('url'),d.get('documentType'),d.get('datePublished'))
        if key[0] in (None,''):raise ValueError('Document identifier missing')
        result[key]=d
    return list(result.values())

def award_timing(dates,year):
    if not dates:return 'missing'
    for d in dates:date.fromisoformat(d)
    if any(d[:4]!=year for d in dates):return 'outside_source_year_or_spanning_years'
    return 'within_source_year_metadata_only'

def extract_native(matched):
    by_ocid={r['ocid']:r for r in matched};native=[]
    if len(by_ocid)!=380 or len(matched)!=380:raise ValueError('Historical source process universe changed')
    for pin in json.loads((DOC/'creative-historical-source-manifest.json').read_text())['sources']:
        p=Path('data/raw/creative-causal-routes-2026-10-12/opentender')/pin['file']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('Annual snapshot changed')
        with gzip.open(p,'rb') as f:
            total=0
            while line:=f.readline(64*1024**2+1):
                total+=len(line)
                if len(line)>64*1024**2 or total>1024**3:raise ValueError('Snapshot bound exceeded')
                r=json.loads(line)
                if r['ocid'] not in by_ocid:continue
                m=by_ocid[r['ocid']];t=r.get('tender',{});awards=r.get('awards',[])
                if m['period']!=pin['period'] or t.get('procurementMethod')!=m['procurement_method'] or t.get('procurementMethodDetails')!=m['procurement_method_details']:raise ValueError('Compiled field mismatch')
                native.append({'ocid':r['ocid'],'ags':m['ags'],'period':pin['period'],'tender_id':t.get('id'),'award_dates':sorted({a['date'][:10] for a in awards if a.get('date')}),'awards_count':len(awards),'lots_count':len(t.get('lots',[])),'source_dataset_sha256':pin['sha256']})
    if len(native)!=380 or len({r['ocid'] for r in native})!=380:raise ValueError('Native matched records omitted or duplicated')
    return {r['ocid']:r for r in native}

def scoped(text,start,end):
    match=re.search(re.escape(start)+r'(.*?)'+end,text,re.S)
    return match[1].strip() if match else ''

def original_fields(raw,filename,notice):
    if not raw:raise ValueError('Empty response is not original notice evidence')
    s=' '.join(original_visible_text(raw,filename).split());s=re.sub(r'\s*:\s*',': ',s)
    if notice not in s:raise ValueError('Wrong notice identity')
    section=scoped(s,'IV.1.1. Type of procedure',r'IV\.1\.[2-9]\.')
    method=next((code for label,code in METHODS.items() if section==label),'unresolved')
    if method=='unresolved':raise ValueError('Unresolved original procedure section')
    authority=scoped(s,'I.1. Name and addresses',r'I\.[234]\.')
    names=re.findall(r'Official name: (.*?)(?: Postal address:| National registration number:| Town:)',authority)
    country=re.search(r'Country: (.*?)(?: Contact person:| E-mail:| Telephone:| Fax:| Internet address|$)',authority)
    typ=scoped(s,'I.4. Type of the contracting authority',r'I\.5\.')
    dispatch=re.search(r'VI\.5\. Date of dispatch of this notice\s+(\d{2}/\d{2}/\d{4})',s)
    publication=re.search(r'OJ S\s+\d+/\d{4}\s+(\d{2}/\d{2}/\d{4})',s)
    def iso(match):
        if not match:return ''
        d,m,y=match[1].split('/');return date(int(y),int(m),int(d)).isoformat()
    references=sorted({str(int(num))+'-'+year for year,num in re.findall(r'(\d{4})/S\s+\d+\s*-\s*(\d+)',s)})
    return {'method_details':method,'buyer_names':names,'buyer_country':country[1].strip() if country else '', 'buyer_type':typ,'municipal_buyer_type':typ=='Regional or local authority','dispatch_date':iso(dispatch),'publication_date':iso(publication),'previous_notice_references':references,'decision_date_verified':False}

def assess_scope(fields,expected_buyer):
    if len(fields['buyer_names'])!=1:return 'unresolved_multiple_or_missing_named_buyers'
    if normal_text(fields['buyer_names'][0])!=normal_text(expected_buyer):return 'named_buyer_conflict'
    if fields.get('buyer_country')!='Germany':return 'country_missing_or_conflicting'
    if not fields['municipal_buyer_type']:return 'named_municipality_but_authority_type_conflict'
    return 'original_named_municipal_buyer_type_supported'

def original_audit(receipts,matched):
    by_ocid={r['ocid']:r for r in matched};audited=[]
    for receipt in receipts:
        if not receipt.get('artifact'):continue
        raw=pin_read(receipt)
        if not raw:continue
        try:fields=original_fields(raw,Path(receipt['artifact']).name,receipt['notice'])
        except ValueError:continue
        m=by_ocid[receipt['ocid']]
        if any(r['notice']==receipt['notice'] for r in audited):raise ValueError('Do not count representations as extra notices')
        audited.append({'ags':receipt['ags'],'ocid':receipt['ocid'],'period':receipt['period'],'notice':receipt['notice'],'url':receipt['url'],'sha256':receipt['sha256'],'fields':fields,'method_detail_agrees':fields['method_details']==m['procurement_method_details'],'broad_open_conceals_negotiation':m['procurement_method']=='open' and fields['method_details']=='pt_competitive_negotiation','buyer_scope_disposition':assess_scope(fields,m['buyer_name']),'document_publication_day_agrees':fields['publication_date']==receipt['expected_document_day'],'publication_dispatch_lag_days':(date.fromisoformat(fields['publication_date'])-date.fromisoformat(fields['dispatch_date'])).days if fields['publication_date'] and fields['dispatch_date'] else None})
    return audited

def availability(frame,matched,native):
    inventory=[]
    for e in frame:
        result={'ags':e['ags'],'municipality':e['municipality'],'first_coder_pair_status':e['first_coder_pair_status'],'female_presented_winner':e['female_presented_winner']}
        period_data={}
        for y in ('2019','2021'):
            rs=[r for r in matched if r['ags']==e['ags'] and r['period']==y and r['first_document_in_target_calendar_year']];period_data[y]=rs
            called=[r for r in rs if r['earliest_tender_document_publication_date']]
            no_call=[r for r in rs if r['procurement_method_details']=='pt_award_contract_without_call']
            values={'first_document_year_processes':len(rs),'call_metadata_processes':len(called),'award_only_metadata_processes':len(rs)-len(called),'method_detail_present':sum(bool(r['procurement_method_details']) for r in rs),'explicit_no_call_processes':len(no_call),'no_call_missing_award_date':sum(award_timing(native[r['ocid']]['award_dates'],y)=='missing' for r in no_call),'no_call_award_date_outside_snapshot_year':sum(award_timing(native[r['ocid']]['award_dates'],y)=='outside_source_year_or_spanning_years' for r in no_call),'broad_open_but_negotiated_detail':sum(r['procurement_method']=='open' and r['procurement_method_details']=='pt_competitive_negotiation' for r in rs),'repeated_document_references_collapsed':sum(len(r['source_documents'])-len(unique_documents(r['source_documents'])) for r in rs)}
            result.update({y+'_'+k:v for k,v in values.items()})
            if result[y+'_first_document_year_processes']!=int(e['source_observed_processes_pre2019' if y=='2019' else 'source_observed_processes_post2021']):raise ValueError('Full-frame availability does not reproduce prior counts')
        result.update(has_method_metadata_pre_and_post=bool(period_data['2019'] and period_data['2021'] and all(any(r['procurement_method_details'] for r in period_data[y]) for y in period_data)),has_call_metadata_pre_and_post=all(any(r['earliest_tender_document_publication_date'] for r in period_data[y]) for y in period_data),both_periods_reporting_coverage_verified=False,all_procedure_denominator_verified=False,common_decision_date_rule_verified=False,independent_second_coding_completed=False,main_study_eligibility_certified=False)
        inventory.append(result)
    return inventory

def case_audit(selected,inventory,receipts,originals,matched,native):
    by_ags={r['ags']:r for r in inventory};cases=[]
    for e in selected:
        rs=[r for r in matched if r['ags']==e['ags'] and r['first_document_in_target_calendar_year']];attempts=[r for r in receipts if r['ags']==e['ags']];os=[r for r in originals if r['ags']==e['ags']]
        periods={r['period'] for r in os};pair=by_ags[e['ags']]
        cases.append({'ags':e['ags'],'municipality':e['municipality'],'stratum':e['stratum'],'selection_hash':e['selection_hash'],'first_coder_pair_status':e['first_coder_pair_status'],'female_presented_winner':e['female_presented_winner'],'metadata_processes_2019':pair['2019_first_document_year_processes'],'metadata_processes_2021':pair['2021_first_document_year_processes'],'new_retrieval_attempts':len(attempts),'usable_original_notice_representations':len(os),'original_2019_inspected':'2019' in periods,'original_2021_inspected':'2021' in periods,'original_method_detail_matches':sum(r['method_detail_agrees'] for r in os),'original_broad_open_negotiation_conflicts':sum(r['broad_open_conceals_negotiation'] for r in os),'original_buyer_scope_conflicts':sum(r['buyer_scope_disposition']!='original_named_municipal_buyer_type_supported' for r in os),'metadata_no_call_processes':sum(r['procurement_method_details']=='pt_award_contract_without_call' for r in rs),'duplicate_source_document_references':sum(len(r['source_documents'])-len(unique_documents(r['source_documents'])) for r in rs),'compiled_ocids_unique_in_both_years':len({r['ocid'] for r in rs})==len(rs),'all_original_procedure_identifiers_and_revisions_reconciled':False,'both_period_original_scope_timing_verified':False,'all_procedure_denominator_verified':False,'common_decision_date_rule_verified':False,'calibration_disposition':'original_scope_conflict_and_incomplete_periods' if any(r['buyer_scope_disposition']!='original_named_municipal_buyer_type_supported' for r in os) else ('partial_original_support_no_complete_denominator' if os else ('no_preperiod_metadata_and_originals_unavailable' if not pair['2019_first_document_year_processes'] else 'originals_unavailable_under_fixed_budget')),'review_complete_with_disposition':True,'independent_second_coding_completed':False,'main_study_eligibility_certified':False})
    return cases

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for pin in json.loads((RAW/'completed-input-pins.json').read_text())['inputs']:pin_read(pin)
    batch=json.loads((RAW/'before-original-inspection.json').read_text())
    for pin in batch['inputs']:pin_read(pin)
    frame=list(csv.DictReader((DOC/'creative-procedure-choice-assignment-opportunities.csv').open()));selected=select_cases(frame)
    if selected!=batch['selected']:raise ValueError('Post-inspection case selection changed')
    matched=json.loads(Path('outputs/creative-causal-routes-2026-10-12/historical-matched-processes.json').read_text());native=extract_native(matched)
    receipts=json.loads((RAW/'retrieval.json').read_text())
    if len(receipts)>30 or max(Counter(r['url'] for r in receipts).values())>2:raise ValueError('Acquisition budget exceeded')
    for r in receipts:
        if r.get('artifact'):pin_read(r)
    originals=original_audit(receipts,matched);inventory=availability(frame,matched,native);cases=case_audit(selected,inventory,receipts,originals,matched,native)
    csv_write(DOC/'procedure-choice-calibration-availability.csv',inventory)
    csv_write(DOC/'procedure-choice-calibration-cases.csv',cases)
    original_public=[]
    for r in originals:
        f=r['fields'];original_public.append({'ags':r['ags'],'source_period':r['period'],'notice':r['notice'],'source_url':r['url'],'source_sha256':r['sha256'],'original_method_details':f['method_details'],'detailed_metadata_agrees':r['method_detail_agrees'],'broad_open_conceals_negotiation':r['broad_open_conceals_negotiation'],'buyer_scope_disposition':r['buyer_scope_disposition'],'original_publication_date':f['publication_date'],'original_dispatch_date':f['dispatch_date'],'publication_dispatch_lag_days':r['publication_dispatch_lag_days'],'publication_day_metadata_agrees':r['document_publication_day_agrees'],'decision_date_verified':False,'complete_original_revision_graph_verified':False,'main_study_eligibility_certified':False})
    csv_write(DOC/'procedure-choice-calibration-original-checks.csv',original_public)
    csv_write(DOC/'procedure-choice-calibration-source-manifest.csv',[{k:r.get(k,'') for k in ('attempt','ags','period','notice','url','channel','status','bytes','sha256','retrieved_utc','error')}|{'usable_original_content':r['notice'] in {o['notice'] for o in originals} and bool(r.get('bytes')) and r.get('status')==200} for r in receipts])
    csv_write(DOC/'procedure-choice-calibration-selection.csv',[{k:r[k] for k in ('ags','municipality','stratum','selection_hash','first_coder_pair_status','female_presented_winner','has_method_metadata_pre_and_post')} for r in selected])
    (OUT/'original-field-audit.json').write_text(json.dumps(originals,indent=2)+'\n');(OUT/'native-projection.json').write_text(json.dumps(list(native.values()),indent=2)+'\n')
    in_scope=[r for r in matched if r['first_document_in_target_calendar_year']];no_call=[r for r in in_scope if r['procurement_method_details']=='pt_award_contract_without_call']
    summary={'checked_on':'2026-10-14','full_availability_denominator_elections':55,'selected_calibration_cases':len(cases),'completed_case_dispositions':sum(r['review_complete_with_disposition'] for r in cases),'selection_strata':dict(Counter(r['stratum'] for r in cases)),'source_matched_compiled_processes':len(matched),'first_document_in_target_year_processes':len(in_scope),'municipalities_with_any_first_document_year_metadata':sum(r['2019_first_document_year_processes']+r['2021_first_document_year_processes']>0 for r in inventory),'municipalities_with_pre_post_method_metadata':sum(r['has_method_metadata_pre_and_post'] for r in inventory),'municipalities_with_pre_post_call_metadata':sum(r['has_call_metadata_pre_and_post'] for r in inventory),'mixed_pre_post_method_leads':sum(r['first_coder_pair_status']=='mixed_public_presentation' and r['has_method_metadata_pre_and_post'] for r in inventory),'new_source_retrieval_attempts':len(receipts),'source_retrieval_cap':30,'HTTP_202_empty_responses':sum(r.get('status')==202 and r.get('bytes')==0 for r in receipts),'browser_inaccessible_responses':sum(r.get('status')=='tool_inaccessible' for r in receipts),'usable_original_notices':len(originals),'cases_with_any_usable_original':sum(bool(r['usable_original_notice_representations']) for r in cases),'cases_with_usable_originals_in_both_periods':sum(r['original_2019_inspected'] and r['original_2021_inspected'] for r in cases),'original_detailed_method_agreements':sum(r['method_detail_agrees'] for r in originals),'original_broad_open_negotiation_conflicts':sum(r['broad_open_conceals_negotiation'] for r in originals),'original_buyer_scope_conflicts':sum(r['buyer_scope_disposition']!='original_named_municipal_buyer_type_supported' for r in originals),'all_frame_broad_open_negotiated_detail_records':sum(r['procurement_method']=='open' and r['procurement_method_details']=='pt_competitive_negotiation' for r in in_scope),'explicit_no_call_processes':len(no_call),'no_call_missing_award_date_metadata':sum(not native[r['ocid']]['award_dates'] for r in no_call),'no_call_award_date_outside_source_year_metadata':sum(award_timing(native[r['ocid']]['award_dates'],r['period'])=='outside_source_year_or_spanning_years' for r in no_call),'repeated_document_references_collapsed_all_matched':sum(len(r['source_documents'])-len(unique_documents(r['source_documents'])) for r in matched),'same_document_identifies_multiple_compiled_processes_observed':False,'original_revision_graphs_certified':0,'all_procedure_denominator_validated':False,'called_only_prototype_validated':False,'primary_outcome_adopted':False,'all_procedure_share_decision':'not_validated; missing comparable no-call timing and complete reporting universe','called_only_prototype_decision':'proposed conditional measurement only; original coverage, zero-denominator selection and decision-date interpretation unresolved','additional_supported_count_elections':0,'existing_provisional_mixed_count_elections_unchanged':6,'independent_second_coding_completed':False,'main_study_elections_certified':0,'effects_or_outcome_rates_estimated':False,'pre_election_predictive_R_squared_estimated':False,'pages_deployed':False,'warning':'Two available original notices are not representative validation of ten cases or the 55-election frame. Access failures do not establish invalidity of the underlying procedures.'}
    # Cross-process source identity checks, not an assumption of unique purchases.
    identities=defaultdict(set)
    for r in matched:
        for d in unique_documents(r['source_documents']):identities[d['url']].add(r['ocid'])
    summary['same_document_identifies_multiple_compiled_processes_observed']=any(len(v)>1 for v in identities.values())
    (DOC/'procedure-choice-calibration-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (DOC/'procedure-choice-calibration-input-manifest.json').write_text(json.dumps({'public_input_pins':[p for p in batch['inputs'] if p['artifact'].startswith('docs/')],'private_complete_before_inspection_pin_sha256':hashlib.sha256((RAW/'before-original-inspection.json').read_bytes()).hexdigest(),'private_original_queue_sha256':hashlib.sha256((RAW/'original-queue.json').read_bytes()).hexdigest(),'originals_and_process_records_uploaded':False,'complete_offline_replay_requires_private_pinned_sources':True},indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
