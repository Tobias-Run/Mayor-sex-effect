"""Verify a report build and rebuild it using only the public report inputs.

Run after build_feasibility_report.py --pdf. Uses the existing environment;
does not acquire data or install software. Poppler tools verify the PDF text.
Visual review is recorded only when explicitly supplied by the reviewer.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import build_feasibility_report as report

ROOT = report.ROOT
SOURCE_PATHS = [
    'src/report/build_feasibility_report.py',
    'src/report/pdf-tables.lua',
    'src/report/pdf-layout.tex',
    'analysis/requirements-report.txt',
    'manuscript/report-inputs.json',
    'manuscript/feasibility-report.template.md',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args, cwd=ROOT):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout, result.stderr


def run(visual_pages):
    pins = report.verify_inputs()
    checkpoint = json.loads((report.MAN/'report-reproduction-checkpoint.json').read_text())
    report.require(checkpoint['report_date'] == pins['report_date'] and
                   checkpoint['evidence_cutoff'] == pins['evidence_cutoff'], 'Report/evidence dates differ')
    outputs = checkpoint['outputs']
    report.require('manuscript/feasibility-report.pdf' in {r['artifact'] for r in outputs}, 'Build --pdf first')
    for row in outputs:
        path = ROOT/row['artifact']
        report.require(digest(path) == row['sha256'] and path.stat().st_size == row['bytes'],
                       'Build output changed: ' + row['artifact'])
    with tempfile.TemporaryDirectory(prefix='mayor-public-report-') as directory:
        clean = Path(directory)
        paths = SOURCE_PATHS + [r['artifact'] for r in pins['inputs']]
        for name in paths:
            target = clean/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, target)
        report.require(not (clean/'data').exists() and not (clean/'outputs').exists(),
                       'Public rebuild contains private source/output directories')
        command([sys.executable, str(clean/'src/report/build_feasibility_report.py'), '--pdf'], cwd=clean)
        comparisons = [dict(artifact=r['artifact'], byte_identical=digest(clean/r['artifact']) == r['sha256'])
                       for r in outputs]
        report.require(all(r['byte_identical'] for r in comparisons),
                       'Public-only rebuild differs: ' + str([r for r in comparisons if not r['byte_identical']]))
        rebuilt = json.loads((clean/'manuscript/report-reproduction-checkpoint.json').read_text())
        original = dict(checkpoint)
        for value in (rebuilt, original):
            value.pop('checked_at_utc')
        report.require(rebuilt == original, 'Build checkpoint differs beyond its verification timestamp')
    stdout, stderr = command([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'])
    test_text = stdout + stderr
    count = re.search(r'Ran (\d+) tests?', test_text)
    report.require(count is not None and int(count[1]) > 0, 'Missing test result')
    skip = re.search(r'OK \(skipped=(\d+)\)', test_text)
    skipped = int(skip[1]) if skip else 0
    pdf = report.MAN/'feasibility-report.pdf'
    text, _ = command(['pdftotext', '-layout', str(pdf), '-'])
    pages = [p for p in text.split('\f') if p.strip()]
    table_pages = {}
    for number in range(1, 6):
        matching = [i for i, page in enumerate(pages, 1) if f'Table {number}.' in page]
        report.require(len(matching) == 1, 'PDF table caption absent or duplicated')
        table_pages[str(number)] = matching[0]
    report.require('Confirmed NRW' in pages[table_pages['5']-1] and
                   'Conditional NRW + named' in pages[table_pages['5']-1], 'Precision table spans PDF pages')
    report.require(all(0 < number <= len(pages) for number in visual_pages), 'Visual-review page outside PDF')
    bbox, _ = command(['pdftotext', '-bbox', str(pdf), '-'])
    tree = ET.fromstring(bbox)
    outside = []
    for number, page in enumerate((e for e in tree.iter() if e.tag.endswith('}page')), 1):
        width, height = float(page.attrib['width']), float(page.attrib['height'])
        for word in (e for e in page.iter() if e.tag.endswith('}word')):
            if (float(word.attrib['xMin']) < 0 or float(word.attrib['xMax']) > width or
                float(word.attrib['yMin']) < 0 or float(word.attrib['yMax']) > height):
                outside.append(number)
    report.require(not outside, 'PDF text extends beyond page boundaries')
    # Check links in the manuscript and its reproduction guide, including the
    # verification record about to be written. Do not treat planned docs as built.
    verification_path = report.MAN/'report-verification.json'
    checked_links = 0
    for path in (report.MAN/'feasibility-report.md', report.MAN/'README.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if re.match(r'\w+://', target) or target.startswith('#'):
                continue
            linked = (path.parent/target.split('#')[0]).resolve()
            report.require(linked.is_file() or linked == verification_path,
                           'Missing report/reproduction link: ' + target)
            checked_links += 1
    verification = dict(
        report_version=pins['report_version'], verified_at_utc=datetime.now(timezone.utc).isoformat(),
        report_date=pins['report_date'], evidence_cutoff=pins['evidence_cutoff'],
        pinned_public_inputs_verified=len(pins['inputs']),
        public_only_rebuild=dict(private_inputs_copied=False, network_requests=False,
                                 outputs=comparisons, checkpoint_equal_except_timestamp=True),
        offline_tests=dict(run=int(count[1]), skipped=skipped, passed=True,
                           all_optional_numerical_checks_run=skipped == 0),
        pdf=dict(pages=len(pages), table_caption_pages=table_pages,
                 text_within_page_boundaries=True, precision_table_on_one_page=True,
                 visual_reviewed_pages=visual_pages,
                 visual_review_scope='title, tables, figures and clipping' if visual_pages else 'not recorded'),
        relative_report_links_verified=checked_links,
        report_sources=[dict(artifact=name, sha256=digest(ROOT/name))
                        for name in SOURCE_PATHS + ['src/report/verify_feasibility_report.py', 'tests/test_feasibility_report.py']],
        independent_second_coding_completed=False, causal_effects_estimated=False,
        report_status='draft_for_review', github_pages='deferred',
        limitation='Mechanical public-input reproduction is not independent candidate coding or upstream source validation.')
    verification_path.write_text(json.dumps(verification, indent=2) + '\n')
    report.OUT.mkdir(parents=True, exist_ok=True)
    (report.OUT/'offline-tests.txt').write_text(test_text)
    print(json.dumps({k:verification[k] for k in ('pinned_public_inputs_verified', 'offline_tests', 'pdf',
                                                'report_status', 'github_pages')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--visual-reviewed-pages', default='',
                        help='Comma-separated PDF pages actually inspected; omit if no visual review occurred')
    args = parser.parse_args()
    run([int(value) for value in args.visual_reviewed_pages.split(',') if value])
