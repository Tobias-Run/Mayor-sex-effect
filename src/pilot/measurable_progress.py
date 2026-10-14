"""Replay P1/P2 from pinned local sources; no causal effects or person publication.

Run at repository root. Source retrieval and manual first-coder annotations are
separate private receipts. A reviewed-unresolved gate is never a certified case.
"""
import csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
from html_tables import Tables
from nrw_2025_validation import original_visible_text, csv_write
from creative_cached_2024 import older_exports
from national_scale_expansion import niedersachsen_aliases
from cohort_expansion_national import municipal_match, notice_key, national_day
from federal_procurement import verified_archive, csv_rows
from bandwidth_window_expansion import first_metadata_occurrence

DOC=Path('docs/feasibility')
RAW=Path('data/raw/measurable-progress-2026-10-14')
OUT=Path('outputs/measurable-progress-2026-10-14')

def truth(v):return str(v).lower()=='true'
def rows(name):return list(csv.DictReader((DOC/name).open()))
def indexed(rs,cohort=None):
    result={}
    for r in rs:
        key=(r.get('cohort',cohort),r['ags'])
        if key in result:raise ValueError('Duplicated cohort/municipality key')
        result[key]=r
    return result

def pin_read(pin):
    raw=Path(pin['artifact']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin['sha256']:raise ValueError('Source checksum changed')
    return raw

def official_round(raw,lead):
    text=' '.join(original_visible_text(raw,'original.html').split())
    date='.'.join(reversed(lead['decisive_date'].split('-')))
    if f'Endgültiges Ergebnis - 2. Wahlgang am {date}' not in text or lead['municipality'] not in text:
        raise ValueError('Wrong official event or non-final round')
    parsed=Tables();parsed.feed(raw.decode('utf-8-sig'))
    winners=[t for t in parsed.tables if t and t[0] and t[0][0].startswith(('Gewählter','Gewählte'))]
    totals=[t for t in parsed.tables if any(r and r[0]=='Gültige Stimmen' for r in t)]
    if len(winners)!=1 or not totals:raise ValueError('Ambiguous official result tables')
    table=totals[0]; candidates=[]
    for r in table:
        if len(r)!=3 or not re.search(r'\([^()]*\)$',r[0]):continue
        candidates.append({'name':re.sub(r'\s+\([^()]*\)$','',r[0]),'votes':int(r[1].replace(' ','')),'share':float(r[2].replace(',','.'))})
    total=int(next(r[1] for r in table if r[0]=='Gültige Stimmen').replace(' ',''))
    candidates.sort(key=lambda r:-r['votes'])
    if total!=lead['valid_decisive_votes'] or sum(c['votes'] for c in candidates)!=total:
        raise ValueError('Official valid total mismatch')
    if [c['votes'] for c in candidates]!=[c['votes'] for c in lead['candidates']]:raise ValueError('Official rank/vote vector mismatch')
    if len(candidates)!=lead['final_candidate_count'] or len({c['name'] for c in candidates})!=len(candidates):raise ValueError('Incomplete official identities')
    if winners[0][1][0].split(' (')[0]!=candidates[0]['name']:raise ValueError('Official winner mismatch')
    if any(abs(c['share']-100*c['votes']/total)>.051 for c in candidates):raise ValueError('Official shares disagree')
    return candidates

def legal_rule(raw,dates):
    s=' '.join(original_visible_text(raw,'law.html').split())
    required=['Rechtsbereinigt mit Stand vom 20. Februar 2022','Fassung gültig ab: 20. Februar 2022','§ 44a','Im zweiten Wahlgang ist gewählt, wer die höchste Stimmenzahl auf sich vereint']
    if not all(x in s for x in required):raise ValueError('Historical law not reconciled')
    if not all('2022-02-20'<=d<='2022-07-10' for d in dates):raise ValueError('Outside reviewed event dates')
    return True

def boundary(lead):
    v=[r['votes'] for r in lead['candidates']];total=sum(v)
    return {'top_two_gap_pp':100*(v[0]-v[1])/total,'runner_up_third_gap_pp':100*(v[1]-v[2])/total,
            'third_below_tied_top_if_winner_votes_transferred_to_runner':v[2]<(v[0]+v[1])/2,
            'causal_boundary_stability_certified':False}

def candidate_audit(leads,official,sources):
    annotations=json.loads((RAW/'candidate-dispositions.json').read_text())
    expected={(e['ags'],role) for e in leads for role in ('winner','runner_up')}
    if {(r['ags'],r['role']) for r in annotations}!=expected or len(annotations)!=14:raise ValueError('Every top-two candidate needs one disposition')
    for a in annotations:
        idx=0 if a['role']=='winner' else 1
        if a['official_name']!=official[a['ags']][idx]['name']:raise ValueError('Candidate identity does not match official rank')
        if a['label'] not in ('male','female','unresolved'):raise ValueError('Unsupported label')
        if a['label']!='unresolved':
            if not a['source_key'] or not a['locator'] or not a['identity_and_person_reference_reviewed']:raise ValueError('Unvalidated presentation')
            pin=sources[a['source_key']];raw=pin_read(pin)
            s=' '.join(original_visible_text(raw,Path(pin['artifact']).name).split())
            if a['locator'] not in s:raise ValueError('Accepted locator absent from original')
            if a['context_year']!='2022':raise ValueError('Unrelated historical context')
    (OUT/'candidate-dispositions.json').write_text(json.dumps(annotations,indent=2)+'\n')
    return {(a['ags'],a['role']):a for a in annotations}

def saxony_aliases(leads):
    aliases=niedersachsen_aliases(leads)
    if any(e['ags']=='14612000' for e in leads):aliases['landeshauptstadt dresden'].add('14612000')
    return aliases

def metadata(leads):
    definition=json.loads((RAW/'metadata-before-extraction.json').read_text())
    for p in definition['sources']:pin_read(p)
    addendum=json.loads((RAW/'metadata-exact-alias-addendum.json').read_text())
    source=RAW/'dresden-amtsblatt-july.pdf'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=addendum['source_sha256']:raise ValueError('Alias source changed')
    if 'Landeshauptstadt Dresden' not in ' '.join(original_visible_text(source.read_bytes(),source.name).split()):raise ValueError('Authority alias not in primary source')
    aliases=saxony_aliases(leads)
    # No fuzzy/substring matching, utilities or multi-buyer allocations.
    by_ags={e['ags']:e for e in leads};calls=[];results=[];seen={};pins=[]
    for root,pin in older_exports():
        if pin['format']!='csv' or not pin['period'].startswith('2024-'):continue
        pins.append(pin)
        with verified_archive(root,pin) as z:
            buyers=defaultdict(list)
            for r in csv_rows(z,'organisation.csv'):
                if r['organisationRole']=='buyer':buyers[notice_key(r)].append(r)
            for r in csv_rows(z,'notice.csv'):
                key=notice_key(r);roles=buyers.get(key,[])
                if not first_metadata_occurrence(seen,key,r,roles):continue
                ags,reason=municipal_match(roles,aliases)
                if not ags:continue
                day=national_day(r['publicationDate'])
                if not definition['window_start']<=day<=definition['window_end']:continue
                if r['noticeType'] not in ('cn-standard','can-standard'):continue
                target=calls if r['noticeType']=='cn-standard' else results
                target.append({'ags':ags,'date':day,'notice':key[0],'version':key[1],'guid':r['procedureIdentifier'],'source':pin['file']})
        print('Availability replay',pin['period'],flush=True)
    if len({p['period'] for p in pins})!=12:raise ValueError('Incomplete cached year')
    (OUT/'saxony-call-metadata.json').write_text(json.dumps(calls,indent=2)+'\n')
    (OUT/'saxony-result-metadata.json').write_text(json.dumps(results,indent=2)+'\n')
    (DOC/'saxony-2022-procurement-source-manifest.json').write_text(json.dumps({'window':definition,'cached_csv_archives':pins,'additional_procurement_download_bytes':0,'exact_alias_addendum':addendum,'original_outcomes_verified':False},indent=2)+'\n')
    return {ags:{'calendar_2024_call_notice_versions':sum(c['ags']==ags for c in calls),'calendar_2024_result_notice_versions':sum(c['ags']==ags for c in results),'calendar_2024_call_guids':len({c['guid'] for c in calls if c['ags']==ags and c['guid']}),'calendar_2024_domestic_calls_without_guid':sum(c['ags']==ags and not c['guid'] for c in calls),'cached_months_verified':12,'calendar_followup_mature':True,'reporting_coverage_verified':False,'original_buyer_procedure_outcomes_verified':False} for ags in by_ags}

def pair(labels):
    if 'unresolved' in labels:return 'unresolved'
    return 'mixed_public_presentation' if set(labels)=={'male','female'} else 'same_public_presentation'

def saxony(leads,sources):
    official={}
    for e in leads:
        key='official-dresden' if e['ags']=='14612000' else 'official-'+e['ags']
        official[e['ags']]=official_round(pin_read(sources[key]),e)
    legal_rule(pin_read(sources['law-2022']),[e['decisive_date'] for e in leads])
    annotations=candidate_audit(leads,official,sources);availability=metadata(leads)
    public=[]
    for e in leads:
        a,b=[annotations[(e['ags'],role)] for role in ('winner','runner_up')]
        labels=[a['label'],b['label']];status=pair(labels);mixed=status=='mixed_public_presentation'
        public.append({'cohort':'Saxony 2022 plurality','ags':e['ags'],'municipality':e['municipality'],'decisive_date':e['decisive_date'],'absolute_margin_pp':e['absolute_top_two_gap_pp'],'valid_votes':e['valid_decisive_votes'],'final_candidate_count':e['final_candidate_count'],'official_identities_votes_winner_verified':True,'event_date_plurality_law_verified':True,'pair_status':status,'female_presented_winner':str(labels[0]=='female').lower() if mixed else '', 'signed_presentation_margin_pp':(e['absolute_top_two_gap_pp'] if labels[0]=='female' else -e['absolute_top_two_gap_pp']) if mixed else '', 'winner_presentation_supported':a['label']!='unresolved','loser_presentation_supported':b['label']!='unresolved','winner_source_key':a['source_key'],'loser_source_key':b['source_key'],'winner_reason':a['reason'],'loser_reason':b['reason'],**boundary(e),**availability[e['ags']],'candidate_review_dispositions_completed':2,'independent_second_coding_completed':False,'office_exposure_verified':False,'common_election_relative_window_verified':False,'main_study_eligibility_certified':False,'review_complete_with_disposition':True})
    csv_write(DOC/'saxony-2022-complete-audit.csv',public)
    (OUT/'saxony-official-candidates.json').write_text(json.dumps(official,indent=2)+'\n')
    return public

def scoreboard(sax):
    base=rows('relaxed-acquisition-election-inventory.csv')+rows('national-joint-nrw-2020-election-inventory.csv')
    if len(base)!=169 or len(indexed(base))!=169:raise ValueError('Active acquisition frame changed')
    current=indexed(rows('broader-election-acquisition-frame.csv'))
    labels2020=indexed(rows('creative-2024-assignment-inventory.csv'))
    # Presentation updates are shared across a cohort's windows; outcomes are not.
    assignment2020=indexed(rows('national-joint-nrw-2020-assignment-inventory.csv'))
    recovery=indexed(rows('recovered-original-linked-election-inventory.csv'))
    original2020=indexed(rows('national-joint-nrw-2020-original-linked-election-inventory.csv'))
    closest={r['ags']:r for r in rows('nrw-2025-closest-pair-evidence-review.csv')}
    validated={r['ags']:r for r in json.loads(Path('data/raw/creative-causal-routes-2026-10-12/candidates/validated-reviews.json').read_text())}
    worksheet={r['ags']:r for r in json.loads(Path('data/raw/creative-causal-routes-2026-10-12/candidates/new-reviews.json').read_text())['reviews']}
    nrw_events={e['ags']:e for e in json.loads(Path('outputs/national-joint-expansion-2026-10-11/nrw-2020-selected-elections.json').read_text())}
    score=[]
    for e in base:
        key=(e['cohort'],e['ags']);old=current.get(key,{});lab=labels2020.get(key,{}) if e['cohort']=='NRW 2020' else old
        status=lab.get('first_coder_pair_status',lab.get('pair_status','unresolved'))
        if not status.startswith(('mixed','same','conflicting')):status='unresolved'
        female=lab.get('female_presented_winner','') if status=='mixed_public_presentation' else ''
        if key==('Niedersachsen 2021','03257009'):
            prior=json.loads((DOC/'original-recovery-assignment-checkpoint.json').read_text())
            if not prior['first_coder_mixed_pair_supported']:raise ValueError('Bückeburg evidence changed')
            status='mixed_public_presentation';female='false'
        count=int((assignment2020.get(key,{}) if e['cohort']=='NRW 2020' else recovery.get(key,{})).get('observed_supported_tender_statistics',0))
        proc=int((original2020.get(key,{}) if e['cohort']=='NRW 2020' else recovery.get(key,{})).get('original_window_and_buyer_supported_procedures',0))
        win=lose='unresolved';role_reason='No candidate-role disposition in current aggregate; not inferred from names.'
        if status in ('mixed_public_presentation','same_public_presentation'):win=lose='pass';role_reason='Both candidates supported in existing first-coder pair audit.'
        if e['cohort']=='NRW 2025' and e['ags'] in closest:
            cr=closest[e['ags']];win='pass' if cr['winner_review_disposition']=='accepted_first_coder' else 'unresolved';lose='pass' if cr['loser_review_disposition']=='accepted_first_coder' else 'unresolved';role_reason=cr['unresolved_reason'] or role_reason
        if e['cohort']=='NRW 2020':
            candidates=worksheet[e['ags']]['candidates'];byname={c['name']:c for c in nrw_events[e['ags']]['candidates']}
            if len(candidates)!=2:raise ValueError('Wrong candidate count in source worksheet')
            supported=sum(bool(c['accepted_evidence']) for c in candidates)
            if supported!=validated[e['ags']]['supported_candidates']:raise ValueError('Prior audited candidate support disagrees')
            for c in candidates:
                role='winner' if byname[c['candidate_name_source']]['winner'] else 'loser'
                value='pass' if c['accepted_evidence'] else 'unresolved'
                if role=='winner':win=value
                else:lose=value
            role_reason=validated[e['ags']]['remaining_gap'] or role_reason
        official=e.get('official_source_status','official_NRW_2020_identities_votes_day_winner_verified')
        provisional='provisional' in official
        if e['cohort']=='NRW 2020':start,end='2025-01-01','2025-03-31'
        else:start,end=e['call_window_start'],e['call_window_end']
        score.append({'frame':'existing_active_169','cohort':e['cohort'],'ags':e['ags'],'municipality':e['municipality'],'decisive_date':e['decisive_date'],'absolute_margin_pp':e['absolute_margin_pp'],'source_frame_gate':'pass','official_identity_vote_gate':'pass' if not official.startswith('unresolved') else 'unresolved','official_source_status':official,'official_finality_gate':'unresolved' if provisional else 'pass','event_legal_gate':'unresolved','event_legal_reason':'Earlier cohort source rules retained; case-specific legal/exposure certification not inferred.','winner_presentation_gate':win,'loser_presentation_gate':lose,'presentation_reason':role_reason,'pair_status':status,'female_presented_winner':str(female).lower(),'original_supported_procedures':proc,'original_supported_tender_statistics':count,'provisional_mixed_count_link':status=='mixed_public_presentation' and count>0,'original_buyer_procedure_evidence_gate':'pass' if proc else 'unresolved','observation_window_start':start,'observation_window_end':end,'common_election_relative_window_gate':'unresolved','reporting_coverage_gate':'unresolved','office_exposure_itt_gate':'unresolved','independent_coding_gate':'unresolved','main_study_gate':'unresolved','main_study_eligibility_certified':False,'remaining_reasons':'common_window;reporting_coverage;office_exposure_itt;independent_coding;design_precision','presentation_provenance':'creative-2024-assignment-inventory.csv' if e['cohort']=='NRW 2020' else 'broader-election-acquisition-frame.csv','outcome_provenance':'national-joint-nrw-2020-assignment-inventory.csv' if e['cohort']=='NRW 2020' else 'recovered-original-linked-election-inventory.csv'})
    for e in sax:
        score.append({'frame':'separate_saxony_2022_leads','cohort':e['cohort'],'ags':e['ags'],'municipality':e['municipality'],'decisive_date':e['decisive_date'],'absolute_margin_pp':e['absolute_margin_pp'],'source_frame_gate':'pass','official_identity_vote_gate':'pass','official_source_status':'official_final_state_original_reconciled','official_finality_gate':'pass','event_legal_gate':'pass','event_legal_reason':'KomWG historical version effective 2022-02-20; section 44a second-round plurality.','winner_presentation_gate':'pass' if e['winner_presentation_supported'] else 'unresolved','loser_presentation_gate':'pass' if e['loser_presentation_supported'] else 'unresolved','presentation_reason':e['winner_reason']+'; '+e['loser_reason'],'pair_status':e['pair_status'],'female_presented_winner':e['female_presented_winner'],'original_supported_procedures':0,'original_supported_tender_statistics':0,'provisional_mixed_count_link':False,'original_buyer_procedure_evidence_gate':'unresolved','observation_window_start':'2024-01-01','observation_window_end':'2024-12-31','common_election_relative_window_gate':'unresolved','reporting_coverage_gate':'unresolved','office_exposure_itt_gate':'unresolved','independent_coding_gate':'unresolved','main_study_gate':'unresolved','main_study_eligibility_certified':False,'remaining_reasons':'original_outcomes;common_window;reporting_coverage;office_exposure_itt;independent_coding;plurality_design_precision','presentation_provenance':'saxony-2022-complete-audit.csv','outcome_provenance':'saxony-2022-procurement-source-manifest.json'})
    return score

def summaries(score):
    summaries=[]
    for cohort in sorted({r['cohort'] for r in score}):
        all_cohort=[r for r in score if r['cohort']==cohort]
        for width in (2,5,10):
            es=[r for r in all_cohort if float(r['absolute_margin_pp'])<=width]
            mixed=[r for r in es if r['pair_status']=='mixed_public_presentation'];linked=[r for r in es if r['provisional_mixed_count_link']]
            summaries.append({'cohort':cohort,'cumulative_margin_pp':width,'events':len(es),'distinct_municipalities':len({r['ags'] for r in es}),'both_presentations_supported':sum(r['winner_presentation_gate']==r['loser_presentation_gate']=='pass' for r in es),'mixed_pairs':len(mixed),'female_presented_wins':sum(truth(r['female_presented_winner']) for r in mixed),'female_presented_losses':sum(r['female_presented_winner']=='false' for r in mixed),'unresolved_pairs':sum(r['pair_status']=='unresolved' for r in es),'provisional_mixed_count_links':len(linked),'linked_female_wins':sum(truth(r['female_presented_winner']) for r in linked),'linked_female_losses':sum(r['female_presented_winner']=='false' for r in linked),'independently_coded_pairs':0,'certified_main_study_elections':0})
    csv_write(DOC/'eligibility-scoreboard-cohort-bands.csv',summaries)
    bias=[]
    for cohort in sorted({r['cohort'] for r in score}):
        for matched in (False,True):
            es=[r for r in score if r['cohort']==cohort and (r['original_supported_procedures']>0)==matched]
            bias.append({'cohort':cohort,'has_original_supported_procedure':matched,'events':len(es),'winner_presentation_supported':sum(r['winner_presentation_gate']=='pass' for r in es),'loser_presentation_supported':sum(r['loser_presentation_gate']=='pass' for r in es),'both_presentations_supported':sum(r['winner_presentation_gate']==r['loser_presentation_gate']=='pass' for r in es),'winner_presentation_unresolved':sum(r['winner_presentation_gate']!='pass' for r in es),'loser_presentation_unresolved':sum(r['loser_presentation_gate']!='pass' for r in es),'causal_selection_bias_eliminated':False})
    csv_write(DOC/'eligibility-scoreboard-selection-diagnostics.csv',bias)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for pin in json.loads((RAW/'completed-audit-pins.json').read_text())['inputs']:pin_read(pin)
    pins=json.loads((RAW/'scoreboard-input-pins.json').read_text())
    for p in pins['inputs']:pin_read(p)
    source_rows=json.loads((RAW/'source-retrieval.json').read_text());sources={r['key']:r for r in source_rows}
    if len(source_rows)>30 or max(Counter(r['url'] for r in source_rows).values())>2:raise ValueError('Source budget exceeded')
    for r in source_rows:
        if r.get('artifact'):pin_read(r)
    leads=[e for e in json.loads(Path('outputs/creative-causal-routes-2026-10-12/plurality-leads.json').read_text()) if e['decisive_date'].startswith('2022')]
    expected=json.loads((RAW/'before-search.json').read_text())['event_order']
    if [(e['ags'],e['decisive_date']) for e in leads]!=[(e['ags'],e['date']) for e in expected]:raise ValueError('Selection order changed')
    sax=saxony(leads,sources);score=scoreboard(sax)
    clusters=Counter(r['ags'] for r in score)
    base_rows=rows('relaxed-acquisition-election-inventory.csv')+rows('national-joint-nrw-2020-election-inventory.csv')
    for r in score:
        if r['frame']=='existing_active_169':
            base_row=next(e for e in base_rows if (e['cohort'],e['ags'])==(r['cohort'],r['ags']))
            r['metadata_call_notice_versions']=int(base_row.get('national_standard_call_notices',0)) if r['cohort']!='NRW 2020' else int(next(e for e in rows('national-joint-nrw-2020-original-linked-election-inventory.csv') if e['ags']==r['ags'])['selected_standard_call_notices'])
            r['metadata_availability_provenance']='relaxed-acquisition-election-inventory.csv' if r['cohort']!='NRW 2020' else 'national-joint-nrw-2020-original-linked-election-inventory.csv'
        else:
            se=next(e for e in sax if e['ags']==r['ags']);r['metadata_call_notice_versions']=se['calendar_2024_call_notice_versions'];r['metadata_availability_provenance']='saxony-2022-complete-audit.csv'
        r['current_assignment_gate']='pass' if r['pair_status']=='mixed_public_presentation' else ('fail_first_coder_same_presentation' if r['pair_status']=='same_public_presentation' else 'unresolved')
        if r['current_assignment_gate'].startswith('fail'):r['remaining_reasons']='first_coder_same_presentation_exclusion;'+r['remaining_reasons']
        r['event_key']=r['ags']+':'+r['decisive_date'];r['retained_events_for_municipality']=clusters[r['ags']];r['repeated_municipality']=clusters[r['ags']]>1
    if len({r['event_key'] for r in score})!=176:raise ValueError('Duplicate event or omitted event')
    csv_write(DOC/'eligibility-scoreboard-events.csv',score);summaries(score)
    queue=[]
    for rank,r in enumerate(sorted(score,key=lambda r:(r['cohort'],float(r['absolute_margin_pp']),r['decisive_date'],r['ags'])),1):
        next_gate=next(g for g in ('official_identity_vote_gate','official_finality_gate','event_legal_gate','winner_presentation_gate','loser_presentation_gate','original_buyer_procedure_evidence_gate','common_election_relative_window_gate','reporting_coverage_gate','office_exposure_itt_gate','independent_coding_gate','main_study_gate') if r[g]!='pass')
        queue.append({'rank':rank,'event_key':r['event_key'],'cohort':r['cohort'],'ags':r['ags'],'municipality':r['municipality'],'absolute_margin_pp':r['absolute_margin_pp'],'next_unresolved_gate':next_gate,'outcome_independent_order':True,'next_source_action':'Review dated primary evidence for '+next_gate,'automatic_new_retrieval_authorized':False})
    csv_write(DOC/'eligibility-scoreboard-acquisition-queue.csv',queue)
    # Candidate names/locators stay local; public event ledger retains aggregate statuses.
    public_sources=[]
    for r in source_rows:
        raw=Path(r['artifact']).read_bytes() if r.get('artifact') else b''
        irrelevant=bool(raw and 'Google Gmail Images Sign in' in ' '.join(original_visible_text(raw,Path(r['artifact']).name).split()))
        public_sources.append({k:r.get(k,'') for k in ('key','url','method','public_download_form','status','final_url','sha256','bytes','retrieved_utc','error')}|{'retrieval_disposition':'irrelevant_redirect_content' if irrelevant else ('source_bytes_pinned' if raw else 'failed_or_size_capped'),'HTTP_200_is_not_source_acceptance':True})
    csv_write(DOC/'saxony-2022-source-manifest.csv',public_sources)
    summary={'date':'2026-10-14','existing_active_events':169,'existing_active_municipalities':len({r['ags'] for r in score if r['frame']=='existing_active_169'}),'separate_saxony_events':7,'combined_bookkeeping_events':len(score),'combined_bookkeeping_municipalities':len(clusters),'repeated_municipalities':sum(n>1 for n in clusters.values()),'repeated_event_excess':sum(n-1 for n in clusters.values()),'existing_provisional_mixed_count_links':sum(r['provisional_mixed_count_link'] for r in score),'independent_coding_or_exposure_promoted_by_scoreboard':False,'saxony_official_full_rounds_reconciled':7,'saxony_event_date_legal_rules_verified':7,'saxony_candidate_dispositions_completed':14,'saxony_supported_candidate_presentations':sum(e['winner_presentation_supported']+e['loser_presentation_supported'] for e in sax),'saxony_supported_mixed_pairs':sum(e['pair_status']=='mixed_public_presentation' for e in sax),'saxony_mixed_female_wins':sum(e['pair_status']=='mixed_public_presentation' and truth(e['female_presented_winner']) for e in sax),'saxony_mixed_female_losses':sum(e['pair_status']=='mixed_public_presentation' and e['female_presented_winner']=='false' for e in sax),'saxony_calls_2024':sum(e['calendar_2024_call_notice_versions'] for e in sax),'saxony_municipalities_with_call_metadata':sum(e['calendar_2024_call_notice_versions']>0 for e in sax),'saxony_original_supported_outcomes_added':0,'new_provisional_mixed_count_links':0,'new_source_retrieval_attempts':len(source_rows),'source_retrieval_cap':30,'source_attempts_remaining':30-len(source_rows),'additional_procurement_download_bytes':0,'independent_coding_completed_pairs':0,'certified_main_study_elections':0,'effects_estimated':False,'cohorts_pooled':False,'pages_deployed':False,'completion_definition':'All planned events have explicit source/measurement/legal/boundary/window dispositions; unresolved gates remain unresolved; no eligibility gain inferred.'}
    (DOC/'measurable-progress-p1-p2-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    input_public=[]
    for p in pins['inputs']:
        if not p['artifact'].startswith(('data/','outputs/')):input_public.append(p)
    (DOC/'eligibility-scoreboard-input-manifest.json').write_text(json.dumps({'public_input_pins':input_public,'private_inputs_required_for_full_candidate_replay':True,'raw_sources_uploaded':False},indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
