"""Complete multi-candidate final-round opportunity screen; no assignments."""
import csv,json,hashlib
from collections import defaultdict,Counter
from pathlib import Path
from cohort_expansion import SOURCE,SOURCE_SHA
from national_scale_expansion import integer,load_frame
from bandwidth_window_expansion import band,check_pin
from nrw_2025_validation import csv_write
from nrw_2025_validation import original_visible_text

def plurality_lead(group):
    def one(field):
        values={r[field] for r in group}
        if len(values)!=1:raise ValueError('Conflicting '+field)
        return next(iter(values))
    if one('election_type') not in ('Bürgermeisterwahl','Oberbürgermeisterwahl') or any('Landrat' in r['office_type'] for r in group):return None
    if any(r[f]=='TRUE' for r in group for f in ('flag_superseded','flag_shared_ags','flag_decisive_round_missing')):return None
    if one('has_stichwahl')!='TRUE':return None
    day=one('election_date_sw')
    if not '2018-01-01'<=day<='2025-12-31':return None
    finalists=[r for r in group if integer(r['candidate_votes_sw']) is not None]
    n={integer(r['n_candidates_sw']) for r in finalists}
    if n!={len(finalists)} or len(finalists)<3:return None
    votes=[integer(r['candidate_votes_sw']) for r in finalists]
    if any(v<0 for v in votes) or sum(votes)<=0:return None
    ranked=sorted(finalists,key=lambda r:integer(r['candidate_votes_sw']),reverse=True)
    if integer(ranked[0]['candidate_votes_sw'])==integer(ranked[1]['candidate_votes_sw']):return None
    if [integer(r['candidate_rank_sw']) for r in ranked]!=list(range(1,len(finalists)+1)):return None
    if [r for r in group if r['is_winner']=='TRUE']!=[ranked[0]]:return None
    total=sum(votes)
    if any(not r['candidate_voteshare_sw'] or abs(float(r['candidate_voteshare_sw'])-integer(r['candidate_votes_sw'])/total)>.0001 for r in finalists):return None
    gap=(integer(ranked[0]['candidate_votes_sw'])-integer(ranked[1]['candidate_votes_sw']))*100/total
    third=(integer(ranked[1]['candidate_votes_sw'])-integer(ranked[2]['candidate_votes_sw']))*100/total
    return {'state':one('state'),'ags':one('ags'),'municipality':one('ags_name'),'decisive_date':day,'valid_decisive_votes':total,'final_candidate_count':len(finalists),'absolute_top_two_gap_pp':gap,'runner_up_third_gap_pp':third,'both_top_two_names_available':all(r['candidate_name'] for r in ranked[:2]),'candidates':[{'name':r['candidate_name'],'votes':integer(r['candidate_votes_sw']),'winner':r['is_winner']=='TRUE'} for r in ranked]}

def main():
    root=Path('data/raw/creative-causal-routes-2026-10-12');doc=Path('docs/feasibility')
    for p in json.loads((root/'plurality-before-screen.json').read_text())['inputs']:check_pin(p,p['artifact'])
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    groups=defaultdict(list)
    for r in csv.DictReader(SOURCE.open()):groups[(r['state'],r['ags'],r['election_date'],r['election_type'])].append(r)
    leads=[];errors=Counter()
    for group in groups.values():
        try:lead=plurality_lead(group)
        except (ValueError,TypeError,ArithmeticError) as e:errors[str(e)]+=1;continue
        if lead and lead['absolute_top_two_gap_pp']<=10:leads.append(lead)
    leads.sort(key=lambda r:(r['state'],r['decisive_date'],r['ags']))
    original=[r for r in load_frame()[0] if r['absolute_margin_pp']<=10]
    old={(r['ags'],r['decisive_date']) for r in original};new={(r['ags'],r['decisive_date']) for r in leads}
    assert old.isdisjoint(new)
    Path('outputs/creative-causal-routes-2026-10-12/plurality-leads.json').write_text(json.dumps(leads,indent=2)+'\n')
    public=[{k:v for k,v in r.items() if k!='candidates'}|{'margin_stratum':band(r['absolute_top_two_gap_pp']),'event_specific_legal_rule_verified':False,'official_election_reverified':False,'presentation_assignment_verified':False,'main_study_eligibility_certified':False} for r in leads]
    csv_write(doc/'multi-candidate-plurality-opportunities.csv',public)
    summary={'source_opportunity_events':len(leads),'both_top_two_names_available':sum(r['both_top_two_names_available'] for r in leads),'by_state':dict(Counter(r['state'] for r in leads)),'within_2pp':sum(r['absolute_top_two_gap_pp']<=2 for r in leads),'within_5pp':sum(r['absolute_top_two_gap_pp']<=5 for r in leads),'original_two_candidate_screen_events':len(original),'combined_source_opportunity_events':len(old|new),'combined_source_municipal_clusters':len({ags for ags,day in old|new}),'certified_main_study_elections_added':0,'source_reconciliation_errors':dict(errors),'warning':'Separate complete multi-candidate second-round source leads. Event-specific plurality-law applicability, official identities/votes, both candidate presentations, third-candidate boundary stability and precision remain pending. No first-round majority extension or automatic pooling.'}
    law=json.loads((root/'plurality-election-law-retrieval.json').read_text());raw=check_pin(law,root/law['file'])
    quote='Im zweiten Wahlgang ist gewählt, wer die höchste Stimmenzahl auf sich vereint; bei Stimmengleichheit entscheidet das Los.'
    assert quote in ' '.join(original_visible_text(raw,law['file']).split())
    summary.update({'plurality_rule_principle_original_source_verified':True,'legal_source':law['url'],'legal_source_sha256':law['sha256'],'legal_locator':'SächsKomWG §44a, no. 4','legal_quote':quote,'event_specific_historical_legal_applicability_verified':False})
    (doc/'multi-candidate-plurality-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
