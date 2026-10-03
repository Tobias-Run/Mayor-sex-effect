"""Audit all district-municipality runoffs in the NRW 2020 summary export.
Run from repo root: python src/pilot/nrw_runoffs.py
Does not infer candidate gender or establish actual terms. Outputs are ignored by Git.
"""
import csv
import io
import json
import hashlib
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

OUT = Path("outputs/nrw-runoff-audit")
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://www.wahlergebnisse.nrw/kommunalwahlen/2020/"

def download(url):
    with urllib.request.urlopen(url, timeout=25) as response:
        return response.read()

raw = download(BASE + "KW20_pers_gemeinden.txt")
(OUT / "summary-source.txt").write_bytes(raw)
rows = list(csv.DictReader(io.StringIO("\n".join(raw.decode("utf-8-sig").splitlines()[3:])), delimiter=";"))
codes = sorted({r["Verwaltungsbezirks-Nr."] for r in rows if r["Datum"] == "27.09.2020"})

def audit(code):
    url = BASE + f"aktuell/txtdateien/b{code}kw2000.txt"
    try:
        raw = download(url)
        (OUT / f"{code}.txt").write_bytes(raw)
        lines = raw.decode("utf-8-sig").splitlines()
        valid = next(csv.reader([next(x for x in lines if x.startswith("Gültige Stimmen;"))], delimiter=";"))
        start = lines.index("davon entfielen auf:") + 1
        candidates = [r for r in csv.reader(lines[start:], delimiter=";") if len(r) >= 4 and r[1].isdigit()]
        runoff = [int(r[3]) for r in candidates if r[3].isdigit()]
        assert len(runoff) == 2, "Expected two runoff candidates"
        assert sum(runoff) == int(valid[3]), "Runoff totals do not reconcile"
        assert sum(int(r[1]) for r in candidates) == int(valid[1]), "First-round totals do not reconcile"
        return {"code": code, "url": url, "valid": True, "sha256": hashlib.sha256(raw).hexdigest(),
                "runoff_valid_votes": int(valid[3]), "first_round_candidates": len(candidates)}
    except Exception as e:
        return {"code": code, "url": url, "valid": False, "error": str(e)}

with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(audit, codes))
(OUT / "audit.json").write_text(json.dumps(results, indent=2))
summary = {"expected_runoffs": len(codes), "validated": sum(r["valid"] for r in results),
           "failures": [r for r in results if not r["valid"]],
           "scope": "District municipalities only; gender and term dates unverified"}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
