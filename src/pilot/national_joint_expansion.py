"""Unfiltered national event-to-register screen and official NRW 2020 replay."""
import csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
from national_scale_expansion import load_frame,niedersachsen_aliases
from bandwidth_window_expansion import band,monthly_sources,first_metadata_occurrence,check_pin
from cohort_expansion_national import municipal_match,notice_key,national_day
from federal_procurement import verified_archive,csv_rows
from nrw_2025_validation import csv_write
from nrw_election_register import parse_detail

RAW=Path('data/raw/national-joint-expansion-2026-10-11')
OUT=Path('outputs/national-joint-expansion-2026-10-11')
DOC=Path('docs/feasibility')

def event_key(event):
    return event['ags']+':'+event['decisive_date']

def discovery_window(event):
    return ('2026-01-01','2026-03-31') if event['decisive_date'][:4]=='2025' else ('2025-01-01','2025-12-31')

def eligible_links(events,day):
    return [e for e in events if discovery_window(e)[0]<=day<=discovery_window(e)[1]]

def official_nrw_2020():
    root=Path('data/raw/nrw-2020')
    pins=json.loads((root/'detail-retrieval.json').read_text())
    old=json.loads(Path('outputs/nrw-election-register/events.json').read_text())
    selected=[];manifest=[]
    for e in old:
        pin=pins[e['source_code']]
        parsed=parse_detail(check_pin(pin,root/(e['source_code']+'.txt')).decode('utf-8-sig'),e)
        assert parsed['candidates']==e['candidates'] and parsed['absolute_margin_pp']==e['absolute_margin_pp']
        if not parsed['decisive_pair'] or parsed['absolute_margin_pp']>10:continue
        field='votes_runoff' if parsed['has_runoff'] else 'votes_first'
        pair=[c for c in parsed['candidates'] if c[field] is not None]
        event={'state':'05','cohort':'NRW 2020','ags':parsed['ags'],'municipality':re.sub(r'^Krfr\. Stadt ','',parsed['municipality_source']),'decisive_date':parsed['decisive_date'],'absolute_margin_pp':parsed['absolute_margin_pp'],'margin_stratum':band(parsed['absolute_margin_pp']),'valid_votes':sum(c[field] for c in pair),'candidates':[{'name':c['candidate_name_source'],'votes':c[field],'winner':c['candidate_name_source']==parsed['winner_name_source']} for c in pair]}
        selected.append(event);manifest.append({'ags':event['ags'],'cohort':'NRW 2020','url':pin['url'],'sha256':pin['sha256'],'source_status':'official_final_identities_votes_total_winner_verified'})
    return selected,manifest

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for pin in json.loads((RAW/'protocol-before-discovery.json').read_text())['inputs']:check_pin(pin,pin['artifact'])
    frame=[e for e in load_frame()[0] if e['absolute_margin_pp']<=10]
    assert len(frame)==654 and len({e['ags'] for e in frame})==629
    nrw,official=official_nrw_2020();assert len(nrw)==55
    (OUT/'nrw-2020-selected-elections.json').write_text(json.dumps(nrw,indent=2)+'\n')
    csv_write(DOC/'national-joint-nrw-2020-official-manifest.csv',official)
    by_ags=defaultdict(list)
    for e in frame:by_ags[e['ags']].append(e)
    aliases=niedersachsen_aliases(frame)
    aliases['stadt velten - die bürgermeisterin'].add('12065332')
    seen={};duplicates=0;calls=[];outside=[];dispositions=Counter();sources=monthly_sources(False)
    assert len(sources)==15
    for root,pin in sorted(sources,key=lambda x:x[1]['period']):
        with verified_archive(root,pin) as archive:
            buyers=defaultdict(list)
            for row in csv_rows(archive,'organisation.csv'):
                if row['organisationRole']=='buyer':buyers[notice_key(row)].append(row)
            for row in csv_rows(archive,'notice.csv'):
                key=notice_key(row);roles=buyers.get(key,[])
                if not first_metadata_occurrence(seen,key,row,roles):duplicates+=1;continue
                ags,reason=municipal_match(roles,aliases);dispositions[reason]+=1
                if not ags or row['noticeType']!='cn-standard':continue
                day=national_day(row['publicationDate'])
                links=eligible_links(by_ags[ags],day)
                if not links:
                    outside.append({'ags':ags,'national_notice_identifier':key[0],'version':key[1],'publication_day_berlin':day,'reason':'outside_all_prespecified_event_windows'});continue
                for e in links:
                    calls.append({'event_key':event_key(e),'state':e['state'],'cohort':e['state']+' '+e['decisive_date'][:4],'ags':ags,'municipality':e['municipality'],'decisive_date':e['decisive_date'],'margin_stratum':band(e['absolute_margin_pp']),'both_names_available':e['both_names_available'],'municipal_cluster_key':ags,'national_notice_identifier':key[0],'version':key[1],'publication_day_berlin':day,'procedure_identifier_source':row['procedureIdentifier'],'buyer_name_source':roles[0]['organisationName'],'source_export_file':pin['file'],'source_export_sha256':pin['sha256'],'office_exposure_verified':False,'original_call_verified':False,'main_study_eligibility_certified':False})
        print('Screened',pin['period'],flush=True)
    by_event=defaultdict(list)
    for c in calls:by_event[c['event_key']].append(c)
    inventory=[]
    for e in frame:
        cs=by_event[event_key(e)]
        inventory.append({k:e[k] for k in ('state','ags','municipality','decisive_date','absolute_margin_pp','both_names_available')}|{'event_key':event_key(e),'margin_stratum':band(e['absolute_margin_pp']),'municipal_cluster_key':e['ags'],'retained_events_for_municipality':len(by_ags[e['ags']]),'metadata_window_start':discovery_window(e)[0],'metadata_window_end':discovery_window(e)[1],'standard_call_notice_links':len(cs),'call_links_without_guid':sum(not c['procedure_identifier_source'] for c in cs),'observed_distinct_guids':len({c['procedure_identifier_source'] for c in cs if c['procedure_identifier_source']}),'office_exposure_verified':False,'official_election_reverified_in_this_batch':e['state']=='05' and e['decisive_date'][:4]=='2020','main_study_eligibility_certified':False})
    csv_write(DOC/'national-joint-election-inventory.csv',inventory)
    matrix=[]
    for state,year in sorted({(r['state'],r['decisive_date'][:4]) for r in inventory}):
        rs=[r for r in inventory if r['state']==state and r['decisive_date'][:4]==year]
        cs=[r for r in calls if r['state']==state and r['decisive_date'][:4]==year]
        matrix.append({'state':state,'election_year':year,'retained_events':len(rs),'municipal_clusters':len({r['ags'] for r in rs}),'complete_name_events':sum(r['both_names_available'] for r in rs),'events_with_call_metadata':sum(bool(r['standard_call_notice_links']) for r in rs),'events_with_guid_metadata':sum(bool(r['observed_distinct_guids']) for r in rs),'distinct_call_guids':len({r['procedure_identifier_source'] for r in cs if r['procedure_identifier_source']}),'event_links_without_guid':sum(not r['procedure_identifier_source'] for r in cs),'office_exposure_verified':False,'all_active_official_pairs_previously_available':(state,year) in {('05','2020'),('05','2025'),('03','2021'),('12','2024'),('12','2025')},'interpretation':'Complete source-cohort acquisition opportunity; not a gender/outcome selected sample or precision claim'})
    csv_write(DOC/'national-joint-cohort-opportunities.csv',matrix)
    csv_write(DOC/'national-joint-call-discovery.csv',calls)
    if outside:csv_write(DOC/'national-joint-outside-window-calls.csv',outside)
    # Separate Q1 call roster for the officially reverified older NRW cohort.
    selected_ags={e['ags'] for e in nrw};q1=[]
    for c in calls:
        if c['state']=='05' and c['decisive_date'][:4]=='2020' and c['ags'] in selected_ags and '2025-01-01'<=c['publication_day_berlin']<='2025-03-31':q1.append(dict(c,cohort='NRW 2020'))
    csv_write(DOC/'national-joint-nrw-2020-q1-calls.csv',q1)
    csv_write(DOC/'national-joint-nrw-2020-election-inventory.csv',[{k:e[k] for k in ('cohort','ags','municipality','margin_stratum','decisive_date','absolute_margin_pp')} for e in nrw])
    prior=list(csv.DictReader((DOC/'relaxed-acquisition-election-inventory.csv').open()))
    joined=prior+nrw;clusters=Counter(e['ags'] for e in joined)
    summary={'checked_on':'2026-10-11','retained_national_events':len(frame),'national_municipal_clusters':len(by_ags),'missing_name_events_retained':sum(not e['both_names_available'] for e in frame),'metadata_notice_versions_inspected':len(seen),'identical_duplicate_notice_versions_skipped':duplicates,'call_event_links':len(calls),'distinct_call_notice_versions':len({(c['national_notice_identifier'],c['version']) for c in calls}),'events_with_call_metadata':sum(bool(e['standard_call_notice_links']) for e in inventory),'municipalities_with_call_metadata':len({c['ags'] for c in calls}),'distinct_nonmissing_call_guids':len({c['procedure_identifier_source'] for c in calls if c['procedure_identifier_source']}),'nrw_2020_official_pairs_reverified':len(nrw),'nrw_2020_Q1_2025_call_notice_versions':len(q1),'verified_acquisition_election_events':len(joined),'verified_acquisition_distinct_municipalities':len(clusters),'verified_acquisition_repeated_municipalities':sum(n>1 for n in clusters.values()),'additional_procurement_archive_download_bytes':0,'certified_main_study_elections':0,'provisional_mixed_count_inventory_unchanged':5,'warning':'National source frame is not a census or a verified causal sample. Multiple event links are not independent purchases; office exposure and candidate identities outside the verified cohort remain unresolved.','source_dispositions':dict(dispositions)}
    (DOC/'national-joint-discovery-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
