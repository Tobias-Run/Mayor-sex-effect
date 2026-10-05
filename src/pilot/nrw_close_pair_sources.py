"""Acquire only the public-source pins for the NRW close-pair review.

No alternative route is attempted after an unavailable/protected response.
Changed mutable sources require a new review; they never replace cached pins.
"""
import argparse
import csv
import hashlib
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from nrw_close_pair_screen import MANIFEST, OUT, verified_bytes


def acquire(source, download=False):
    if source['status'] != 'acquired':
        return False  # Preserve failed-attempt provenance; do not retry by default.
    path = Path(source['local_file'])
    if not path.exists():
        if not download:
            raise FileNotFoundError(str(path) + '; rerun with --download if permitted')
        request = Request(source['source_url'], headers={
            'User-Agent': 'MayorProcurementResearch/0.1 (public academic source audit)'})
        with urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise ValueError('Unsuccessful source response; stop and retain the gap')
            raw = response.read(32 * 1024 * 1024 + 1)
        if len(raw) > 32 * 1024 * 1024:
            raise ValueError('Source exceeds the acquisition cap')
        if not raw.startswith(b'%PDF') and any(token in raw[:20000].lower() for token in
                [b'cf-chl-', b'verify you are human', b'javascript is required to view']):
            raise ValueError('Client keyword filter stopped acquisition; this alone does not prove site protection')
        if len(raw) != int(source['bytes']) or hashlib.sha256(raw).hexdigest() != source['sha256']:
            raise ValueError('Mutable source changed; inspect before creating a new version of its pin')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    verified_bytes(source)
    return True


def beckum_ocr(source):
    verified_bytes(source)
    # This is text extraction. The accepted original page was also visually reviewed.
    with tempfile.TemporaryDirectory() as directory:
        prefix = str(Path(directory, 'page'))
        subprocess.run(['pdftoppm', '-f', '22', '-l', '22', '-r', '120', '-singlefile',
                        '-png', source['local_file'], prefix], check=True)
        text = subprocess.check_output(['tesseract', prefix + '.png', 'stdout', '-l', 'eng'], text=True)
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / 'beckum-2020-page-22-ocr.txt'
    if target.exists() and target.read_text() != text:
        raise ValueError('OCR derivative changed; preserve the reviewed version and recheck the page before repinning')
    target.write_text(text)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--all-election-originals', action='store_true',
                        help='Acquire the 382 statewide summary/detail pins without a GERDA dependency')
    parser.add_argument('--ocr-beckum', action='store_true')
    args = parser.parse_args()
    with MANIFEST.open(newline='') as handle:
        sources = list(csv.DictReader(handle))
    checked = sum(acquire(source, args.download) for source in sources)
    if args.all_election_originals:
        with Path('docs/feasibility/nrw-2020-source-manifest.csv').open(newline='') as handle:
            election_pins = list(csv.DictReader(handle))
        for pin in election_pins:
            filename = pin['source_id'] if pin['source_id'].endswith('.txt') else pin['source_id'] + '.txt'
            acquire(dict(pin, status='acquired', local_file=str(Path('data/raw/nrw-2020', filename))), args.download)
        print(f'{len(election_pins)} statewide election summary/detail originals match their pins')
    if args.ocr_beckum:
        beckum_ocr(next(s for s in sources if s['source_id'] == 'beckum-utilities-2020'))
    print(f'{checked} cached originals match their pins; {len(sources)-checked} recorded unavailable attempts retained')


if __name__ == '__main__':
    main()
