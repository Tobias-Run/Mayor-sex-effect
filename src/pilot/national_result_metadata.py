"""CSV total-tender availability discovery, never an original outcome audit."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
from bandwidth_window_expansion import monthly_sources,check_pin
from national_scale_expansion import load_frame,niedersachsen_aliases
from cohort_expansion_national import notice_key,municipal_match,national_day
from federal_procurement import csv_rows,verified_archive
from nrw_2025_validation import csv_write

def positive_total_count(row,lot_rows):
    value=row['receivedSubmissionsCount']
    return row['receivedSubmissionsType']=='tenders' and value.isdigit() and int(value)>0 and len(lot_rows)==1 and lot_rows[0]['winnerChosen']=='selec-w'

def main():
    root=Path('data/raw/national-joint-expansion-2026-10-11');doc=Path('docs/feasibility')
    for p in json.loads((root/'result-metadata-pins.json').read_text())['inputs']:check_pin(p,p['artifact'])
    frame=[e for e in load_frame()[0] if e['absolute_margin_pp']<=10];aliases=niedersachsen_aliases(frame)
    aliases['stadt velten - die bürgermeisterin'].add('12065332')
    calls=list(csv.DictReader((doc/'national-joint-call-discovery.csv').open()));guids={(c['ags'],c['procedure_identifier_source']) for c in calls if c['procedure_identifier_source']}
    retained=[];seen={};types=Counter();domestic_stats=0;domestic_results=0
    for base,pin in monthly_sources(False):
        with verified_archive(base,pin) as z:
            buyers=defaultdict(list)
            for r in csv_rows(z,'organisation.csv'):
                if r['organisationRole']=='buyer':buyers[notice_key(r)].append(r)
            results={}
            for r in csv_rows(z,'notice.csv'):
                if r['noticeType']!='can-standard':continue
                k=notice_key(r);ags,reason=municipal_match(buyers.get(k,[]),aliases)
                if not ags:continue
                payload=json.dumps({'row':r,'buyers':buyers[k]},sort_keys=True)
                if k in seen:
                    if seen[k]!=payload:raise ValueError('Conflicting result duplicate')
                    continue
                seen[k]=payload;results[k]=(ags,r)
                domestic_results+=int(k[0].isdigit())
            lots=defaultdict(list)
            for r in csv_rows(z,'procedureLotResult.csv'):
                k=notice_key(r)
                if k in results:lots[(k,r['procedureLotResultNumber'])].append(r)
            statistics=defaultdict(list)
            for r in csv_rows(z,'receivedSubmissions.csv'):
                k=notice_key(r)
                if k in results:statistics[(k,r['procedureLotResultNumber'])].append(r)
            for (k,number),rows in statistics.items():
                totals=[r for r in rows if r['receivedSubmissionsType']=='tenders']
                if len(totals)!=1:types['missing_or_multiple_total_records']+=1;continue
                r=totals[0]
                if not positive_total_count(r,lots[(k,number)]):types['not_positive_unique_successful_lot_result']+=1;continue
                ags,n=results[k];domestic_stats+=int(k[0].isdigit())
                retained.append({'ags':ags,'national_notice_identifier':k[0],'version':k[1],'publication_day_berlin':national_day(n['publicationDate']),'procedure_identifier_source':n['procedureIdentifier'],'lot_result_identifier':number,'lot_identifier_source':lots[(k,number)][0]['lotIdentifier'],'positive_total_tenders_metadata':int(r['receivedSubmissionsCount']),'call_first_guid_metadata_match':bool(n['procedureIdentifier'] and (ags,n['procedureIdentifier']) in guids),'domestic_numeric_notice_id':k[0].isdigit(),'original_award_graph_verified':False,'main_study_eligibility_certified':False,'source_export_file':pin['file'],'source_export_sha256':pin['sha256']})
        print('Result fields inspected',pin['period'],flush=True)
    csv_write(doc/'national-result-metadata-statistics.csv',retained)
    summary={'retained_national_events':654,'buyer_matched_standard_result_notice_versions':len(seen),'domestic_numeric_standard_result_notices':domestic_results,'positive_unique_total_tender_metadata_rows':len(retained),'municipalities_with_positive_count_metadata':len({r['ags'] for r in retained}),'domestic_numeric_positive_count_metadata_rows':domestic_stats,'metadata_rows_with_call_first_guid_match':sum(r['call_first_guid_metadata_match'] for r in retained),'original_outcomes_added':0,'certified_main_study_elections':0,'limitations':'Partial CSV result-field discovery only. No original issue/contract/award graph, revision resolution, treatment assignment, office exposure or complete follow-up established. No silent replacement of original outcome standards.','excluded_lot_result_groups':dict(types)}
    (doc/'national-result-metadata-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
