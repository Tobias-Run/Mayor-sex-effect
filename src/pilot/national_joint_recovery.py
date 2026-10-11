"""Bounded acquisition of exact missing NRW 2020 cohort originals."""
import hashlib,io,json,zipfile
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import urlopen
from bandwidth_window_expansion import check_pin
from nrw_2025_validation import original_records
from original_recovery import alignment_days
from federal_procurement import export_url,source_date

def recovery_rank(notice,originals):
    types={r['index']['notice-type'] for r in originals if r['index']['procedure-identifier']==notice['procedure-identifier']}
    tier=0 if notice['notice-type']=='cn-standard' and 'can-standard' in types else 1 if notice['notice-type']=='can-standard' and 'cn-standard' in types else 2
    return tier,source_date(notice['publication-date']),notice['publication-number']

def recover(cache,acquire,raw_root,out):
    root=raw_root/'original-recovery';root.mkdir(parents=True,exist_ok=True)
    pinfile=root/'protocol-before-acquisition.json'
    if not pinfile.exists():return cache
    for pin in json.loads(pinfile.read_text())['inputs']:check_pin(pin,pin['artifact'])
    path=root/'retrieval.json';pins=json.loads(path.read_text())['exports'] if path.exists() else []
    if acquire:
        context=json.loads((out/'original-audit/context.json').read_text())
        originals=json.loads((out/'original-audit/originals.json').read_text())
        have={r['index']['publication-number'] for r in originals}
        queue=sorted([n for n in context if n['publication-number'] not in have],key=lambda n:recovery_rank(n,originals))
        attempted={p['period'] for _,p in cache}|{p['period'] for p in pins};stop='fixed_queue_complete'
        for target in queue:
            if target['publication-number'] in have:continue
            for day in alignment_days(target['publication-date']):
                if day in attempted:continue
                used=sum(p['bytes'] for p in pins);allowance=min(32*1024**2,70*1024**2-used,9*1024**3//8-1114683423-used)
                if len(pins)>=18 or allowance<=0:stop='source_count_or_byte_cap';break
                url=export_url(day,'eforms')
                with urlopen(url,timeout=60) as response:
                    raw=response.read(allowance+1)
                    if len(raw)>allowance:stop='next_archive_exceeds_remaining_budget';break
                    if response.status!=200 or response.headers.get('x-amzn-waf-action')=='challenge':raise ValueError('Unsuccessful original response')
                    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                        if archive.testzip() or len(set(archive.namelist()))!=len(archive.namelist()) or sum(i.file_size for i in archive.infolist())>1024**3:raise ValueError('Invalid original archive')
                    pin={'period':day,'file':day+'-eforms.zip','url':url,'final_url':response.url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'retrieved_at_utc':datetime.now(timezone.utc).isoformat()}
                (root/pin['file']).write_bytes(raw);pins.append(pin);attempted.add(day)
                path.write_text(json.dumps({'exports':pins},indent=2)+'\n')
                found,_=original_records(context,[pin],root);have.update(r['index']['publication-number'] for r in found)
                print(day,'exact target matches',len(found),flush=True)
                if target['publication-number'] in have:break
            if stop!='fixed_queue_complete':break
        (root/'acquisition-stop.json').write_text(json.dumps({'stop_reason':stop},indent=2)+'\n')
    used=sum(p['bytes'] for p in pins)
    assert len(pins)<=18 and used<=70*1024**2 and 1114683423+used<=9*1024**3//8
    Path('docs/feasibility/national-joint-original-recovery-export-manifest.json').write_text(json.dumps({'exports':pins,'new_successful_bytes':used,'combined_tracked_procurement_bytes':1114683423+used,'stop':json.loads((root/'acquisition-stop.json').read_text()) if (root/'acquisition-stop.json').exists() else None},indent=2)+'\n')
    return cache+[(root,p) for p in pins]
