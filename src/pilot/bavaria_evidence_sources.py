"""Pinned municipal sources and narrowly scoped public council-table parsing."""
import hashlib
import re
import subprocess
import unicodedata
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen

ROOT = Path("data/raw/bavaria-supplements")


def normalized(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def verified_source(source, download=False, root=ROOT):
    path = root / (source["id"] + source.get("extension", ".pdf"))
    if not path.exists() and download:
        with urlopen(source["url"], timeout=45) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError("Downloaded municipal source changed; review before updating its pin")
        root.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        path.with_suffix(path.suffix + ".retrieved.txt").write_text(datetime.now(timezone.utc).isoformat())
    if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
        raise ValueError(f"Municipal source checksum changed: {path}")
    return path


def pdf_page(source, page, download=False, root=ROOT):
    path = verified_source(source, download, root)
    result = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True,
                            capture_output=True, text=True)
    return normalized(result.stdout.split("\f")[page - 1])


def html_text(raw):
    text = re.sub(r"<(?:script|style)\b.*?</(?:script|style)>", " ", raw,
                  flags=re.S | re.I)
    return normalized(unescape(re.sub(r"<[^>]+>", " ", text)))


class CouncilRows(HTMLParser):
    """Keep role and end date in the same row, using labelled desktop cells."""
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self.row = {}
        elif tag == "td" and self.row is not None:
            self.cell = [attrs.get("data-label"), []]

    def handle_data(self, data):
        if self.cell is not None:
            self.cell[1].append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None:
            label, pieces = self.cell
            if label and label not in self.row:
                self.row[label] = normalized("".join(pieces))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def council_role(raw, candidate, period, council, role):
    text = html_text(raw)
    selected = re.findall(r'<a\b[^>]*class="[^"]*\bsmcfiltermenuselected\b[^"]*"[^>]*>(.*?)</a>', raw, re.S)
    if candidate not in text or [html_text(s) for s in selected] != [f"Wahlperiode {period}"]:
        raise ValueError("Council identity or selected historical period does not match")
    parser = CouncilRows()
    parser.feed(raw)
    rows = [row for row in parser.rows
            if row.get("Gremium") == council and row.get("Mitarbeit") == role]
    if len(rows) != 1:
        raise ValueError("Expected one municipality-head/deputy role in the selected council")
    return rows[0]
