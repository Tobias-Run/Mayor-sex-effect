"""Call-first expanded-cohort context and exact original-cache audit.

Use --acquire-context once; replay without network using pinned local sources.
Domestic IDs without GUIDs stay unresolved. No old artifacts are overwritten.
"""
import argparse,csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
from bandwidth_window_expansion import cohort_window,followup_end,SOURCE_CUTOFF,check_pin
from national_scale_expansion import niedersachsen_aliases
from cohort_expansion import FIELDS
from nrw_2025_validation import original_records,csv_write
from nrw_phase_linkage import competition_graph
from nrw_2025_q1_eligibility import lot_audit,municipal_scope
from federal_procurement import verified_archive,safe_xml,text_at,source_date
import bavaria_bounded_route as ted

RAW=Path('data/raw/expanded-original-audit-2026-10-11')
OUT=Path('outputs/expanded-original-audit-2026-10-11')
DOC=Path('docs/feasibility')


def context_query(guids):
    if not guids: raise ValueError('Empty call-first GUID query')
    return '('+' OR '.join('procedure-identifier = '+json.dumps(g) for g in sorted(guids))+') AND (notice-type = cn-standard OR notice-type = can-standard) AND publication-date <= 20260930'


def cached_exports():
    root=Path('data/raw/nrw-2025-validation/federal-eforms')
    sources=[(root,p) for name in ('retrieval.json','alignment-retrieval.json','q1-completion-retrieval.json') for p in json.loads((root/name).read_text())['exports']]
    other=Path('data/raw/cohort-expansion-2026-10-11/national-xml')
    sources += [(other,p) for p in json.loads((other/'retrieval.json').read_text())['exports']]
    return sources


def chronological_statistic(unit,issue,call_pub,result_issue,result_pub,target_end):
    day=unit['contract_conclusion_date']
    return bool(unit['award_graph_supported'] and unit['total_count_supported'] and day and issue and call_pub and result_issue and result_pub and target_end and issue<=call_pub<=day<=result_issue<=result_pub<=min(target_end,SOURCE_CUTOFF.isoformat()))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire-context',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    pins=json.loads((RAW/'protocol-before-context.json').read_text())
    for pin in pins['inputs']:check_pin(pin,pin['artifact'])
    elections=list(csv.DictReader((DOC/'relaxed-acquisition-election-inventory.csv').open()))
    calls=list(csv.DictReader((DOC/'relaxed-acquisition-national-call-discovery.csv').open()))
    by_guid=defaultdict(list)
    for c in calls:
        if c['procedure_identifier_source']:by_guid[c['procedure_identifier_source']].append(c)
    notices,queries=[],[]
    for cohort in sorted({c['cohort'] for c in calls}):
        guids={c['procedure_identifier_source'] for c in calls if c['cohort']==cohort and c['procedure_identifier_source']}
        slug=cohort.lower().replace(' ','-')
        ted.RAW=RAW/slug;ted.FIELDS=FIELDS;ted.START=None;ted.END='20260930'
        query=context_query(guids)
        if args.acquire_context and not (ted.RAW/'retrieval.json').exists():ted.acquire(query)
        rows,metadata=ted.snapshot(query)
        for n in rows:
            if n['procedure-identifier'] not in guids:raise ValueError('Context outside selected GUID scope')
            n=dict(n,cohort=cohort);notices.append(n)
        queries.append(dict(cohort=cohort,**metadata))
    if len({n['publication-number'] for n in notices})!=len(notices):raise ValueError('Procedure context crosses cohort scope')
    originals={};exports=cached_exports();source_rows=[]
    for root in sorted({root for root,_ in exports}):
        ps=[p for r,p in exports if r==root]
        found,_=original_records(notices,ps,root)
        for rec in found:
            number=rec['index']['publication-number']
            if number in originals:
                if originals[number]['xml_sha256']!=rec['xml_sha256']:raise ValueError('Conflicting cached originals')
                continue
            originals[number]=dict(rec,export_root=str(root))
    roots={}
    archive_groups=defaultdict(list)
    for number,rec in originals.items():archive_groups[(rec['export_root'],rec['export_file'])].append((number,rec))
    for (root,file),recs in archive_groups.items():
        pin=next(p for r,p in exports if str(r)==root and p['file']==file)
        with verified_archive(root,pin) as archive:
            for number,rec in recs:
                raw=archive.read(rec['xml_file'])
                if hashlib.sha256(raw).hexdigest()!=rec['xml_sha256']:raise ValueError('XML original changed')
                roots[number]=safe_xml(raw)
                source_rows.append({'publication_number':number,'procedure_identifier':rec['index']['procedure-identifier'],'xml_sha256':rec['xml_sha256'],'xml_file':rec['xml_file'],'export_url':pin['url'],'export_file':file,'export_sha256':pin['sha256']})
    context=defaultdict(list)
    for n in notices:context[n['procedure-identifier']].append(n)
    procedures,units=[],[]
    for guid,cs in sorted(by_guid.items()):
        keys={(c['cohort'],c['ags']) for c in cs}
        if len(keys)!=1:raise ValueError('GUID assigned to multiple elections')
        cohort,ags=next(iter(keys));event=next(e for e in elections if e['cohort']==cohort and e['ags']==ags)
        rows=context[guid];missing=[n['publication-number'] for n in rows if n['publication-number'] not in originals]
        nodes=[dict(originals[n['publication-number']]['xml'],ags=ags,publication_number=n['publication-number'],competition_publication_date=source_date(n['publication-date'])) for n in rows if n['notice-type']=='cn-standard' and n['publication-number'] in originals]
        calls_complete=all(n['publication-number'] in originals for n in rows if n['notice-type']=='cn-standard')
        graph=competition_graph(nodes) if nodes and calls_complete else {'graph_status':'original_call_graph_pending'}
        number=graph.get('candidate_competition_publication_number');root=originals.get(number)
        issue=source_date(root['xml']['notice_issue_date_source']) if root else None
        pub=graph.get('candidate_competition_date')
        start,end,_=cohort_window(cohort)
        window=bool(issue and pub and start<=issue<=pub<=end)
        target=followup_end(pub).isoformat() if pub else None
        mature=bool(target and target<=SOURCE_CUTOFF.isoformat())
        aliases=set(niedersachsen_aliases([event]))
        if ags=='12065332':aliases.add('stadt velten - die bürgermeisterin')
        available=[n for n in rows if n['publication-number'] in roots]
        scopes={n['publication-number']:municipal_scope(roots[n['publication-number']],aliases)['scope_status']=='sole_named_municipal_contracting_party_supported' for n in available}
        root_scope=bool(number and scopes.get(number) and all(scopes.get(n['publication-number']) for n in rows if n['notice-type']=='cn-standard'))
        codes={text_at(roots[n['publication-number']],'cac:TenderingProcess/cbc:ProcedureCode') for n in rows if n['notice-type']=='cn-standard' and n['publication-number'] in roots}
        category=next(iter(codes)) if len(codes)==1 else 'category_unresolved'
        category_ok=category in ('open','restricted','neg-w-call')
        own=[]
        for n in available:
            num=n['publication-number']
            if n['notice-type']!='can-standard':continue
            result_issue=source_date(originals[num]['xml']['notice_issue_date_source']);result_pub=source_date(n['publication-date'])
            for u in lot_audit(roots[num]):
                supported=bool(window and root_scope and scopes[num] and category_ok and chronological_statistic(u,issue,pub,result_issue,result_pub,target))
                own.append({'cohort':cohort,'ags':ags,'procedure_identifier':guid,'result_publication_number':num,**u,'observed_original_supported_statistic':supported,'nine_month_target_mature_at_cutoff':mature,'result_revision_review_pending':False,'main_study_eligibility_certified':False})
        owners=Counter(lot for u in own for lot in u['lot_ids'].split(';'))
        for u in own:
            if any(owners[lot]>1 for lot in u['lot_ids'].split(';')):
                u['result_revision_review_pending']=True;u['observed_original_supported_statistic']=False
        units+=own
        procedures.append({'cohort':cohort,'ags':ags,'municipality':event['municipality'],'margin_stratum':event['margin_stratum'],'procedure_identifier':guid,'selected_call_notice_versions':len(cs),'context_notices':len(rows),'original_xml_matched':len(available),'missing_original_notices':len(missing),'documented_call_graph_status':graph['graph_status'],'root_publication_number':number,'root_issue_date':issue,'root_publication_date':pub,'original_issue_publication_inside_window':window,'sole_original_municipal_root_buyer_supported':root_scope,'original_called_category':category,'nine_month_followup_target_end':target,'nine_month_target_mature_at_cutoff':mature,'indexed_standard_result_notices':sum(n['notice-type']=='can-standard' for n in rows),'observed_supported_tender_statistics':sum(u['observed_original_supported_statistic'] for u in own),'complete_indexed_original_context':not missing and bool(rows),'main_study_eligibility_certified':False})
    csv_write(DOC/'expanded-original-procedure-audit.csv',procedures)
    if units:csv_write(DOC/'expanded-original-result-audit.csv',units)
    if source_rows:csv_write(DOC/'expanded-original-xml-source-manifest.csv',source_rows)
    linked=[]
    for event in elections:
        ps=[p for p in procedures if p['cohort']==event['cohort'] and p['ags']==event['ags']]
        cs=[c for c in calls if c['cohort']==event['cohort'] and c['ags']==event['ags']]
        linked.append({'cohort':event['cohort'],'ags':event['ags'],'municipality':event['municipality'],'margin_stratum':event['margin_stratum'],'selected_standard_call_notices':len(cs),'domestic_call_records_without_guid':sum(not c['procedure_identifier_source'] for c in cs),'observed_guid_procedures':len(ps),'original_window_and_buyer_supported_procedures':sum(p['original_issue_publication_inside_window'] and p['sole_original_municipal_root_buyer_supported'] for p in ps),'observed_supported_tender_statistics':sum(p['observed_supported_tender_statistics'] for p in ps),'presentation_review_added_in_this_phase':False,'main_study_eligibility_certified':False})
    csv_write(DOC/'expanded-original-linked-election-inventory.csv',linked)
    (OUT/'context.json').write_text(json.dumps(notices,indent=2)+'\n')
    (OUT/'originals.json').write_text(json.dumps(list(originals.values()),indent=2)+'\n')
    (DOC/'expanded-original-context-manifest.json').write_text(json.dumps({'queries':queries},indent=2)+'\n')
    summary={'checked_on':'2026-10-11','active_elections_retained':len(linked),'selected_standard_call_records':len(calls),'domestic_records_without_guid':sum(not c['procedure_identifier_source'] for c in calls),'observed_call_first_guids':len(by_guid),'indexed_context_notices':len(notices),'cached_export_snapshots_checked':len(exports),'exact_original_xml_notices':len(originals),'missing_indexed_originals':len(notices)-len(originals),'original_window_buyer_supported_procedures':sum(p['original_issue_publication_inside_window'] and p['sole_original_municipal_root_buyer_supported'] for p in procedures),'elections_with_original_window_buyer_support':sum(bool(e['original_window_and_buyer_supported_procedures']) for e in linked),'observed_supported_statistics':sum(u['observed_original_supported_statistic'] for u in units),'elections_with_observed_supported_statistics':sum(bool(e['observed_supported_tender_statistics']) for e in linked),'elections_with_supported_statistics_in_new_5_to_10pp_stratum':sum(bool(e['observed_supported_tender_statistics']) and e['margin_stratum']=='over_5_to_10pp' for e in linked),'mature_target_supported_statistics':sum(u['observed_original_supported_statistic'] and u['nine_month_target_mature_at_cutoff'] for u in units),'new_original_xml_download_bytes':0,'new_mixed_count_elections_certified':0,'previous_provisional_mixed_count_elections':4,'certified_main_study_elections':0,'warning':'Cache-first partial original audit, not complete outcome coverage. Domestic GUID gaps, missing originals, result revisions, calendar-immature follow-up and independent candidate coding remain explicit. No new mixed assignment is inferred.'}
    (DOC/'expanded-original-audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
