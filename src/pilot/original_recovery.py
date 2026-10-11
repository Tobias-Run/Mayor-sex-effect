"""Bounded exact-original recovery; reuse the existing auditor unchanged."""
import argparse,csv,hashlib,io,json,shutil,sys,zipfile
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from urllib.request import urlopen
from unittest.mock import patch
import expanded_original_audit as audit
from bandwidth_window_expansion import check_pin
from federal_procurement import export_url,source_date
from nrw_2025_validation import original_records

RAW=Path('data/raw/original-recovery-2026-10-11')
OUT=Path('outputs/original-recovery-2026-10-11')
DOC=Path('docs/feasibility')
PRIOR_BYTES=1027231657


def alignment_days(publication):
    when=date.fromisoformat(source_date(publication))
    return [(when-timedelta(days=i)).isoformat() for i in range(3)]


def recovery_queue(context,originals,procedures,linked):
    have={r['index']['publication-number'] for r in originals}
    zero={(e['cohort'],e['ags']) for e in linked if int(e['observed_supported_tender_statistics'])==0}
    by_guid={p['procedure_identifier']:p for p in procedures}
    def rank(n):
        p=by_guid[n['procedure-identifier']]
        preferred=(p['cohort'],p['ags']) in zero and p['original_issue_publication_inside_window']=='True' and p['sole_original_municipal_root_buyer_supported']=='True'
        cached_result=any(r['index']['procedure-identifier']==p['procedure_identifier'] and r['index']['notice-type']=='can-standard' for r in originals)
        tier=0 if preferred and n['notice-type']=='can-standard' else 1 if cached_result and n['notice-type']=='cn-standard' else 2
        old=p['cohort'] in ('Niedersachsen 2021','Brandenburg 2024')
        return tier,not old,source_date(n['publication-date']),p['ags'],n['publication-number']
    return sorted([n for n in context if n['publication-number'] not in have],key=rank)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');parser.add_argument('--bueckeburg-completion',action='store_true');args=parser.parse_args()
    global RAW,OUT,PRIOR_BYTES
    ceiling=1024**3;new_cap=45*1024**2
    if args.bueckeburg_completion:
        RAW=Path('data/raw/bueckeburg-original-completion-2026-10-11');OUT=Path('outputs/bueckeburg-original-completion-2026-10-11')
        PRIOR_BYTES=1070359794;ceiling=9*1024**3//8;new_cap=64*1024**2
    OUT.mkdir(parents=True,exist_ok=True)
    pins=json.loads((RAW/'protocol-before-acquisition.json').read_text())
    for pin in pins['inputs']:check_pin(pin,pin['artifact'])
    context=json.loads(Path('outputs/expanded-original-audit-2026-10-11/context.json').read_text())
    previous=json.loads(Path('outputs/expanded-original-audit-2026-10-11/originals.json').read_text())
    procedures=list(csv.DictReader((DOC/'expanded-original-procedure-audit.csv').open()))
    linked=list(csv.DictReader((DOC/'expanded-original-linked-election-inventory.csv').open()))
    queue=recovery_queue(context,previous,procedures,linked)
    archive_root=RAW/'xml';archive_root.mkdir(parents=True,exist_ok=True)
    path=archive_root/'retrieval.json'
    extra=json.loads(path.read_text())['exports'] if path.exists() else []
    old_exports=audit.cached_exports()
    if args.bueckeburg_completion:
        phase_root=Path('data/raw/original-recovery-2026-10-11/xml')
        old_exports += [(phase_root,p) for p in json.loads((phase_root/'retrieval.json').read_text())['exports']]
        previous=json.loads(Path('outputs/original-recovery-2026-10-11/audit/originals.json').read_text())
        queue=[n for n in queue if next(p for p in procedures if p['procedure_identifier']==n['procedure-identifier'])['municipality']=='Bückeburg, Stadt']
    cached_days={p['period'] for _,p in old_exports}
    attempted={p['period'] for p in extra}
    have={r['index']['publication-number'] for r in previous}
    if extra:
        found,_=original_records(context,extra,archive_root);have.update(r['index']['publication-number'] for r in found)
    stop='fixed_queue_complete_or_acquisition_not_requested'
    if args.acquire:
        for target in queue:
            if target['publication-number'] in have:continue
            for day in alignment_days(target['publication-date']):
                if day in cached_days or day in attempted:continue
                used=sum(p['bytes'] for p in extra)
                allowance=min(32*1024**2,new_cap-used,ceiling-PRIOR_BYTES-used)
                if len(extra)>=16 or allowance<=0:stop='source_count_or_byte_cap';break
                url=export_url(day,'eforms')
                with urlopen(url,timeout=60) as response:
                    raw=response.read(allowance+1)
                    if len(raw)>allowance:stop='next_archive_exceeds_remaining_budget';break
                    if response.status!=200 or response.headers.get('x-amzn-waf-action')=='challenge':raise ValueError('Protected or failed original export')
                    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                        if len(archive.namelist())!=len(set(archive.namelist())) or sum(i.file_size for i in archive.infolist())>1024**3 or archive.testzip():raise ValueError('Invalid original ZIP')
                    pin={'period':day,'file':day+'-eforms.zip','url':url,'final_url':response.url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'retrieved_at_utc':datetime.now(timezone.utc).isoformat()}
                (archive_root/pin['file']).write_bytes(raw);extra.append(pin);attempted.add(day)
                path.write_text(json.dumps({'exports':extra},indent=2)+'\n')
                found,_=original_records(context,[pin],archive_root)
                have.update(r['index']['publication-number'] for r in found)
                print(day, 'matched',len(found),'new exact targets; remaining',len(context)-len(have),flush=True)
                if target['publication-number'] in have:break
            if stop in ('source_count_or_byte_cap','next_archive_exceeds_remaining_budget'):break
    receipt=RAW/'acquisition-stop.json'
    if args.acquire:
        receipt.write_text(json.dumps({'stop_reason':stop},indent=2)+'\n')
    elif receipt.exists():
        stop=json.loads(receipt.read_text())['stop_reason']
    used=sum(p['bytes'] for p in extra)
    if len(extra)>16 or used>new_cap or PRIOR_BYTES+used>ceiling:raise ValueError('Recovery resource bound exceeded')
    stage=OUT/'staged-docs';stage.mkdir(parents=True,exist_ok=True)
    for name in ('relaxed-acquisition-election-inventory.csv','relaxed-acquisition-national-call-discovery.csv'):shutil.copyfile(DOC/name,stage/name)
    # The prior implementation and query snapshots remain frozen; only the
    # execution destinations and verified export list change in this process.
    with patch.object(audit,'OUT',OUT/'audit'),patch.object(audit,'DOC',stage),patch.object(audit,'cached_exports',return_value=old_exports+[(archive_root,p) for p in extra]),patch.object(sys,'argv',['expanded_original_audit']):audit.main()
    for p in stage.glob('expanded-original-*'):
        (DOC/p.name.replace('expanded-original-','recovered-original-',1)).write_bytes(p.read_bytes())
    summary=json.loads((DOC/'recovered-original-audit-summary.json').read_text())
    summary.update({'new_original_xml_download_bytes':used,'new_daily_exports':len(extra),'combined_tracked_procurement_bytes':PRIOR_BYTES+used,'recovery_stop_reason':stop,'previous_exact_originals':len(previous),'additional_exact_originals':summary['exact_original_xml_notices']-len(previous),'combined_source_ceiling_bytes':ceiling,'execution_tranche':'bueckeburg_completion' if args.bueckeburg_completion else 'initial_recovery'})
    (DOC/'recovered-original-audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    initial=json.loads(Path('data/raw/original-recovery-2026-10-11/xml/retrieval.json').read_text())['exports'] if args.bueckeburg_completion else []
    (DOC/'original-recovery-export-manifest.json').write_text(json.dumps({'initial_tranche_exports':initial,'completion_tranche_exports':extra if args.bueckeburg_completion else [],'exports':extra if not args.bueckeburg_completion else initial+extra,'total_new_bytes':used+sum(p['bytes'] for p in initial)},indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
