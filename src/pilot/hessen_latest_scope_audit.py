"""Audit the latest official Hessen workbook scope; requires openpyxl.

Replay only from the pinned private source bundle; no candidate assignment.
"""
import sys,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime
import openpyxl
sys.path.insert(0,'src/pilot')
from national_scale_expansion import load_frame
from bandwidth_window_expansion import check_pin
root=Path('data/raw/national-joint-expansion-2026-10-11/hessen');sources=json.loads((root/'retrieval.json').read_text())
pin=next(r for r in sources if r.get('file')=='latest-official.xlsx');check_pin(pin,root/pin['file'])
w=openpyxl.load_workbook(root/pin['file'],read_only=True,data_only=True)
rows=list(w['Direktwahlen'].values);records=[]
assert rows[1][0]=='AGS' and rows[3][10]=='Name' and rows[3][12]=='Geschlecht'
assert rows[3][13]=='Träger des Wahlvorschlags' and rows[3][14]=='Anzahl'
for i,r in enumerate(rows,1):
 if not isinstance(r[0],(int,float)) or r[0]<100000 or not isinstance(r[3],datetime):continue
 ags='06'+str(int(r[0])).zfill(6);date=r[3].date().isoformat()
 candidates=[{'party':r[j],'votes':int(r[j+1])} for j in range(13,len(r)-2,3) if isinstance(r[j+1],(int,float))]
 records.append({'ags':ags,'date':date,'row':i,'valid_votes':int(r[9]) if isinstance(r[9],(int,float)) else None,'winner_name':r[10],'winner_gender_field':r[12],'party_vote_records':candidates})
frame=[e for e in load_frame()[0] if e['state']=='06' and e['absolute_margin_pp']<=10]
matched=[]
for e in frame:
 rs=[r for r in records if r['ags']==e['ags'] and r['date']==e['decisive_date']]
 if len(rs)!=1:continue
 r=rs[0];nums=sorted(p['votes'] for p in r['party_vote_records'])
 matched.append({'ags':e['ags'],'decisive_date':e['decisive_date'],'original_source_row':r['row'],'total_and_two_votes_match':r['valid_votes']==e['valid_votes'] and nums==sorted(c['votes'] for c in e['candidates']),'winner_name_present':bool(r['winner_name']),'winner_gender_explicit':r['winner_gender_field'] in ('m','w'),'both_finalist_names_explicit_in_export':False,'both_finalist_gender_fields_explicit_in_export':False})
(root/'municipal-records.json').write_text(json.dumps(records,indent=2)+'\n');(root/'matched-source-scope.json').write_text(json.dumps(matched,indent=2)+'\n')
summary={'national_hessen_events_retained':len(frame),'latest_official_municipal_round_rows':len(records),'event_dates_found_in_current_last_election_export':len(matched),'event_vote_vectors_reconciled':sum(r['total_and_two_votes_match'] for r in matched),'matched_events_with_explicit_winner_gender_field':sum(r['winner_gender_explicit'] for r in matched),'opposing_finalist_names_and_gender_supported_in_export':0,'mixed_elections_certified':0,'source_warning':'Latest reported election only, as of 17 July 2026; agency disclaims currency/completeness. Party-vote blocks omit opponent names and sex/gender fields. Do not copy winner field to losing candidates or treat GERDA raw/predicted labels as original certification.','sources':sources,'inspected_sheet':'Direktwahlen','inspected_field_positions_one_based':{'AGS':1,'election_date':4,'valid_votes':10,'winner_name':11,'winner_nomination':12,'winner_sex_gender':13,'party_vote_triplets_start':14}}
Path('docs/feasibility/hessen-latest-register-scope-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='sources'},indent=2))
