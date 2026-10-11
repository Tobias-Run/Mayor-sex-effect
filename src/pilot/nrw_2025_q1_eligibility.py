"""Audit the fixed 37-procedure NRW 2025 Q1 inventory, never select on results.

Preserves missing results and separate procedure/lot/contract/election units.
This new cohort audit does not mutate the frozen historical eForms parser or
certify a complete primary population, treatment assignment or causal effect.
"""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from federal_procurement import (NS, definitions, identity, ids_at, organization_buyers,
                                 positive_count, safe_xml, source_date, text_at, verified_archive)
from nrw_2025_validation import csv_write, original_visible_text, candidate_window
import bavaria_bounded_route as ted

DOC = Path('docs/feasibility')
RAW = Path('data/raw/nrw-2025-validation/federal-eforms')
OFFICE = Path('data/raw/nrw-2025-q1-eligibility-office')
CUTOFF = '2026-09-30'
CALLED = {'open','restricted','neg-w-call'}


def municipal_scope(root, expected_names):
    """Check actual contracting-party roles, not every named organization."""
    buyers, _ = organization_buyers(root)
    parties = root.findall('cac:ContractingParty',NS)
    codes = [text_at(p,'cac:ContractingPartyType/cbc:PartyTypeCode') for p in parties]
    supported = (len(buyers)==len(parties)==1 and buyers[0]['name'] is not None
                 and ted.normal_text(buyers[0]['name']) in expected_names
                 and codes == ['kommun-beh'])
    services = sum(len(p.findall('cac:Party/cac:ServiceProviderParty',NS)) for p in parties)
    return {'scope_status':'sole_named_municipal_contracting_party_supported' if supported else 'scope_unresolved',
            'buyer_type_codes':';'.join(codes),'procurement_service_provider_records':services}


def lot_audit(root):
    """Validate reciprocal result/tender/contract links, allowing multi-lot contracts.

A contract may cover several lot tenders. Its intersection with each lot result
must equal that result's referenced tenders, and every contract tender must have
an explicitly linked result. This does not allocate a contract's amount to lots.
"""
    results = root.findall('.//efac:NoticeResult',NS)
    if len(results)!=1:
        raise ValueError('Expected one scoped NoticeResult')
    parent = results[0]
    contracts = definitions(parent,'efac:SettledContract')
    tenders = definitions(parent,'efac:LotTender')
    lots = definitions(parent,'efac:LotResult')
    parties = definitions(parent,'efac:TenderingParty')
    _, organizations = organization_buyers(root)
    defined = ids_at(root,'cac:ProcurementProjectLot/cbc:ID')
    if len(defined)!=len(set(defined)):
        raise ValueError('Duplicate defined lot')
    result_tenders = {key:ids_at(value,'efac:LotTender/cbc:ID') for key,value in lots.items()}
    result_contracts = {key:ids_at(value,'efac:SettledContract/cbc:ID') for key,value in lots.items()}
    rows=[]
    for key, result in lots.items():
        lot_ids = ids_at(result,'efac:TenderLot/cbc:ID')
        status = text_at(result,'cbc:TenderResultCode')
        refs, crefs = result_tenders[key], result_contracts[key]
        reasons=[]
        if not lot_ids or len(lot_ids)!=len(set(lot_ids)) or not set(lot_ids)<=set(defined):
            reasons.append('undefined_or_duplicate_lot')
        if any(set(lot_ids)&set(ids_at(other,'efac:TenderLot/cbc:ID')) for oid,other in lots.items() if oid!=key):
            reasons.append('overlapping_result_lots')
        statistics = [(text_at(s,'efbc:StatisticsCode'),text_at(s,'efbc:StatisticsNumeric')) for s in result.findall('efac:ReceivedSubmissionsStatistics',NS)]
        totals = [v for typ,v in statistics if typ=='tenders']
        count = positive_count(totals[0]) if len(totals)==1 else None
        if count is None:
            reasons.append('missing_duplicate_or_invalid_total')
        dates=[];cross=False
        if status=='selec-w':
            if not refs or len(refs)!=len(set(refs)) or not crefs or len(crefs)!=len(set(crefs)):
                reasons.append('missing_or_duplicate_award_reference')
            for tid in refs:
                if tid not in tenders or set(ids_at(tenders[tid],'efac:TenderLot/cbc:ID'))!=set(lot_ids):
                    reasons.append('undefined_or_wrong_lot_tender')
                    continue
                party_refs = ids_at(tenders[tid],'efac:TenderingParty/cbc:ID')
                if not party_refs:
                    reasons.append('missing_winner_party')
                for pid in party_refs:
                    winner_refs = ids_at(parties[pid],'efac:Tenderer/cbc:ID') if pid in parties else []
                    if not winner_refs or any(ref not in organizations for ref in winner_refs):
                        reasons.append('undefined_winner_organization')
            union=set()
            for cid in crefs:
                contract = contracts.get(cid)
                if contract is None:
                    reasons.append('undefined_contract');continue
                tids = ids_at(contract,'efac:LotTender/cbc:ID')
                if not tids or len(tids)!=len(set(tids)) or any(t not in tenders for t in tids):
                    reasons.append('undefined_or_duplicate_contract_tender')
                intersection = set(tids)&set(refs)
                if not intersection:
                    reasons.append('contract_has_no_tender_for_this_result')
                union.update(intersection)
                cross = cross or bool(set(tids)-set(refs))
                for tid in tids:
                    owners = [rid for rid,rr in result_tenders.items() if tid in rr]
                    if len(owners)!=1 or cid not in result_contracts.get(owners[0],[]):
                        reasons.append('nonreciprocal_contract_result_tender')
                    elif tid in tenders and (set(ids_at(tenders[tid],'efac:TenderLot/cbc:ID'))!=set(ids_at(lots[owners[0]],'efac:TenderLot/cbc:ID')) or text_at(lots[owners[0]],'cbc:TenderResultCode')!='selec-w'):
                        reasons.append('contract_tender_owner_lot_or_status_conflict')
                dates.append(source_date(text_at(contract,'cbc:IssueDate')))
            if union != set(refs):
                reasons.append('result_tender_missing_from_contracts')
        else:
            reasons.append('not_a_successful_award')
        common_date = dates[0] if dates and all(d and d==dates[0] for d in dates) else None
        if status=='selec-w' and common_date is None:
            reasons.append('missing_or_conflicting_contract_date')
        graph_reasons=[r for r in reasons if r not in {'missing_duplicate_or_invalid_total','missing_or_conflicting_contract_date','not_a_successful_award'}]
        supported = status=='selec-w' and not graph_reasons
        rows.append({'result_id':key,'lot_ids':';'.join(lot_ids),'result_status':status,
                     'explicit_total_tenders':count,'total_count_supported':count is not None,
                     'award_graph_supported':supported,'cross_lot_contract_supported':cross and supported,
                     'contract_ids':';'.join(crefs),'contract_conclusion_date':common_date,
                     'grouped_lot_statistic':len(lot_ids)>1,
                     'audit_reasons':';'.join(sorted(set(reasons)))})
    return rows


def audit_procedure(roster, records, roots, expected_names):
    guid = roster['procedure_identifier']
    if any(r['xml']['procedure_identifier']!=guid for r in records):
        raise ValueError('Mixed procedure identities')
    by_number={r['index']['publication-number']:r for r in records}
    original = by_number[roster['root_call_publication_number']]
    call_day = source_date(original['index']['publication-date'])
    issue = source_date(original['xml']['notice_issue_date_source'])
    if not candidate_window(call_day,issue):
        raise ValueError('Outside fixed original Q1 cohort')
    scopes = [municipal_scope(roots[r['index']['publication-number']],expected_names) for r in records]
    scope = all(s['scope_status']=='sole_named_municipal_contracting_party_supported' for s in scopes)
    codes = {text_at(roots[r['index']['publication-number']],'cac:TenderingProcess/cbc:ProcedureCode') for r in records}
    category = next(iter(codes)) if len(codes)==1 and codes<=CALLED else 'category_unresolved'
    results = [r for r in records if r['index']['notice-type']=='can-standard']
    units=[]
    for r in results:
        pub = source_date(r['index']['publication-date'])
        dispatch = source_date(r['xml']['notice_issue_date_source'])
        observed = bool(pub and dispatch and issue<=dispatch<=pub<=CUTOFF)
        for u in lot_audit(roots[r['index']['publication-number']]):
            units.append({'ags':roster['ags'],'procedure_identifier':guid,
                          'publication_number':r['index']['publication-number'],
                          'result_publication_date':pub,**u,
                          'candidate_count_population_supported':scope and category in CALLED and observed and u['award_graph_supported'] and u['total_count_supported'],
                          'dated_count_population_supported':scope and category in CALLED and observed and u['award_graph_supported'] and u['total_count_supported'] and bool(u['contract_conclusion_date'] and issue<=u['contract_conclusion_date']<=pub),
                          'original_xml_sha256':r['xml_sha256'],
                          'main_study_eligibility_certified':False})
    # Never choose the latest unlinked result when lots collide across notices.
    lot_owners=Counter(lot for u in units for lot in u['lot_ids'].split(';'))
    for u in units:
        if any(lot_owners[l]>1 for l in u['lot_ids'].split(';')):
            u['candidate_count_population_supported']=False;u['dated_count_population_supported']=False
            u['audit_reasons']+=';overlapping_result_notices_require_correction_review'
    record={'ags':roster['ags'],'procedure_identifier':guid,
            'root_publication_number':roster['root_call_publication_number'],
            'root_call_issue_date':issue,'root_call_publication_date':call_day,
            'followup_days_to_cutoff':(date.fromisoformat(CUTOFF)-date.fromisoformat(call_day)).days,
            'municipal_scope_status':'sole_named_municipal_contracting_party_supported' if scope else 'scope_unresolved',
            'literal_procedure_codes':';'.join(sorted(codes)),'called_category':category,
            'candidate_called_composition_population_supported':scope and category in CALLED,
            'procurement_service_provider_present':any(s['procurement_service_provider_records'] for s in scopes),
            'result_followup_status':'indexed_result_present' if results else 'no_indexed_standard_result_by_cutoff',
            'successful_lot_results':sum(u['result_status']=='selec-w' for u in units),
            'closed_without_winner_lot_results':sum(u['result_status']=='clos-nw' for u in units),
            'candidate_count_lot_results':sum(u['candidate_count_population_supported'] for u in units),
            'dated_supported_count_lot_results':sum(u['dated_count_population_supported'] for u in units),
            'unique_awarded_contracts_in_supported_lots':len({c for u in units if u['candidate_count_population_supported'] for c in u['contract_ids'].split(';') if c}),
            'all_category_negotiated_population_supported':False,
            'continuous_original_winner_exposure_verified':False,
            'main_study_eligibility_certified':False}
    return record,units


def main():
    originals_path = Path('outputs/nrw-2025-validation/q1-original-records.json')
    originals = json.loads(originals_path.read_text())
    with (DOC/'nrw-2025-q1-call-procedures.csv').open(newline='') as f:
        roster = [r for r in csv.DictReader(f) if r['original_issue_and_publication_in_q1']=='True']
    assert len(roster)==37 and len({r['procedure_identifier'] for r in roster})==37
    selected_guids={r['procedure_identifier'] for r in roster}
    selected=[r for r in originals if r['xml']['procedure_identifier'] in selected_guids]
    by_file=defaultdict(list)
    for r in selected:by_file[r['export_file']].append(r)
    pins={p['file']:p for filename in ('retrieval.json','alignment-retrieval.json','q1-completion-retrieval.json') for p in json.loads((RAW/filename).read_text())['exports']}
    roots={};source_rows=[]
    for filename,records in by_file.items():
        with verified_archive(RAW,pins[filename]) as archive:
            for r in records:
                raw=archive.read(r['xml_file'])
                if hashlib.sha256(raw).hexdigest()!=r['xml_sha256'] or len(raw)!=r['xml_bytes']:
                    raise ValueError('Original XML changed')
                root=safe_xml(raw);idx=r['index']
                if identity(text_at(root,'cbc:ID'),text_at(root,'cbc:VersionID'))!=identity(idx['notice-identifier'],idx['notice-version']) or text_at(root,'cbc:ContractFolderID')!=idx['procedure-identifier']:
                    raise ValueError('Source identity changed')
                number=idx['publication-number'];roots[number]=root
                source_rows.append({'publication_number':number,'notice_type':idx['notice-type'],'procedure_identifier':idx['procedure-identifier'],
                                    'xml_file':r['xml_file'],'xml_sha256':r['xml_sha256'],'xml_bytes':r['xml_bytes'],
                                    'export_url':pins[filename]['url'],'export_file':filename,'export_sha256':pins[filename]['sha256']})
    events=json.loads(Path('outputs/nrw-election-register-2025/events.json').read_text())
    selected_events=[]
    for e in events:
        if e['decisive_pair'] and e['absolute_margin_pp']<=5:
            selected_events.append({**e,'municipality':e['municipality_source'].removeprefix('Krfr. Stadt ').removesuffix(', Stadt')})
    aliases=ted.aliases(selected_events)
    election_dates={e['ags']:e['decisive_date'] for e in selected_events}
    by_guid=defaultdict(list)
    for r in selected:by_guid[r['xml']['procedure_identifier']].append(r)
    procedures=[];units=[]
    for r in roster:
        expected={name for name,ags in aliases.items() if ags=={r['ags']}}
        row,lots=audit_procedure(r,by_guid[r['procedure_identifier']],roots,expected)
        row['post_election_calendar_chronology_supported']=election_dates[r['ags']]<row['root_call_issue_date']
        procedures.append(row);units.extend(lots)
    with (DOC/'nrw-2025-presentation-pairs.csv').open(newline='') as f:presentations={r['ags']:r for r in csv.DictReader(f)}
    with (DOC/'nrw-2025-closest-pair-evidence-review.csv').open(newline='') as f:presentations.update({r['ags']:r for r in csv.DictReader(f)})
    office_sources=json.loads((OFFICE/'retrieval.json').read_text())
    office_observations=json.loads((OFFICE/'office-observations.json').read_text())
    for observation in office_observations:
        pin=office_sources[observation['source_id']];raw=(OFFICE/pin['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=pin['sha256'] or len(raw)!=pin['bytes'] or ' '.join(observation['locator_quote'].split()) not in ' '.join(original_visible_text(raw,pin['file']).split()):
            raise ValueError('Office original or locator changed')
    elections=[]
    for e in selected_events:
        ps=[p for p in procedures if p['ags']==e['ags']]
        us=[u for u in units if u['ags']==e['ags'] and u['candidate_count_population_supported']]
        pres=presentations.get(e['ags'],{})
        mixed=pres.get('pair_status')=='mixed_public_presentation'
        observations=[r for r in office_observations if r['ags']==e['ags']]
        elections.append({'ags':e['ags'],'municipality':e['municipality'],'absolute_margin_pp':e['absolute_margin_pp'],
                          'pair_status':pres.get('pair_status','unreviewed_in_this_cohort_batch'),
                          'female_presented_winner':pres.get('female_presented_winner') if mixed else None,
                          'original_q1_procedures':len(ps),
                          'candidate_called_composition_procedures':sum(p['candidate_called_composition_population_supported'] for p in ps),
                          'procedures_without_indexed_standard_result':sum(p['result_followup_status']=='no_indexed_standard_result_by_cutoff' for p in ps),
                          'candidate_tender_count_lot_results':len(us),'procedures_with_supported_count_result':len({u['procedure_identifier'] for u in us}),
                          'known_mixed_with_called_composition_inventory':mixed and bool(ps),
                          'known_mixed_with_count_inventory':mixed and bool(us),
                          'new_office_role_observations':len(observations),
                          'original_winner_office_review_status':'source_bounded_role_observations_available' if observations else 'not_reviewed_in_this_bounded_office_batch',
                          'continuous_original_winner_exposure_verified':False,
                          'independent_second_coding':False,'main_study_eligibility_certified':False})
    csv_write(DOC/'nrw-2025-q1-procedure-eligibility.csv',procedures)
    csv_write(DOC/'nrw-2025-q1-result-eligibility.csv',units)
    csv_write(DOC/'nrw-2025-q1-linked-election-inventory.csv',elections)
    csv_write(DOC/'nrw-2025-q1-eligibility-source-manifest.csv',source_rows)
    csv_write(DOC/'nrw-2025-q1-office-source-manifest.csv',[{'source_id':key,'provider':urlparse(pin['url']).netloc,**pin} for key,pin in office_sources.items()])
    csv_write(DOC/'nrw-2025-q1-office-observations.csv',[{k:r[k] for k in ('ags','source_id','document_date','role_observation_date','date_precision','observation_type','continuous_officeholding_verified')} for r in office_observations])
    mixed_calls=[e for e in elections if e['known_mixed_with_called_composition_inventory']]
    mixed_counts=[e for e in elections if e['known_mixed_with_count_inventory']]
    summary={'checked_on_utc':'2026-10-11','original_q1_procedures':len(procedures),'municipalities_with_q1_procedures':sum(bool(e['original_q1_procedures']) for e in elections),
             'scope_status_counts':dict(Counter(p['municipal_scope_status'] for p in procedures)),
             'literal_called_category_counts':dict(Counter(p['called_category'] for p in procedures)),
             'candidate_called_composition_procedures':sum(p['candidate_called_composition_population_supported'] for p in procedures),
             'no_indexed_standard_result_procedures':sum(p['result_followup_status']=='no_indexed_standard_result_by_cutoff' for p in procedures),
             'result_lot_units':len(units),'successful_result_lot_units':sum(u['result_status']=='selec-w' for u in units),
             'closed_without_winner_lot_units':sum(u['result_status']=='clos-nw' for u in units),
             'candidate_count_lot_units':sum(u['candidate_count_population_supported'] for u in units),
             'dated_supported_count_lot_units':sum(u['dated_count_population_supported'] for u in units),
             'cross_lot_contract_supported_units':sum(u['cross_lot_contract_supported'] for u in units),
             'distinct_awarded_contracts_in_supported_lots':sum(p['unique_awarded_contracts_in_supported_lots'] for p in procedures),
             'original_result_xml_notices':sum(r['index']['notice-type']=='can-standard' for r in selected),
             'minimum_call_followup_days':min(p['followup_days_to_cutoff'] for p in procedures),
             'maximum_call_followup_days':max(p['followup_days_to_cutoff'] for p in procedures),
             'known_mixed_elections_with_called_inventory':len(mixed_calls),
             'called_inventory_female_presented_wins':sum(e['female_presented_winner']=='True' for e in mixed_calls),
             'called_inventory_female_presented_losses':sum(e['female_presented_winner']=='False' for e in mixed_calls),
             'known_mixed_elections_with_count_inventory':len(mixed_counts),
             'count_inventory_female_presented_wins':sum(e['female_presented_winner']=='True' for e in mixed_counts),
             'count_inventory_female_presented_losses':sum(e['female_presented_winner']=='False' for e in mixed_counts),
             'known_mixed_count_lot_units':sum(e['candidate_tender_count_lot_results'] for e in mixed_counts),
             'certified_main_study_elections':0,'causal_effects_estimated':False,'primary_outcome_rates_estimated':False,
             'all_category_negotiated_population_supported':False,'office_role_observations':len(office_observations),
             'independent_second_coding_completed':False,
             'inputs':[{'artifact':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [originals_path,DOC/'nrw-2025-q1-call-procedures.csv',Path('outputs/nrw-election-register-2025/events.json'),DOC/'nrw-2025-presentation-pairs.csv',DOC/'nrw-2025-closest-pair-evidence-review.csv',OFFICE/'office-observations.json',OFFICE/'retrieval.json']]}
    from nrw_early_feasibility import gaussian_t_mde, balanced_required_n
    sample_sizes=[(label,sum(e['female_presented_winner']=='True' for e in sample),
                   sum(e['female_presented_winner']=='False' for e in sample))
                  for label,sample in [('called_composition',mixed_calls),('conditional_tender_count',mixed_counts)]]
    summary['precision_planning']={
        'model':'Independent equal-variance Gaussian pooled two-sample t; not RDD power or observed outcome variance',
        'power':0.8,'two_sided':True,
        'mde_outcome_sd':[{'inventory':label,'elections':wins+losses,'wins':wins,'losses':losses,'per_test_alpha':alpha,
                           'mde_sd':gaussian_t_mde(wins,losses,alpha) if min(wins,losses)>0 and wins+losses>2 else None}
                          for label,wins,losses in sample_sizes for alpha in (.05,.025)],
        'illustrative_balanced_required_elections':[{'effect_sd':effect,'per_test_alpha':.025,
                                                    'total_elections':balanced_required_n(effect,.025)} for effect in (.25,.5,1.0)],
        'two_sided_balanced_full_permutation_minimum_p':[
            {'inventory':label,'elections':wins+losses,'wins':wins,'losses':losses,
             'minimum_p':2/math.comb(wins+losses,wins) if wins==losses and wins>0 else None}
            for label,wins,losses in sample_sizes],
        'permutation_assumptions':'Fixed treated counts; all allocations equally likely; absolute difference-in-means statistic; balanced complementary allocations. Not a general RDD impossibility result.',
        'effect_threshold_prespecified':False}
    (DOC/'nrw-2025-q1-eligibility-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
