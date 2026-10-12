"""Audit historical OCDS fields for all official close NRW 2020 pairs."""
import csv,gzip,hashlib,json,math
from pathlib import Path
from collections import Counter,defaultdict
from bandwidth_window_expansion import check_pin
from national_scale_expansion import niedersachsen_aliases
from bavaria_bounded_route import normal_text
from nrw_2025_validation import csv_write
from nrw_close_pair_screen import audit_reviews,original_events

RAW=Path('data/raw/creative-causal-routes-2026-10-12')
OUT=Path('outputs/creative-causal-routes-2026-10-12')
DOC=Path('docs/feasibility')

def total_statistics(record):
    result=[]
    for row in record.get('bids',{}).get('statistics',[]):
        value=row.get('value')
        if row.get('measure') in ('bids','totalBids') and isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>0 and int(value)==value:
            result.append({'field':'bids.statistics.'+row['measure'],'lot':row.get('relatedLot',''),'count':int(value)})
    value=record.get('tender',{}).get('numberOfTenderers')
    if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>0 and int(value)==value:
        result.append({'field':'tender.numberOfTenderers','lot':'whole_procedure_unspecified','count':int(value)})
    return result

def earliest_call_date(record):
    dates=[d.get('datePublished','')[:10] for d in record.get('tender',{}).get('documents',[]) if d.get('documentType')=='tenderNotice' and d.get('datePublished')]
    return min(dates) if dates else None

def main():
    for p in json.loads((RAW/'protocol-before-extraction.json').read_text())['inputs']:check_pin(p,p['artifact'])
    elections=json.loads(Path('outputs/national-joint-expansion-2026-10-11/nrw-2020-selected-elections.json').read_text());aliases=niedersachsen_aliases(elections)
    root=RAW/'opentender';pins=json.loads((root/'retrieval.json').read_text())['sources']
    retained=[];summary_rows=[];stats=Counter();all_ids=defaultdict(set)
    for pin in pins:
        if pin['status']!='acquired':continue
        check_pin(pin,root/pin['file']);seen={};dispositions=Counter();decompressed=0;matched=0
        with gzip.open(root/pin['file'],'rb') as f:
            while raw:=f.readline(64*1024**2+1):
                if len(raw)>64*1024**2:raise ValueError('Record exceeds source inspection bound')
                decompressed+=len(raw)
                if decompressed>1024**3:raise ValueError('Annual source exceeds decompression bound')
                r=json.loads(raw);ocid=r['ocid'];fingerprint=hashlib.sha256(raw).hexdigest()
                if ocid in seen:
                    if seen[ocid]!=fingerprint:raise ValueError('Conflicting compiled release within annual file')
                    dispositions['identical_duplicate_ocid']+=1;continue
                seen[ocid]=fingerprint;all_ids[ocid].add(pin['period'])
                buyer=r.get('buyer',{});possible=aliases.get(normal_text(buyer.get('name','')),set())
                if len(possible)!=1:continue
                parties=[p for p in r.get('parties',[]) if 'buyer' in p.get('roles',[])]
                if len(parties)!=1 or parties[0].get('id')!=buyer.get('id') or normal_text(parties[0].get('name',''))!=normal_text(buyer.get('name','')):dispositions['inconsistent_or_multiple_buyer_roles']+=1;continue
                if parties[0].get('address',{}).get('countryName') not in (None,'','DE','DEU','Deutschland','Germany'):dispositions['country_conflict']+=1;continue
                ags=next(iter(possible));matched+=1;day=earliest_call_date(r)
                in_year=bool(day and pin['period']+'-01-01'<=day<=pin['period']+'-12-31')
                for s in r.get('bids',{}).get('statistics',[]):stats[(pin['period'],s.get('measure',''))]+=1
                totals=total_statistics(r)
                docs=r.get('tender',{}).get('documents',[])+[d for a in r.get('awards',[]) for d in a.get('documents',[])]
                doc_dates=[d.get('datePublished','')[:10] for d in docs if d.get('datePublished')]
                first=min(doc_dates) if doc_dates else None
                retained.append({'ags':ags,'period':pin['period'],'ocid':ocid,'buyer_name':buyer['name'],'earliest_tender_document_publication_date':day,'call_metadata_in_target_calendar_year':in_year,'earliest_document_publication_date':first,'first_document_in_target_calendar_year':bool(first and pin['period']+'-01-01'<=first<=pin['period']+'-12-31'),'release_date':r.get('date'),'total_tender_statistics':totals,'procurement_method':r.get('tender',{}).get('procurementMethod'),'procurement_method_details':r.get('tender',{}).get('procurementMethodDetails'),'has_award_metadata':bool(r.get('awards')),'source_documents':docs,'source_dataset_sha256':pin['sha256'],'original_call_award_graph_verified':False,'main_study_eligibility_certified':False})
        summary_rows.append({'period':pin['period'],'compiled_process_records':len(seen),'buyer_matched_processes':matched,'target_year_call_metadata_processes':sum(r['call_metadata_in_target_calendar_year'] and r['period']==pin['period'] for r in retained),'matched_positive_total_count_metadata_processes':sum(bool(r['total_tender_statistics']) and r['call_metadata_in_target_calendar_year'] and r['period']==pin['period'] for r in retained),'decompressed_bytes_inspected':decompressed,'dispositions':dict(dispositions)})
        print('Inspected historical year',pin['period'],flush=True)
    (OUT/'historical-matched-processes.json').write_text(json.dumps(retained,indent=2)+'\n')
    inventory=[]
    for e in elections:
        rs=[r for r in retained if r['ags']==e['ags'] and r['call_metadata_in_target_calendar_year']]
        cs={year:[r for r in rs if r['period']==year] for year in ('2019','2021')}
        inventory.append({'ags':e['ags'],'municipality':e['municipality'],'margin_stratum':e['margin_stratum'],'pre2019_call_metadata_processes':len(cs['2019']),'post2021_call_metadata_processes':len(cs['2021']),'pre2019_positive_count_metadata_processes':sum(bool(r['total_tender_statistics']) for r in cs['2019']),'post2021_positive_count_metadata_processes':sum(bool(r['total_tender_statistics']) for r in cs['2021']),'has_pre_and_post_call_metadata':bool(cs['2019'] and cs['2021']),'has_pre_and_post_count_metadata':any(r['total_tender_statistics'] for r in cs['2019']) and any(r['total_tender_statistics'] for r in cs['2021']),'baseline_scope_reporting_compatible_verified':False,'main_study_eligibility_certified':False})
    csv_write(DOC/'creative-historical-bridge-inventory.csv',inventory)
    choices=[r for r in retained if r['first_document_in_target_calendar_year']]
    method_inventory=[]
    for e in elections:
        cs={year:[r for r in choices if r['ags']==e['ags'] and r['period']==year] for year in ('2019','2021')}
        method_inventory.append({'ags':e['ags'],'municipality':e['municipality'],'source_observed_processes_pre2019':len(cs['2019']),'source_observed_processes_post2021':len(cs['2021']),'method_field_present_pre2019':sum(bool(r['procurement_method']) for r in cs['2019']),'method_field_present_post2021':sum(bool(r['procurement_method']) for r in cs['2021']),'method_detail_field_present_pre2019':sum(bool(r['procurement_method_details']) for r in cs['2019']),'method_detail_field_present_post2021':sum(bool(r['procurement_method_details']) for r in cs['2021']),'has_method_metadata_pre_and_post':any(r['procurement_method_details'] for r in cs['2019']) and any(r['procurement_method_details'] for r in cs['2021']),'all_procedure_reporting_and_no_call_timing_verified':False,'main_study_eligibility_certified':False})
    csv_write(DOC/'creative-procedure-choice-opportunity.csv',method_inventory)
    review_root=Path('data/raw/national-joint-expansion-2026-10-11/candidates')
    for p in json.loads((review_root/'accepted-source-pins.json').read_text())['inputs']:check_pin(p,p['artifact'])
    source_rows={r['source_id']:r for r in csv.DictReader((DOC/'nrw-close-pair-source-manifest.csv').open())}
    for p in json.loads((review_root/'source-retrieval.json').read_text()):source_rows[p['source_id']]=p
    review_rows=audit_reviews(original_events(source_rows),json.loads((review_root/'new-reviews.json').read_text())['reviews'],source_rows)
    label_map={r['ags']:r for r in review_rows}
    candidate_opportunities=[dict(r,first_coder_pair_status=label_map[r['ags']]['pair_status'],female_presented_winner=label_map[r['ags']]['female_presented_winner'],mixed_pair_with_pre_post_method_metadata=r['has_method_metadata_pre_and_post'] and label_map[r['ags']]['pair_status']=='mixed_public_presentation',independent_second_coding_completed=False) for r in method_inventory]
    csv_write(DOC/'creative-procedure-choice-assignment-opportunities.csv',candidate_opportunities)
    summary={'selected_elections':55,'years':summary_rows,'municipalities_with_pre_and_post_call_metadata':sum(r['has_pre_and_post_call_metadata'] for r in inventory),'municipalities_with_pre_and_post_positive_count_metadata':sum(r['has_pre_and_post_count_metadata'] for r in inventory),'matched_bids_statistics_measures':[{'period':p,'measure':m,'rows':n} for (p,m),n in sorted(stats.items())],'cross_year_ocids_in_full_datasets':sum(len(periods)>1 for periods in all_ids.values()),'downloaded_compressed_bytes':sum(p.get('bytes',0) for p in pins),'source_license':'CC BY-NC-SA 4.0, as described by OCP registry; source snapshots/person/process records remain local','original_supported_outcomes_added':0,'certified_main_study_elections':0,'warning':'Compiled/transformed source metadata, not original TED graph evidence or complete temporal reporting. Baseline/post counts are acquisition opportunities; no outcome correlation, RDD precision improvement or causal effect estimated.'}
    methods=Counter((r['period'],r['procurement_method'],r['procurement_method_details']) for r in choices)
    leads=[r for r in candidate_opportunities if r['mixed_pair_with_pre_post_method_metadata']]
    summary.update({'first_document_year_matched_processes':len(choices),'municipalities_with_pre_and_post_procedure_detail_metadata':sum(r['has_method_metadata_pre_and_post'] for r in method_inventory),'first_coder_mixed_pairs_with_pre_post_method_metadata':len(leads),'female_presented_wins_among_method_leads':sum(r['female_presented_winner']=='true' for r in leads),'female_presented_losses_among_method_leads':sum(r['female_presented_winner']=='false' for r in leads),'literal_method_metadata_distribution':[{'period':p,'method':m,'method_details':d,'processes':n} for (p,m,d),n in sorted(methods.items(),key=lambda item:tuple(str(x) for x in item[0]))],'procedure_choice_universe_certified':False})
    (DOC/'creative-historical-bridge-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (DOC/'creative-historical-source-manifest.json').write_text(json.dumps({'sources':pins,'source_registry':'https://data.open-contracting.org/en/publication/53','source_license':summary['source_license']},indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
