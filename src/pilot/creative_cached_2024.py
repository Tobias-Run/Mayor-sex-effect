"""Unfiltered older-cohort calendar-2024 discovery and cached original audit."""
import argparse,csv,hashlib,json,shutil,sys
from pathlib import Path
from collections import Counter,defaultdict
from unittest.mock import patch
from bandwidth_window_expansion import check_pin,band,first_metadata_occurrence
from national_scale_expansion import niedersachsen_aliases
from cohort_expansion_national import municipal_match,notice_key,national_day
from federal_procurement import verified_archive,csv_rows
from nrw_2025_validation import csv_write
from nrw_close_pair_screen import audit_reviews,original_events
from national_joint_originals import exports as newer_exports
from bandwidth_window_expansion import monthly_sources
import expanded_original_audit as audit
import bavaria_bounded_route as ted

RAW=Path('data/raw/creative-causal-routes-2026-10-12')
OUT=Path('outputs/creative-causal-routes-2026-10-12')
DOC=Path('docs/feasibility')

def older_exports():
    return [(Path('data/raw/federal-procurement'),p) for p in json.loads((DOC/'federal-procurement-export-manifest.json').read_text())]

def complete_newer_exports():
    root=Path('data/raw/national-joint-expansion-2026-10-11/original-recovery')
    return newer_exports()+[(root,p) for p in json.loads((root/'retrieval.json').read_text())['exports']]

def shared_guids(calls):
    mapping=defaultdict(set)
    for c in calls:
        if c['procedure_identifier_source']:mapping[c['procedure_identifier_source']].add((c['cohort'],c['ags']))
    return {guid for guid,keys in mapping.items() if len(keys)>1}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire-context',action='store_true');args=parser.parse_args()
    OUT.mkdir(exist_ok=True,parents=True)
    for pin in json.loads((RAW/'protocol-before-extraction.json').read_text())['inputs']:check_pin(pin,pin['artifact'])
    nrw=json.loads(Path('outputs/national-joint-expansion-2026-10-11/nrw-2020-selected-elections.json').read_text())
    ni=[e for e in json.loads(Path('outputs/bandwidth-window-expansion-2026-10-11/selected-elections.json').read_text()) if e['cohort']=='Niedersachsen 2021']
    elections=nrw+ni
    assert len(elections)==91 and len({e['ags'] for e in elections})==91
    for e in elections:e['margin_stratum']=band(e['absolute_margin_pp'])
    aliases=niedersachsen_aliases(elections);by_ags={e['ags']:e for e in elections}
    seen={};calls=[];duplicates=0;outside=0
    for root,pin in older_exports():
        if pin['format']!='csv':continue
        with verified_archive(root,pin) as z:
            buyers=defaultdict(list)
            for r in csv_rows(z,'organisation.csv'):
                if r['organisationRole']=='buyer':buyers[notice_key(r)].append(r)
            for r in csv_rows(z,'notice.csv'):
                k=notice_key(r);roles=buyers.get(k,[])
                if not first_metadata_occurrence(seen,k,r,roles):duplicates+=1;continue
                ags,reason=municipal_match(roles,aliases)
                if not ags or r['noticeType']!='cn-standard':continue
                day=national_day(r['publicationDate'])
                if not '2024-01-01'<=day<='2024-12-31':outside+=1;continue
                e=by_ags[ags]
                calls.append({'cohort':e['cohort'],'ags':ags,'municipality':e['municipality'],'margin_stratum':e['margin_stratum'],'national_notice_identifier':k[0],'version':k[1],'publication_day_berlin':day,'procedure_identifier_source':r['procedureIdentifier'],'buyer_name_source':roles[0]['organisationName'],'source_export_file':pin['file'],'source_export_sha256':pin['sha256'],'original_call_verified':False,'main_study_eligibility_certified':False})
        print('Replayed archive',pin['period'],flush=True)
    csv_write(DOC/'creative-2024-call-discovery.csv',calls)
    ambiguous=shared_guids(calls)
    withheld=[c for c in calls if c['procedure_identifier_source'] in ambiguous]
    if withheld:csv_write(DOC/'creative-2024-shared-guid-calls.csv',withheld)
    csv_write(DOC/'creative-2024-election-inventory.csv',[{k:e[k] for k in ('cohort','ags','municipality','decisive_date','margin_stratum','absolute_margin_pp')} for e in elections])
    stage=OUT/'stage';stage.mkdir(exist_ok=True)
    for source,target in [('creative-2024-call-discovery.csv','relaxed-acquisition-national-call-discovery.csv'),('creative-2024-election-inventory.csv','relaxed-acquisition-election-inventory.csv')]:shutil.copyfile(DOC/source,stage/target)
    if ambiguous:
        for p in json.loads((RAW/'shared-guid-before-resumed-audit.json').read_text())['inputs']:check_pin(p,p['artifact'])
        csv_write(stage/'relaxed-acquisition-national-call-discovery.csv',[c for c in calls if c['procedure_identifier_source'] not in ambiguous])
    paths=['docs/feasibility/creative-causal-routes-protocol.md','docs/feasibility/creative-2024-call-discovery.csv','docs/feasibility/creative-2024-election-inventory.csv']
    pins={'inputs':[{'artifact':p,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in paths]}
    pinfile=RAW/'protocol-before-context.json'
    if pinfile.exists():assert json.loads(pinfile.read_text())==pins
    else:pinfile.write_text(json.dumps(pins,indent=2)+'\n')
    cache=complete_newer_exports()+[(r,p) for r,p in older_exports() if p['format']=='eforms']
    argv=['expanded_original_audit']+(['--acquire-context'] if args.acquire_context else [])
    query_original=audit.context_query;snapshot_original=ted.snapshot
    def full_query(guids):
        cohort=next(c['cohort'] for c in calls if c['procedure_identifier_source'] in guids)
        full={c['procedure_identifier_source'] for c in calls if c['cohort']==cohort and c['procedure_identifier_source']}
        return query_original(full)
    def filtered_snapshot(query):
        rs,metadata=snapshot_original(query)
        retained=[r for r in rs if r['procedure-identifier'] not in ambiguous]
        return retained,dict(metadata,shared_guid_notices_withheld=len(rs)-len(retained),audit_retained_context_notices=len(retained))
    with patch.object(audit,'RAW',RAW),patch.object(audit,'OUT',OUT/'original-audit'),patch.object(audit,'DOC',stage),patch.object(audit,'cached_exports',return_value=cache),patch.object(audit,'cohort_window',return_value=('2024-01-01','2024-12-31','calendar_2024_later_term')),patch.object(audit,'context_query',side_effect=full_query),patch.object(ted,'snapshot',side_effect=filtered_snapshot),patch.object(ted,'MAX_PAGES',8),patch.object(sys,'argv',argv):audit.main()
    for p in stage.glob('expanded-original-*'):(DOC/p.name.replace('expanded-original-','creative-2024-original-',1)).write_bytes(p.read_bytes())
    root=Path('data/raw/national-joint-expansion-2026-10-11/candidates')
    for p in json.loads((root/'accepted-source-pins.json').read_text())['inputs']:check_pin(p,p['artifact'])
    sources={r['source_id']:r for r in csv.DictReader((DOC/'nrw-close-pair-source-manifest.csv').open())}
    for p in json.loads((root/'source-retrieval.json').read_text()):sources[p['source_id']]=p
    rows=audit_reviews(original_events(sources),json.loads((root/'new-reviews.json').read_text())['reviews'],sources)
    labels={r['ags']:r for r in rows}
    linked=list(csv.DictReader((stage/'expanded-original-linked-election-inventory.csv').open()))
    current={('NRW 2025',ags) for ags in ('05382040','05954020','05962032','05978024')}|{('Niedersachsen 2021','03257009'),('NRW 2020','05962060')}
    assignment=[];new_mixed=set()
    for e in linked:
        if e['cohort']=='NRW 2020':status=labels[e['ags']]['pair_status'];female=labels[e['ags']]['female_presented_winner']
        elif e['ags']=='03257009':
            p=json.loads((DOC/'original-recovery-assignment-checkpoint.json').read_text());assert p['first_coder_mixed_pair_supported'];status='mixed_public_presentation';female='false'
        else:status='not_reviewed_in_this_batch';female=''
        mixed=status=='mixed_public_presentation' and int(e['observed_supported_tender_statistics'])>0
        if mixed:new_mixed.add((e['cohort'],e['ags']))
        assignment.append(dict(e,first_coder_pair_status=status,female_presented_winner=female,provisional_mixed_count_election=mixed,already_in_current_six_inventory=(e['cohort'],e['ags']) in current,independent_second_coding_completed=False))
    csv_write(DOC/'creative-2024-assignment-inventory.csv',assignment)
    summary=json.loads((DOC/'creative-2024-original-audit-summary.json').read_text())
    summary.update({'checked_on':'2026-10-12','metadata_versions_inspected':len(seen),'identical_duplicates_skipped':duplicates,'municipal_calls_outside_2024':outside,'calendar_2024_mixed_count_elections':len(new_mixed),'additional_independent_election_events_over_current_six':len(new_mixed-current),'overlap_with_current_six':len(new_mixed&current),'current_and_calendar_2024_provisional_election_union':len(current|new_mixed),'current_and_calendar_2024_distinct_municipal_union':len({ags for _,ags in current|new_mixed}),'cohorts_pooled':False,'previous_provisional_mixed_count_elections':6,'warning':'Common calendar-2024 source audit, not a common election-relative window or causal estimator. Candidate measurement is first-coder only; exposure, reporting, corrections, selection and RDD precision remain gates. One election with two windows is counted once.'})
    (DOC/'creative-2024-original-audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
    all_pins=older_exports()+complete_newer_exports()+monthly_sources(False)
    counts=Counter(p['sha256'] for _,p in all_pins);unique={p['sha256']:p for _,p in all_pins}
    accounting={'earlier_monthly_archive_bytes':sum(p['bytes'] for _,p in older_exports()),'newer_tranche_manifest_bytes':sum(p['bytes'] for _,p in complete_newer_exports()+monthly_sources(False)),'listed_snapshot_entries':len(all_pins),'unique_archive_sha256_count':len(unique),'duplicate_archive_entries_by_sha256':sum(n-1 for n in counts.values()),'all_listed_archive_bytes':sum(p['bytes'] for _,p in all_pins),'unique_retained_archive_bytes_by_sha256':sum(p['bytes'] for p in unique.values()),'correction':'Earlier combined-source ceilings covered newer acquisition tranches only; the older monthly archive cache was omitted from those accounting statements. Earlier receipts/limits preserved. This ledger covers the listed source manifests, not every file in the repository.','additional_downloaded_archive_bytes_in_this_route':0}
    (DOC/'creative-source-accounting.json').write_text(json.dumps(accounting,indent=2)+'\n')

if __name__=='__main__':main()
